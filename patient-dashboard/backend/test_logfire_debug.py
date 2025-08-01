#!/usr/bin/env python3
"""Debug script to test Logfire configuration."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print current environment
print("Environment Variables:")
print(f"LOGFIRE_TOKEN: {os.getenv('LOGFIRE_TOKEN', 'NOT SET')[:20]}...")
print(f"LOGFIRE_WRITE_TOKEN: {os.getenv('LOGFIRE_WRITE_TOKEN', 'NOT SET')[:20]}...")
print(f"LOGFIRE_PROJECT_NAME: {os.getenv('LOGFIRE_PROJECT_NAME', 'NOT SET')}")
print(f"LOGFIRE_PROJECT_URL: {os.getenv('LOGFIRE_PROJECT_URL', 'NOT SET')}")
print()

# Try to configure and send a test log
try:
    import logfire
    
    # Configure with explicit project name
    logfire.configure(
        token=os.getenv('LOGFIRE_WRITE_TOKEN') or os.getenv('LOGFIRE_TOKEN'),
        project_name='pfinni'
    )
    
    print("✅ Logfire configured successfully")
    
    # Send test logs
    logfire.info("Test log from PFINNI backend", test=True, environment="debug")
    
    with logfire.span("test_span", test=True):
        logfire.info("Inside test span")
        logfire.warn("Test warning")
        logfire.error("Test error (not a real error)")
    
    print("✅ Test logs sent")
    print(f"Check logs at: {os.getenv('LOGFIRE_PROJECT_URL', 'https://logfire-us.pydantic.dev/devq-ai/pfinni')}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()