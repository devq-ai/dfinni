"""Check database contents using HTTP API with SQL queries"""
import requests
from requests.auth import HTTPBasicAuth
import json

def execute_and_display(query, description):
    """Execute a SQL query and display results"""
    print(f"\n{'='*60}")
    print(f"Description: {description}")
    print(f"SQL Query: {query}")
    print(f"{'='*60}")
    
    response = requests.post(
        "http://localhost:8000/sql",
        headers={"Content-Type": "text/plain", "Accept": "application/json"},
        auth=HTTPBasicAuth("root", "root"),
        data=f"USE NS patient_dashboard DB patient_dashboard; {query}"
    )
    
    try:
        result = response.json()
        print(f"HTTP Status: {response.status_code}")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Extract actual data from SurrealDB response format
        if isinstance(result, list) and len(result) > 1:
            data = result[-1].get('result', [])
            if data:
                print(f"\nRecord Count: {len(data)}")
                if len(data) <= 5:  # Show all if 5 or fewer records
                    for i, record in enumerate(data):
                        print(f"\nRecord {i+1}:")
                        print(json.dumps(record, indent=2))
            else:
                print("\nNo records found")
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response.text}")

# Execute queries
queries = [
    ("SELECT * FROM user", "Get all users"),
    ("SELECT * FROM patient", "Get all patients"),
    ("SELECT id, email, role FROM user", "Get user summary"),
    ("SELECT count() FROM user GROUP ALL", "Count all users"),
    ("SELECT count() FROM patient GROUP ALL", "Count all patients"),
    ("SELECT * FROM user:admin", "Get admin user by ID"),
    ("SELECT * FROM patient:MRN001", "Get patient by ID"),
]

print("Checking database contents with SQL queries...")
print(f"Target: namespace=patient_dashboard, database=patient_dashboard")

for query, description in queries:
    execute_and_display(query, description)