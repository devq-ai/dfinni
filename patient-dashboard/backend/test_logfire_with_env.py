"""Test logfire with environment variables"""
import os
from dotenv import load_dotenv
import logfire

# Load environment variables
env_path = "/Users/dionedge/devqai/pfinni/.env"
print(f"Loading environment from: {env_path}")
load_dotenv(env_path)

# Show environment variables
print("\n=== Environment Variables ===")
print(f"LOGFIRE_TOKEN: {os.getenv('LOGFIRE_TOKEN', 'NOT SET')[:20]}..." if os.getenv('LOGFIRE_TOKEN') else "LOGFIRE_TOKEN: NOT SET")
print(f"LOGFIRE_PROJECT_NAME: {os.getenv('LOGFIRE_PROJECT_NAME', 'NOT SET')}")
print(f"LOGFIRE_WRITE_TOKEN: {os.getenv('LOGFIRE_WRITE_TOKEN', 'NOT SET')[:20]}..." if os.getenv('LOGFIRE_WRITE_TOKEN') else "LOGFIRE_WRITE_TOKEN: NOT SET")
print(f"LOGFIRE_PROJECT_URL: {os.getenv('LOGFIRE_PROJECT_URL', 'NOT SET')}")

# Test configuration
print("\n=== Testing Logfire Configuration ===")
try:
    # Set the token explicitly if available
    token = os.getenv('LOGFIRE_WRITE_TOKEN') or os.getenv('LOGFIRE_TOKEN')
    if token:
        os.environ['LOGFIRE_TOKEN'] = token
        print(f"Set LOGFIRE_TOKEN from env: {token[:20]}...")
    
    logfire.configure()
    print("✅ Logfire configured successfully!")
    
    # Test a simple log
    with logfire.span("test_span", project_name="pfinni"):
        logfire.info("Test message from pfinni backend")
        print("✅ Test log sent successfully!")
        
except Exception as e:
    print(f"❌ Logfire configuration failed: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()