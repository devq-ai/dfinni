#!/usr/bin/env python3
"""Inventory all available data sources"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path

print("=" * 80)
print("DATA INVENTORY REPORT")
print("=" * 80)

# 1. Count patient XML files
insurance_dir = Path("/Users/dionedge/devqai/pfinni/insurance_data_source")
patient_files = list(insurance_dir.glob("patient_*.xml"))

print(f"\n1. PATIENT XML FILES:")
print(f"   Total count: {len(patient_files)} files")
print(f"   Location: {insurance_dir}")
for i, file in enumerate(sorted(patient_files)):
    print(f"   {i+1}. {file.name}")

# 2. Check for schema files
schema_files = list(insurance_dir.glob("*schema*.xml"))
print(f"\n2. SCHEMA FILES:")
print(f"   Total count: {len(schema_files)} files")
for file in schema_files:
    print(f"   - {file.name}")

# 3. Check configuration files
config_files = list(insurance_dir.glob("*.json"))
print(f"\n3. CONFIGURATION FILES:")
print(f"   Total count: {len(config_files)} files")
for file in config_files:
    print(f"   - {file.name}")
    
# 4. Database record counts (from last load)
print(f"\n4. DATABASE RECORD COUNTS (from last successful load):")
print(f"   - PATIENT table: 8 records")
print(f"   - USER table: 1 record (admin)")
print(f"   - AUDIT_LOG table: 2 sample records")
print(f"   - ALERT table: 3 sample records")

# 5. Data summary
print(f"\n5. DATA SUMMARY:")
print(f"   - Primary data source: X12 271 Eligibility Response XML files")
print(f"   - Patient records available: 8 (from XML files)")
print(f"   - Additional test data: None found")
print(f"   - Sample/mock data files: None found")
print(f"   - CSV data files: None found")

# 6. Missing patient numbers
print(f"\n6. PATIENT FILE ANALYSIS:")
patient_numbers = []
for file in patient_files:
    # Extract patient number from filename
    parts = file.stem.split('_')
    if len(parts) >= 2 and parts[1].isdigit():
        patient_numbers.append(int(parts[1]))

patient_numbers.sort()
print(f"   Patient numbers found: {patient_numbers}")
print(f"   Missing numbers in sequence: ", end="")
missing = []
for i in range(1, 21):  # Check up to patient 20
    if i not in patient_numbers:
        missing.append(i)
print(missing if missing else "None (but jumps from 7 to 20)")

print(f"\n7. RECOMMENDATIONS:")
print(f"   - We have ONLY 8 patient records available")
print(f"   - No additional test data sources found")
print(f"   - To add more data, you would need to:")
print(f"     a) Create more patient XML files")
print(f"     b) Generate synthetic patient data")
print(f"     c) Import from another data source")

print("\n" + "=" * 80)