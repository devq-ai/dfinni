#!/usr/bin/env python3
"""Create XML files for patients 8-19"""

import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Base directory for insurance data
output_dir = Path("/Users/dionedge/devqai/pfinni/insurance_data_source")

# Patient data for patients 8-19
patients = [
    {"num": "008", "first": "Jennifer", "last": "Martinez", "dob": "1982-04-12", "member_id": "UHC823456789", "city": "San Diego", "state": "CA", "zip": "92101", "gender": "F"},
    {"num": "009", "first": "Christopher", "last": "Thompson", "dob": "1975-09-23", "member_id": "AET923456789", "city": "Phoenix", "state": "AZ", "zip": "85001", "gender": "M"},
    {"num": "010", "first": "Patricia", "last": "Wilson", "dob": "1968-11-07", "member_id": "BCBS923456789", "city": "Denver", "state": "CO", "zip": "80201", "gender": "F"},
    {"num": "011", "first": "Daniel", "last": "Moore", "dob": "1990-06-15", "member_id": "CIG923456789", "city": "Seattle", "state": "WA", "zip": "98101", "gender": "M"},
    {"num": "012", "first": "Linda", "last": "Taylor", "dob": "1955-12-28", "member_id": "HUM923456789", "city": "Portland", "state": "OR", "zip": "97201", "gender": "F"},
    {"num": "013", "first": "Matthew", "last": "Anderson", "dob": "1987-03-19", "member_id": "KAI923456789", "city": "Las Vegas", "state": "NV", "zip": "89101", "gender": "M"},
    {"num": "014", "first": "Barbara", "last": "Thomas", "dob": "1960-08-04", "member_id": "ANT923456789", "city": "Salt Lake City", "state": "UT", "zip": "84101", "gender": "F"},
    {"num": "015", "first": "Joseph", "last": "Jackson", "dob": "1992-01-25", "member_id": "UHC103456789", "city": "Albuquerque", "state": "NM", "zip": "87101", "gender": "M"},
    {"num": "016", "first": "Elizabeth", "last": "White", "dob": "1979-07-11", "member_id": "AET103456789", "city": "Tucson", "state": "AZ", "zip": "85701", "gender": "F"},
    {"num": "017", "first": "David", "last": "Harris", "dob": "1984-10-30", "member_id": "BCBS103456789", "city": "Sacramento", "state": "CA", "zip": "95814", "gender": "M"},
    {"num": "018", "first": "Susan", "last": "Martin", "dob": "1973-05-22", "member_id": "CIG103456789", "city": "San Francisco", "state": "CA", "zip": "94102", "gender": "F"},
    {"num": "019", "first": "Charles", "last": "Lee", "dob": "1988-02-14", "member_id": "HUM103456789", "city": "Los Angeles", "state": "CA", "zip": "90001", "gender": "M"},
]

# XML template
xml_template = """<?xml version="1.0" encoding="UTF-8"?>
<!-- Updated: {timestamp} -->
<EligibilityResponse xmlns="http://x12.org/schemas/005010/270271" version="005010" transactionSet="271">
  <TransactionHeader>
    <HierarchicalStructureCode>0022</HierarchicalStructureCode>
    <TransactionSetPurposeCode>11</TransactionSetPurposeCode>
    <ReferenceIdentification>ELG{ref_id}</ReferenceIdentification>
    <Date>{date}</Date>
    <Time>09:15:00</Time>
  </TransactionHeader>
  <InformationSource>
    <EntityIdentifierCode>PR</EntityIdentifierCode>
    <EntityTypeQualifier>2</EntityTypeQualifier>
    <OrganizationName>United Healthcare</OrganizationName>
    <PayerIdentification>87726</PayerIdentification>
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
    <MiddleName></MiddleName>
    <MemberIdentification>{member_id}</MemberIdentification>
    <SocialSecurityNumber>{ssn}</SocialSecurityNumber>
    <DateOfBirth>{dob}</DateOfBirth>
    <Gender>{gender}</Gender>
    <Address>
      <AddressLine>123 Main St</AddressLine>
      <City>{city}</City>
      <State>{state}</State>
      <PostalCode>{zip_code}</PostalCode>
    </Address>
  </Subscriber>
  <EligibilityInfo>
    <EligibilityCode>1</EligibilityCode>
    <PlanType>PPO</PlanType>
    <CoverageLevelCode>EMP</CoverageLevelCode>
    <ServiceTypeCode>30</ServiceTypeCode>
    <PlanCoverageDescription>PPO Standard Plan</PlanCoverageDescription>
    <EffectiveDate>{effective_date}</EffectiveDate>
    <TerminationDate></TerminationDate>
  </EligibilityInfo>
  <BenefitInfo>
    <CoverageLevel>IND</CoverageLevel>
    <ServiceTypeCode>30</ServiceTypeCode>
    <BenefitType>ActiveCoverage</BenefitType>
    <DeductibleAmount>1500.00</DeductibleAmount>
    <CopayAmount>25.00</CopayAmount>
    <CoInsurancePercent>80</CoInsurancePercent>
    <NetworkIndicator>Y</NetworkIndicator>
  </BenefitInfo>
</EligibilityResponse>"""

# Create XML files
created_count = 0
for patient in patients:
    filename = f"patient_{patient['num']}_{patient['last'].lower()}_{patient['first'].lower()}.xml"
    filepath = output_dir / filename
    
    # Generate dates
    now = datetime.now()
    effective_date = (now - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
    
    # Generate SSN (fake pattern)
    ssn = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
    
    # Create XML content
    xml_content = xml_template.format(
        timestamp=now.strftime("%Y-%m-%dT%H:%M:%S-05:00"),
        ref_id=f"{patient['num']}{random.randint(1000, 9999)}",
        date=now.strftime("%Y-%m-%d"),
        first_name=patient['first'],
        last_name=patient['last'],
        member_id=patient['member_id'],
        ssn=ssn,
        dob=patient['dob'],
        gender=patient['gender'],
        city=patient['city'],
        state=patient['state'],
        zip_code=patient['zip'],
        effective_date=effective_date
    )
    
    # Write file
    with open(filepath, 'w') as f:
        f.write(xml_content)
    
    created_count += 1
    print(f"Created: {filename}")

print(f"\nTotal files created: {created_count}")
print(f"Location: {output_dir}")