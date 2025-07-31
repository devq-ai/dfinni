# Updated: 2025-07-27T12:58:15-05:00
"""
Insurance Data Source Integration
Secure X12 271 Eligibility Data Fetcher for Patient Management System

This module demonstrates how to authenticate and pull patient eligibility data
from a secure insurance company data source using OAuth 2.0 and TLS encryption.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

import httpx
from pydantic import BaseModel, Field
from fastapi import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InsuranceConfig(BaseModel):
    """Configuration for insurance data source connection"""
    base_url: str
    auth_url: str
    client_id: str
    client_secret: str
    timeout: int = 30
    retry_attempts: int = 3

class PatientEligibility(BaseModel):
    """Patient eligibility data model"""
    member_id: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    date_of_birth: str
    gender: Optional[str] = None
    status: str
    insurance_company: str
    plan_description: Optional[str] = None
    effective_date: Optional[str] = None
    termination_date: Optional[str] = None
    address: Dict[str, str]
    benefits: Dict[str, float]
    last_updated: datetime = Field(default_factory=datetime.now)

class SecureInsuranceClient:
    """Client for secure insurance data source integration"""

    def __init__(self, config_path: str = "auth_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.access_token = None
        self.token_expires_at = None
        self.session = None

    def _load_config(self) -> InsuranceConfig:
        """Load authentication configuration"""
        try:
            with open(self.config_path) as f:
                config_data = json.load(f)

            return InsuranceConfig(
                base_url=config_data["insurance_data_source"]["base_url"],
                auth_url=config_data["authentication"]["auth_url"],
                client_id=config_data["authentication"]["client_id"],
                client_secret=config_data["authentication"]["client_secret"],
                timeout=config_data["insurance_data_source"]["timeout"],
                retry_attempts=config_data["insurance_data_source"]["retry_attempts"]
            )
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise HTTPException(status_code=500, detail="Configuration error")

    async def authenticate(self) -> str:
        """Authenticate with OAuth 2.0 client credentials flow"""
        if self.access_token and self.token_expires_at > datetime.now():
            return self.access_token

        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "scope": "eligibility:read"
        }

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    self.config.auth_url,
                    data=auth_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()

                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer

                logger.info("Successfully authenticated with insurance data source")
                return self.access_token

        except httpx.HTTPStatusError as e:
            logger.error(f"Authentication failed: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=401, detail="Authentication failed")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=500, detail="Authentication error")

    async def fetch_patient_eligibility(self, member_id: str) -> PatientEligibility:
        """Fetch eligibility data for a specific patient"""
        await self.authenticate()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/xml",
            "Content-Type": "application/json"
        }

        url = f"{self.config.base_url}/eligibility/patient/{member_id}"

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                return self._parse_eligibility_xml(response.text)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Patient {member_id} not found")
            logger.error(f"API request failed: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail="API request failed")
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(status_code=500, detail="Request error")

    async def fetch_daily_batch(self, date: str) -> List[PatientEligibility]:
        """Fetch daily batch of eligibility updates"""
        await self.authenticate()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/xml"
        }

        url = f"{self.config.base_url}/eligibility/batch/{date}"

        try:
            async with httpx.AsyncClient(timeout=60) as client:  # Longer timeout for batch
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                # Parse batch XML response
                root = ET.fromstring(response.text)
                patients = []

                for patient_elem in root.findall(".//EligibilityResponse"):
                    patient_xml = ET.tostring(patient_elem, encoding='unicode')
                    patients.append(self._parse_eligibility_xml(patient_xml))

                logger.info(f"Fetched {len(patients)} patients from daily batch for {date}")
                return patients

        except Exception as e:
            logger.error(f"Batch fetch error: {e}")
            raise HTTPException(status_code=500, detail="Batch fetch error")

    def _parse_eligibility_xml(self, xml_data: str) -> PatientEligibility:
        """Parse X12 271 XML into PatientEligibility model"""
        try:
            root = ET.fromstring(xml_data)
            ns = {"x12": "http://x12.org/schemas/005010/270271"}

            # Extract subscriber information
            subscriber = root.find(".//x12:Subscriber", ns)
            eligibility = root.find(".//x12:EligibilityInfo", ns)
            benefits = root.find(".//x12:BenefitInfo", ns)
            info_source = root.find(".//x12:InformationSource", ns)
            address_elem = subscriber.find("x12:Address", ns)

            # Map status code to patient status
            eligibility_code = eligibility.find("x12:EligibilityStatusCode", ns).text
            effective_date = eligibility.find("x12:EffectiveDate", ns)
            termination_date = eligibility.find("x12:TerminationDate", ns)

            status = self._map_eligibility_status(
                eligibility_code,
                effective_date.text if effective_date is not None else None,
                termination_date.text if termination_date is not None else None
            )

            # Build address dictionary
            address = {
                "street_address": address_elem.find("x12:AddressLine1", ns).text,
                "city": address_elem.find("x12:City", ns).text,
                "state": address_elem.find("x12:State", ns).text,
                "postal_code": address_elem.find("x12:PostalCode", ns).text
            }

            address_line_2 = address_elem.find("x12:AddressLine2", ns)
            if address_line_2 is not None:
                address["address_line_2"] = address_line_2.text

            # Build benefits dictionary
            benefit_data = {}
            if benefits is not None:
                deductible = benefits.find("x12:DeductibleAmount", ns)
                if deductible is not None:
                    benefit_data["deductible"] = float(deductible.text)

                copay = benefits.find("x12:CopayAmount", ns)
                if copay is not None:
                    benefit_data["copay"] = float(copay.text)

                coinsurance = benefits.find("x12:CoInsurancePercent", ns)
                if coinsurance is not None:
                    benefit_data["coinsurance"] = float(coinsurance.text)

            # Extract optional middle name
            middle_name_elem = subscriber.find("x12:MiddleName", ns)
            middle_name = middle_name_elem.text if middle_name_elem is not None else None

            return PatientEligibility(
                member_id=subscriber.find("x12:MemberIdentification", ns).text,
                first_name=subscriber.find("x12:FirstName", ns).text,
                last_name=subscriber.find("x12:LastName", ns).text,
                middle_name=middle_name,
                date_of_birth=subscriber.find("x12:DateOfBirth", ns).text,
                gender=subscriber.find("x12:Gender", ns).text,
                status=status,
                insurance_company=info_source.find("x12:OrganizationName", ns).text,
                plan_description=eligibility.find("x12:PlanCoverageDescription", ns).text,
                effective_date=effective_date.text if effective_date is not None else None,
                termination_date=termination_date.text if termination_date is not None else None,
                address=address,
                benefits=benefit_data
            )

        except Exception as e:
            logger.error(f"XML parsing error: {e}")
            raise HTTPException(status_code=500, detail="XML parsing error")

    def _map_eligibility_status(self, eligibility_code: str, effective_date: Optional[str],
                               termination_date: Optional[str]) -> str:
        """Map X12 eligibility codes to patient management statuses"""
        today = datetime.now().date()

        if eligibility_code == "1":  # Active
            if effective_date:
                eff_date = datetime.strptime(effective_date, "%Y-%m-%d").date()
                if eff_date > today:
                    return "Onboarding"

            if termination_date:
                term_date = datetime.strptime(termination_date, "%Y-%m-%d").date()
                if term_date < today:
                    return "Churned"

            return "Active"
        elif eligibility_code == "6":  # Inactive
            return "Churned"
        elif eligibility_code == "7":  # Pending
            return "Onboarding"
        else:
            return "Inquiry"

    async def register_webhook(self, callback_url: str, events: List[str]) -> bool:
        """Register webhook for real-time updates"""
        await self.authenticate()

        webhook_data = {
            "callback_url": callback_url,
            "events": events,
            "secret_token": "webhook_secret_token"  # Should be from config
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    f"{self.config.base_url}/webhooks/register",
                    json=webhook_data,
                    headers=headers
                )
                response.raise_for_status()

                logger.info(f"Successfully registered webhook: {callback_url}")
                return True

        except Exception as e:
            logger.error(f"Webhook registration failed: {e}")
            return False

# Example usage and testing
async def main():
    """Example usage of the insurance client"""

    # For local development, simulate the secure connection using local files
    client = SecureInsuranceClient("auth_config.json")

    try:
        # Example 1: Fetch specific patient
        print("\\n=== Fetching specific patient ===")
        # In production: patient = await client.fetch_patient_eligibility("UHC123456789")

        # For demo, load local file
        with open("patient_001_anderson_sarah.xml", "r") as f:
            xml_content = f.read()

        patient = client._parse_eligibility_xml(xml_content)
        print(f"Patient: {patient.first_name} {patient.last_name}")
        print(f"Status: {patient.status}")
        print(f"Insurance: {patient.insurance_company}")
        print(f"Address: {patient.address}")

        # Example 2: Process multiple patients (batch simulation)
        print("\\n=== Processing batch of patients ===")

        patient_files = [
            "patient_001_anderson_sarah.xml",
            "patient_002_johnson_michael.xml",
            "patient_003_williams_emily.xml",
            "patient_004_brown_james.xml",
            "patient_005_garcia_maria.xml"
        ]

        patients = []
        for file_name in patient_files:
            try:
                with open(file_name, "r") as f:
                    xml_content = f.read()
                patient = client._parse_eligibility_xml(xml_content)
                patients.append(patient)
            except FileNotFoundError:
                print(f"File not found: {file_name}")
                continue

        print(f"Processed {len(patients)} patients:")
        for p in patients:
            print(f"  - {p.first_name} {p.last_name}: {p.status} ({p.insurance_company})")

        # Example 3: Status analysis
        print("\\n=== Status Analysis ===")
        status_counts = {}
        for p in patients:
            status_counts[p.status] = status_counts.get(p.status, 0) + 1

        for status, count in status_counts.items():
            print(f"  {status}: {count} patients")

    except Exception as e:
        logger.error(f"Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
