# Updated: 2025-07-27T12:58:15-05:00
#!/usr/bin/env python3
"""
Generate sample X12 271 Eligibility Response XML files
Simulating secure insurance company data source
"""

import os
from datetime import datetime, timedelta
import random

# Sample data for realistic patient generation
INSURANCE_COMPANIES = [
    ("United Healthcare", "87726"),
    ("Aetna Insurance", "60054"),
    ("Blue Cross Blue Shield", "55555"),
    ("Cigna Health", "62308"),
    ("Humana Inc", "61519"),
    ("Anthem BCBS", "47518"),
    ("Kaiser Permanente", "52132"),
    ("Molina Healthcare", "37709")
]

FIRST_NAMES = [
    "Emily", "James", "Olivia", "Benjamin", "Sophia", "William", "Ava", "Alexander",
    "Isabella", "Michael", "Charlotte", "Ethan", "Amelia", "Daniel", "Harper",
    "Matthew", "Evelyn", "Henry", "Abigail", "Joseph", "Emma", "David"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson"
]

MIDDLE_NAMES = [
    "Marie", "James", "Ann", "Michael", "Rose", "David", "Grace", "Robert",
    "Elizabeth", "John", "Mae", "Thomas", "Jean", "William", "Hope", "Paul"
]

CITIES = [
    ("Austin", "TX", "78701"), ("Houston", "TX", "77001"), ("Dallas", "TX", "75201"),
    ("San Antonio", "TX", "78201"), ("Fort Worth", "TX", "76101"), ("El Paso", "TX", "79901"),
    ("Arlington", "TX", "76001"), ("Corpus Christi", "TX", "78401"), ("Plano", "TX", "75023"),
    ("Lubbock", "TX", "79401")
]

PLAN_TYPES = [
    "PPO Health Plan", "HMO Select", "EPO Advantage", "POS Choice",
    "High Deductible Health Plan", "Traditional Indemnity"
]

STREET_PREFIXES = [
    "123", "456", "789", "101", "202", "303", "404", "505", "606", "707",
    "808", "909", "111", "222", "333", "444", "555", "666", "777", "888"
]

STREET_NAMES = [
    "Main Street", "Oak Avenue", "Maple Drive", "Pine Lane", "Cedar Court",
    "Elm Way", "Birch Road", "Willow Circle", "Ash Boulevard", "Hickory Trail"
]

def generate_ssn():
    """Generate a fake SSN for testing purposes"""
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

def generate_member_id(company_code):
    """Generate member ID based on insurance company"""
    return f"{company_code}{random.randint(100000000, 999999999)}"

def generate_patient_xml(patient_num):
    """Generate a single patient XML file"""

    # Random selections
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    middle_name = random.choice(MIDDLE_NAMES) if random.random() > 0.3 else None
    insurance_company, payer_id = random.choice(INSURANCE_COMPANIES)
    city, state, zip_code = random.choice(CITIES)
    plan_type = random.choice(PLAN_TYPES)

    # Generate random dates
    birth_year = random.randint(1950, 2005)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    birth_date = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"

    gender = random.choice(["M", "F"])

    # Address
    street_prefix = random.choice(STREET_PREFIXES)
    street_name = random.choice(STREET_NAMES)
    apt_num = f"Apt {random.randint(1, 20)}{random.choice(['A', 'B', 'C'])}" if random.random() > 0.6 else None

    # Benefits
    deductible = random.choice([500, 1000, 1500, 2000, 2500, 3000, 5000])
    coinsurance = random.choice([10, 15, 20, 25, 30])
    copay = random.choice([15, 20, 25, 30, 35, 40, 50])
    benefit_amount = random.choice([2000, 3000, 5000, 7500, 10000, 15000])

    # Status - mostly active, some inactive for testing
    status_code = "1" if random.random() > 0.1 else "6"  # 1=Active, 6=Inactive

    middle_name_xml = f"    <MiddleName>{middle_name}</MiddleName>\n" if middle_name else ""
    apt_xml = f"      <AddressLine2>{apt_num}</AddressLine2>\n" if apt_num else ""

    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<EligibilityResponse xmlns="http://x12.org/schemas/005010/270271" version="005010" transactionSet="271">
  <TransactionHeader>
    <HierarchicalStructureCode>0022</HierarchicalStructureCode>
    <TransactionSetPurposeCode>11</TransactionSetPurposeCode>
    <ReferenceIdentification>ELG{patient_num:09d}</ReferenceIdentification>
    <Date>2025-07-25</Date>
    <Time>{random.randint(8, 17):02d}:{random.randint(0, 59):02d}:00</Time>
  </TransactionHeader>
  <InformationSource>
    <EntityIdentifierCode>PR</EntityIdentifierCode>
    <EntityTypeQualifier>2</EntityTypeQualifier>
    <OrganizationName>{insurance_company}</OrganizationName>
    <PayerIdentification>{payer_id}</PayerIdentification>
  </InformationSource>
  <InformationReceiver>
    <EntityIdentifierCode>1P</EntityIdentifierCode>
    <EntityTypeQualifier>2</EntityTypeQualifier>
    <OrganizationName>Memorial Healthcare Center</OrganizationName>
    <ProviderIdentification>1234567890</ProviderIdentification>
  </InformationReceiver>
  <Subscriber>
    <EntityIdentifierCode>IL</EntityIdentifierCode>
    <EntityTypeQualifier>1</EntityTypeQualifier>
    <LastName>{last_name}</LastName>
    <FirstName>{first_name}</FirstName>
{middle_name_xml}    <MemberIdentification>{generate_member_id(payer_id[:3])}</MemberIdentification>
    <SocialSecurityNumber>{generate_ssn()}</SocialSecurityNumber>
    <DateOfBirth>{birth_date}</DateOfBirth>
    <Gender>{gender}</Gender>
    <GroupNumber>GRP{random.randint(1, 999):03d}</GroupNumber>
    <Address>
      <AddressLine1>{street_prefix} {street_name}</AddressLine1>
{apt_xml}      <City>{city}</City>
      <State>{state}</State>
      <PostalCode>{zip_code}</PostalCode>
    </Address>
  </Subscriber>
  <EligibilityInfo>
    <EligibilityStatusCode>{status_code}</EligibilityStatusCode>
    <CoverageLevel>IND</CoverageLevel>
    <ServiceType>30</ServiceType>
    <PlanCoverageDescription>{plan_type}</PlanCoverageDescription>
    <EffectiveDate>2025-01-01</EffectiveDate>
    <TerminationDate>2025-12-31</TerminationDate>
  </EligibilityInfo>
  <BenefitInfo>
    <BenefitCode>1</BenefitCode>
    <CoverageLevel>IND</CoverageLevel>
    <ServiceType>30</ServiceType>
    <BenefitAmount>{benefit_amount}.00</BenefitAmount>
    <DeductibleAmount>{deductible}.00</DeductibleAmount>
    <CoInsurancePercent>{coinsurance}</CoInsurancePercent>
    <CopayAmount>{copay}.00</CopayAmount>
    <NetworkIndicator>Y</NetworkIndicator>
  </BenefitInfo>
</EligibilityResponse>'''

    return xml_content, f"patient_{patient_num:03d}_{last_name.lower()}_{first_name.lower()}.xml"

def main():
    """Generate all patient files"""
    output_dir = "/Users/dionedge/devqai/insurance_data_source"

    # Generate patients 3-20 (we already have 1-2)
    for i in range(3, 21):
        xml_content, filename = generate_patient_xml(i)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        print(f"Generated: {filename}")

    print(f"\nGenerated 18 additional patient files in {output_dir}")
    print("Total: 20 patient eligibility files")

if __name__ == "__main__":
    main()
