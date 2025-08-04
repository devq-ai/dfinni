#\!/usr/bin/env python3
"""Test Logfire configuration directly"""
import os
import sys

# Set environment variables from .env file
import os
from dotenv import load_dotenv

# Load from the main .env file
load_dotenv('/Users/dionedge/devqai/.env')

# Get token from environment
token = os.getenv('PFINNI_LOGFIRE_TOKEN')
if not token:
    print("ERROR: PFINNI_LOGFIRE_TOKEN not found in environment")
    print("Please set PFINNI_LOGFIRE_TOKEN in your .env file")
    exit(1)

os.environ['LOGFIRE_TOKEN'] = token
os.environ['LOGFIRE_PROJECT_NAME'] = os.getenv('PFINNI_LOGFIRE_PROJECT_NAME', 'pfinni')

# Configure logfire
import logfire

print("Configuring Logfire...")
logfire.configure(
    service_name='pfinni-test',
    send_to_logfire=True
)

print("Sending test logs...")
logfire.info("TEST_LOG", message="This is a test log from test_logfire.py")
logfire.error("TEST_ERROR", message="This is a test error")

with logfire.span("test_span"):
    logfire.info("Inside span", test=True)

print("Test completed\!")
print("Check logs at: https://logfire-us.pydantic.dev/devq-ai/pfinni")
EOF < /dev/null