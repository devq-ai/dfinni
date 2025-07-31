<!-- Updated: 2025-07-27T12:58:15-05:00 -->
# Insurance Data Source Configuration
# Secure X12 270/271 Eligibility Data Integration

## Overview
This directory simulates a secure insurance company data source containing X12 270/271 eligibility verification responses in XML format. In a production environment, this would be accessed via:

- **SFTP/FTP with SSL/TLS encryption**
- **RESTful API with OAuth 2.0 authentication**
- **VPN-secured direct database connections**
- **EDI clearinghouse integration**

## Data Source Details

### Connection Parameters
```
Environment: Production Insurance Data Hub
Protocol: HTTPS/SFTP
Authentication: OAuth 2.0 + Client Certificate
Base URL: https://secure-eligibility.insurance-hub.com/api/v1/
Data Format: X12 271 XML (converted from EDI)
Encryption: AES-256 at rest, TLS 1.3 in transit
```

### Authentication Requirements
```bash
# OAuth 2.0 Token Endpoint
POST https://auth.insurance-hub.com/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id=MEMORIAL_HC_CLIENT_ID&
client_secret=MEMORIAL_HC_SECRET&
scope=eligibility:read
```

### API Endpoints
```
GET /eligibility/patients           # List all patients
GET /eligibility/patient/{id}       # Get specific patient
GET /eligibility/batch/{date}       # Get daily batch
POST /eligibility/inquiry           # Submit 270 request
```

## File Structure
- `eligibility_schema.xml` - X12 271 XML Schema Definition
- `patient_*.xml` - Individual patient eligibility responses
- `auth_config.json` - Authentication configuration template
- `data_mapping.json` - Field mapping rules

## Data Fields Mapped to Patient Management System

### Core Patient Data
- **Name**: LastName, FirstName, MiddleName
- **Date of Birth**: DateOfBirth (YYYY-MM-DD format)
- **Address**: AddressLine1, AddressLine2, City, State, PostalCode
- **Status**: Derived from EligibilityStatusCode
  - `1` = Active
  - `6` = Inactive/Churned
  - `7` = Pending (maps to Onboarding)
  - `8` = Inquiry

### Insurance-Specific Fields
- **Member ID**: MemberIdentification
- **Insurance Company**: InformationSource/OrganizationName
- **Plan Type**: PlanCoverageDescription
- **Group Number**: GroupNumber
- **Effective Dates**: EffectiveDate, TerminationDate

### Status Mapping Logic
```python
def map_eligibility_status(eligibility_code, effective_date, termination_date):
    """Map X12 eligibility codes to patient management statuses"""
    today = datetime.now().date()
    
    if eligibility_code == "1":  # Active
        if effective_date > today:
            return "Onboarding"
        elif termination_date and termination_date < today:
            return "Churned"
        else:
            return "Active"
    elif eligibility_code == "6":  # Inactive
        return "Churned"
    elif eligibility_code == "7":  # Pending
        return "Onboarding"
    else:
        return "Inquiry"
```

## Data Quality & Validation Rules

### Schema Evolution Handling
When insurance companies update their data schemas:

1. **New Fields**: Auto-detected and flagged for manual mapping
2. **Modified Fields**: Generate change alerts with data preservation
3. **Removed Fields**: Maintain historical data, mark as deprecated
4. **Field Type Changes**: Validate and convert with error logging

### Validation Rules
```python
VALIDATION_RULES = {
    "date_of_birth": {
        "required": True,
        "format": "YYYY-MM-DD",
        "range": ["1900-01-01", "today"]
    },
    "member_identification": {
        "required": True,
        "pattern": r"^[A-Z]{3}\d{9}$",
        "unique": True
    },
    "eligibility_status_code": {
        "required": True,
        "allowed_values": ["1", "6", "7", "8"]
    },
    "postal_code": {
        "required": True,
        "pattern": r"^\d{5}(-\d{4})?$"
    }
}
```

## Real-Time vs Batch Processing

### Real-Time (Priority)
- **URGENT Status Changes**: Immediate processing via webhook
- **New Patient Enrollments**: Real-time API calls
- **Coverage Terminations**: Immediate updates

### Batch Processing (Standard)
- **Daily Eligibility Updates**: 2:00 AM CST
- **Monthly Coverage Reviews**: 1st of each month
- **Birthday Alerts**: Daily scan at 6:00 AM CST

## Security & Compliance

### HIPAA Compliance
- All data encrypted in transit (TLS 1.3) and at rest (AES-256)
- Access logging with audit trails
- Role-based access controls
- PHI de-identification for development environments

### Data Retention
- **Active Records**: Indefinite (per state requirements)
- **Audit Logs**: 6 years minimum (HIPAA requirement)
- **System Logs**: 90 days rolling
- **Backup Data**: 7 years encrypted storage

## Monitoring & Alerting

### Health Checks
```bash
# API Health Check
curl -H "Authorization: Bearer $TOKEN" \
  https://secure-eligibility.insurance-hub.com/health

# Expected Response
{
  "status": "healthy",
  "timestamp": "2025-07-25T10:30:00Z",
  "version": "v1.2.3",
  "checks": {
    "database": "healthy",
    "cache": "healthy",
    "external_apis": "healthy"
  }
}
```

### Alert Conditions
1. **Connection Failures**: > 3 consecutive failures
2. **Data Quality Issues**: Invalid records > 5%
3. **Schema Changes**: New fields detected
4. **Volume Anomalies**: Daily volume ±50% from baseline
5. **Authentication Failures**: > 10 failed attempts/hour

## Sample Integration Code

### FastAPI Data Fetcher
```python
import httpx
from datetime import datetime
import xml.etree.ElementTree as ET

class InsuranceDataFetcher:
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        
    async def authenticate(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "eligibility:read"
                }
            )
            self.token = response.json()["access_token"]
    
    async def fetch_patient_eligibility(self, member_id: str):
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/eligibility/patient/{member_id}",
                headers=headers
            )
            return self.parse_eligibility_xml(response.text)
    
    def parse_eligibility_xml(self, xml_data: str) -> dict:
        root = ET.fromstring(xml_data)
        ns = {"x12": "http://x12.org/schemas/005010/270271"}
        
        subscriber = root.find(".//x12:Subscriber", ns)
        eligibility = root.find(".//x12:EligibilityInfo", ns)
        
        return {
            "first_name": subscriber.find("x12:FirstName", ns).text,
            "last_name": subscriber.find("x12:LastName", ns).text,
            "middle_name": getattr(subscriber.find("x12:MiddleName", ns), 'text', None),
            "date_of_birth": subscriber.find("x12:DateOfBirth", ns).text,
            "status": self.map_status(eligibility.find("x12:EligibilityStatusCode", ns).text),
            "member_id": subscriber.find("x12:MemberIdentification", ns).text,
            "address": self.parse_address(subscriber.find("x12:Address", ns), ns)
        }
```

## Error Handling & Recovery

### Common Issues & Solutions
1. **Token Expiration**: Auto-refresh with exponential backoff
2. **Rate Limiting**: Implement queue with retry logic
3. **Network Timeouts**: Circuit breaker pattern
4. **Invalid XML**: Schema validation with detailed error reporting
5. **Missing Fields**: Default values with logging

### Failover Strategy
- **Primary**: Real-time API calls
- **Secondary**: Cached data (max 24 hours old)
- **Tertiary**: Manual file processing
- **Emergency**: Read-only mode with alerts

## Testing & Development

### Mock Data Setup
The current directory contains 20 sample patient files for development and testing:
- Mix of active/inactive statuses
- Various insurance companies
- Different plan types and coverage levels
- Realistic Texas addresses and demographics

### Test Scenarios
1. **New Patient Processing**: Unknown member IDs
2. **Status Changes**: Active → Churned transitions
3. **Schema Evolution**: New fields, modified structures
4. **Data Quality**: Invalid dates, missing required fields
5. **Volume Testing**: Batch processing 1000+ records

This configuration provides a comprehensive foundation for integrating X12 271 eligibility data into your patient management system while maintaining security, compliance, and data quality standards.
