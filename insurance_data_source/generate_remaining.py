# Updated: 2025-07-27T12:58:15-05:00
import os

# Remaining patient data (patients 6-20)
patients = [
    ("Davis", "Robert", None, "Kaiser Permanente", "52132", "KAI521345678", "678-90-1234", "1971-09-14", "M", "GRP006", "303 Birch Road", None, "Fort Worth", "TX", "76101", "1", "Traditional Indemnity", "3000.00", "1500.00", "20", "25.00"),
    ("Miller", "Jessica", "Ann", "Anthem BCBS", "47518", "ANT475987654", "789-01-2345", "1995-02-03", "F", "GRP007", "404 Willow Circle", "Apt 12", "El Paso", "TX", "79901", "1", "PPO Health Plan", "5000.00", "2000.00", "25", "30.00"),
    ("Wilson", "Christopher", "Paul", "Molina Healthcare", "37709", "MOL377456789", "890-12-3456", "1983-08-25", "M", "GRP008", "505 Ash Boulevard", None, "Arlington", "TX", "76001", "1", "HMO Select", "2000.00", "3000.00", "15", "20.00"),
    ("Moore", "Amanda", "Rose", "United Healthcare", "87726", "UHC877234567", "901-23-4567", "1990-01-12", "F", "GRP009", "606 Hickory Trail", None, "Corpus Christi", "TX", "78401", "1", "EPO Advantage", "7500.00", "1000.00", "20", "25.00"),
    ("Taylor", "Daniel", "Michael", "Aetna Insurance", "60054", "AET600789123", "012-34-5678", "1976-06-19", "M", "GRP010", "707 Main Street", "Suite 3", "Plano", "TX", "75023", "6", "High Deductible Health Plan", "0.00", "5000.00", "30", "0.00"),
    ("Anderson", "Lisa", "Marie", "Blue Cross Blue Shield", "55555", "BCBS555123456", "123-45-6789", "1987-11-08", "F", "GRP011", "808 Oak Avenue", None, "Lubbock", "TX", "79401", "1", "POS Choice", "10000.00", "1500.00", "15", "35.00"),
    ("Thomas", "Kevin", "James", "Cigna Health", "62308", "CIG623789456", "234-56-7890", "1969-04-27", "M", "GRP012", "909 Pine Lane", "Unit 2B", "Austin", "TX", "78702", "1", "PPO Health Plan", "5000.00", "2000.00", "20", "30.00"),
    ("Jackson", "Nicole", "Grace", "Humana Inc", "61519", "HUM615567890", "345-67-8901", "1993-10-15", "F", "GRP013", "111 Cedar Court", None, "Houston", "TX", "77002", "1", "HMO Select", "3000.00", "2500.00", "15", "25.00"),
    ("White", "Brandon", "David", "Kaiser Permanente", "52132", "KAI521678901", "456-78-9012", "1982-12-02", "M", "GRP014", "222 Elm Way", None, "Dallas", "TX", "75202", "1", "Traditional Indemnity", "2000.00", "3000.00", "25", "20.00"),
    ("Harris", "Stephanie", "Hope", "Anthem BCBS", "47518", "ANT475234567", "567-89-0123", "1991-07-31", "F", "GRP015", "333 Birch Road", "Apt 4C", "San Antonio", "TX", "78202", "1", "EPO Advantage", "7500.00", "1000.00", "20", "25.00"),
    ("Martin", "Andrew", "Thomas", "Molina Healthcare", "37709", "MOL377890123", "678-90-1234", "1974-03-18", "M", "GRP016", "444 Willow Circle", None, "Fort Worth", "TX", "76102", "6", "High Deductible Health Plan", "0.00", "5000.00", "30", "0.00"),
    ("Thompson", "Rachel", "Elizabeth", "United Healthcare", "87726", "UHC877345678", "789-01-2345", "1989-09-06", "F", "GRP017", "555 Ash Boulevard", None, "El Paso", "TX", "79902", "1", "POS Choice", "10000.00", "1500.00", "15", "35.00"),
    ("Garcia", "Carlos", "Antonio", "Aetna Insurance", "60054", "AET600456789", "890-12-3456", "1986-01-23", "M", "GRP018", "666 Hickory Trail", "Suite 1A", "Arlington", "TX", "76002", "1", "PPO Health Plan", "5000.00", "2000.00", "20", "30.00"),
    ("Martinez", "Jennifer", "Lynn", "Blue Cross Blue Shield", "55555", "BCBS555678901", "901-23-4567", "1977-08-14", "F", "GRP019", "777 Main Street", None, "Corpus Christi", "TX", "78402", "1", "HMO Select", "3000.00", "2500.00", "15", "25.00"),
    ("Robinson", "Joshua", "William", "Cigna Health", "62308", "CIG623012345", "012-34-5678", "1994-05-29", "M", "GRP020", "888 Oak Avenue", "Apt 6B", "Plano", "TX", "75024", "1", "Traditional Indemnity", "2000.00", "3000.00", "25", "20.00")
]

base_dir = "/Users/dionedge/devqai/insurance_data_source"

for i, patient_data in enumerate(patients, 6):
    (last_name, first_name, middle_name, insurance_company, payer_id, member_id, ssn, dob,
     gender, group_num, addr1, addr2, city, state, zip_code, status_code, plan_type,
     benefit_amount, deductible, coinsurance, copay) = patient_data

    middle_name_xml = f"    <MiddleName>{middle_name}</MiddleName>\n" if middle_name else ""
    addr2_xml = f"      <AddressLine2>{addr2}</AddressLine2>\n" if addr2 else ""

    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<EligibilityResponse xmlns="http://x12.org/schemas/005010/270271" version="005010" transactionSet="271">
  <TransactionHeader>
    <HierarchicalStructureCode>0022</HierarchicalStructureCode>
    <TransactionSetPurposeCode>11</TransactionSetPurposeCode>
    <ReferenceIdentification>ELG{i:09d}</ReferenceIdentification>
    <Date>2025-07-25</Date>
    <Time>{10 + (i-6)}:{15 + (i-6)*2:02d}:00</Time>
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
{middle_name_xml}    <MemberIdentification>{member_id}</MemberIdentification>
    <SocialSecurityNumber>{ssn}</SocialSecurityNumber>
    <DateOfBirth>{dob}</DateOfBirth>
    <Gender>{gender}</Gender>
    <GroupNumber>{group_num}</GroupNumber>
    <Address>
      <AddressLine1>{addr1}</AddressLine1>
{addr2_xml}      <City>{city}</City>
      <State>{state}</State>
      <PostalCode>{zip_code}</PostalCode>
    </Address>
  </Subscriber>
  <EligibilityInfo>
    <EligibilityStatusCode>{status_code}</EligibilityStatusCode>
    <CoverageLevel>{"FAM" if i % 4 == 0 else "IND"}</CoverageLevel>
    <ServiceType>30</ServiceType>
    <PlanCoverageDescription>{plan_type}</PlanCoverageDescription>
    <EffectiveDate>{"2024-01-01" if status_code == "6" else "2025-01-01"}</EffectiveDate>
    <TerminationDate>{"2024-12-31" if status_code == "6" else "2025-12-31"}</TerminationDate>
  </EligibilityInfo>
  <BenefitInfo>
    <BenefitCode>{status_code}</BenefitCode>
    <CoverageLevel>{"FAM" if i % 4 == 0 else "IND"}</CoverageLevel>
    <ServiceType>30</ServiceType>
    <BenefitAmount>{benefit_amount}</BenefitAmount>
    <DeductibleAmount>{deductible}</DeductibleAmount>
    <CoInsurancePercent>{coinsurance}</CoInsurancePercent>
    <CopayAmount>{copay}</CopayAmount>
    <NetworkIndicator>{"N" if status_code == "6" else "Y"}</NetworkIndicator>
  </BenefitInfo>
</EligibilityResponse>'''

    filename = f"patient_{i:03d}_{last_name.lower()}_{first_name.lower()}.xml"
    filepath = os.path.join(base_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"Generated: {filename}")

print("\\nCompleted generating patients 6-20")
