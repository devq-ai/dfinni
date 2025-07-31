"""Test logfire configuration"""
import os
import logfire

# Show environment variables
print("=== Environment Variables ===")
print(f"LOGFIRE_TOKEN: {os.getenv('LOGFIRE_TOKEN', 'NOT SET')[:20]}..." if os.getenv('LOGFIRE_TOKEN') else "LOGFIRE_TOKEN: NOT SET")
print(f"LOGFIRE_PROJECT_NAME: {os.getenv('LOGFIRE_PROJECT_NAME', 'NOT SET')}")
print(f"LOGFIRE_WRITE_TOKEN: {os.getenv('LOGFIRE_WRITE_TOKEN', 'NOT SET')[:20]}..." if os.getenv('LOGFIRE_WRITE_TOKEN') else "LOGFIRE_WRITE_TOKEN: NOT SET")

# Test configuration
print("\n=== Testing Logfire Configuration ===")
try:
    logfire.configure()
    print("✅ Logfire configured successfully!")
    
    # Test a simple log
    with logfire.span("test_span"):
        logfire.info("Test message from pfinni backend")
        print("✅ Test log sent successfully!")
        
except Exception as e:
    print(f"❌ Logfire configuration failed: {e}")
    print(f"Error type: {type(e).__name__}")
    
# Check if we need to set project name
print("\n=== Checking Project Configuration ===")
try:
    # Try with explicit project name from env
    project_name = os.getenv('LOGFIRE_PROJECT_NAME', 'pfinni')
    print(f"Using project name: {project_name}")
    
    logfire.configure(project_name=project_name)
    print("✅ Logfire configured with explicit project name!")
    
    with logfire.span("test_with_project"):
        logfire.info("Test with explicit project name")
        
except Exception as e:
    print(f"❌ Failed with explicit project: {e}")