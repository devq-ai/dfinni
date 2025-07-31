"""Test CORS parsing"""
import os
from pydantic import BaseModel, field_validator, Field
from pydantic_settings import BaseSettings
from typing import List

class TestSettings(BaseSettings):
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        env="CORS_ORIGINS",
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        print(f"Validator received: {repr(v)}, type: {type(v)}")
        if isinstance(v, str):
            # Handle escaped asterisk
            if v == "\\*":
                return ["*"]
            result = [origin.strip() for origin in v.split(",")]
            print(f"Parsed result: {result}")
            return result
        return v

# Test it
os.environ['CORS_ORIGINS'] = 'http://localhost:3000,https://patient-dashboard.memorial-hc.com'

try:
    settings = TestSettings()
    print(f"Success! CORS_ORIGINS: {settings.CORS_ORIGINS}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()