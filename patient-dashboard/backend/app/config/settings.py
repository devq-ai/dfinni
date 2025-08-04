# Updated: 2025-07-27T12:58:15-05:00
"""
Application Configuration Settings
Centralized configuration management with environment-based overrides
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file="/Users/dionedge/devqai/.env",  # Single .env file location per Production Proposal
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Application Settings
    APP_NAME: str = "Patient Management Dashboard"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    RELOAD: bool = Field(default=False, env="RELOAD")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Server Settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")

    # Security Settings
    SECRET_KEY: str = Field(env="PFINNI_SECRET_KEY")
    JWT_SECRET_KEY: str = Field(env="PFINNI_JWT_SECRET_KEY")
    ENCRYPTION_KEY: str = Field(env="PFINNI_ENCRYPTION_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Database Settings
    DATABASE_URL: str = Field(env="PFINNI_SURREALDB_URL")
    DATABASE_USER: str = Field(env="PFINNI_SURREALDB_USERNAME")
    DATABASE_PASS: str = Field(env="PFINNI_SURREALDB_PASSWORD")
    DATABASE_NAME: str = Field(env="PFINNI_SURREALDB_DATABASE")
    DATABASE_NAMESPACE: str = Field(env="PFINNI_SURREALDB_NAMESPACE")

    # SurrealDB Cache Settings
    CACHE_ENABLED: bool = Field(default=True, env="PFINNI_CACHE_ENABLED")
    CACHE_DATABASE_URL: str = Field(default="ws://localhost:8080/rpc", env="PFINNI_CACHE_DATABASE_URL")
    CACHE_DATABASE_NAME: str = Field(default="patient_dashboard_cache", env="PFINNI_CACHE_DATABASE_NAME")
    CACHE_NAMESPACE: str = Field(default="cache", env="PFINNI_CACHE_NAMESPACE")
    CACHE_TTL: int = Field(default=300, env="PFINNI_CACHE_TTL")  # 5 minutes

    # CORS Settings  
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000",
        env="PFINNI_CORS_ORIGINS",
    )
    CORS_CREDENTIALS: bool = Field(default=True, env="PFINNI_CORS_CREDENTIALS")
    ALLOWED_HOSTS: str = Field(
        default="localhost,127.0.0.1",
        env="ALLOWED_HOSTS",
    )

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="PFINNI_RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="PFINNI_RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="PFINNI_RATE_LIMIT_WINDOW")

    # File Upload Settings
    MAX_FILE_SIZE: int = Field(default=10485760, env="PFINNI_MAX_FILE_SIZE")  # 10MB
    UPLOAD_DIR: str = Field(default="./uploads", env="PFINNI_UPLOAD_DIR")
    ALLOWED_FILE_TYPES: str = Field(
        default="pdf,jpg,jpeg,png,doc,docx",
        env="PFINNI_ALLOWED_FILE_TYPES",
    )

    # BetterAuth Configuration
    BETTER_AUTH_SECRET: str = Field(env="PFINNI_BETTER_AUTH_SECRET")
    BETTER_AUTH_URL: str = Field(default="http://localhost:8000", env="PFINNI_BETTER_AUTH_URL")
    BETTER_AUTH_DATABASE_URL: Optional[str] = Field(default=None, env="PFINNI_BETTER_AUTH_DATABASE_URL")
    BETTER_AUTH_COOKIE_DOMAIN: str = Field(default="localhost", env="PFINNI_BETTER_AUTH_COOKIE_DOMAIN")
    BETTER_AUTH_COOKIE_SECURE: bool = Field(default=False, env="PFINNI_BETTER_AUTH_COOKIE_SECURE")
    BETTER_AUTH_SESSION_EXPIRES: str = Field(default="7d", env="PFINNI_BETTER_AUTH_SESSION_EXPIRES")

    # External Services
    LOGFIRE_TOKEN: Optional[str] = Field(default=None, env="PFINNI_LOGFIRE_TOKEN")
    LOGFIRE_SERVICE_NAME: str = Field(default="pfinni-patient-dashboard", env="PFINNI_LOGFIRE_SERVICE_NAME")
    LOGFIRE_PROJECT_NAME: str = Field(default="pfinni", env="PFINNI_LOGFIRE_PROJECT_NAME")
    RESEND_API_KEY: Optional[str] = Field(default=None, env="PFINNI_RESEND_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="SHARED_ANTHROPIC_API_KEY")
    CLERK_SECRET_KEY: Optional[str] = Field(default=None, env="PFINNI_CLERK_SECRET_KEY")
    CLERK_PUBLISHABLE_KEY: Optional[str] = Field(default=None, env="PFINNI_CLERK_PUBLISHABLE_KEY")

    # Insurance Integration
    INSURANCE_CLIENT_ID: Optional[str] = Field(default=None, env="PFINNI_INSURANCE_CLIENT_ID")
    INSURANCE_CLIENT_SECRET: Optional[str] = Field(default=None, env="PFINNI_INSURANCE_CLIENT_SECRET")
    INSURANCE_API_URL: Optional[str] = Field(default=None, env="PFINNI_INSURANCE_API_URL")
    WEBHOOK_SECRET: Optional[str] = Field(default=None, env="PFINNI_WEBHOOK_SECRET")

    # Email Settings
    SMTP_HOST: str = Field(default="smtp.resend.com", env="PFINNI_SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="PFINNI_SMTP_PORT")
    FROM_EMAIL: str = Field(default="noreply@memorial-hc.com", env="PFINNI_FROM_EMAIL")
    FROM_NAME: str = Field(default="Memorial Healthcare Center", env="PFINNI_FROM_NAME")

    # Monitoring Settings
    ENABLE_METRICS: bool = Field(default=True, env="PFINNI_ENABLE_METRICS")
    METRICS_PORT: int = Field(default=8001, env="PFINNI_METRICS_PORT")

    # Background Jobs Settings (SurrealDB)
    JOB_QUEUE_DATABASE_URL: str = Field(default="ws://localhost:8080/rpc", env="PFINNI_JOB_QUEUE_DATABASE_URL")
    JOB_QUEUE_DATABASE_NAME: str = Field(default="patient_dashboard_jobs", env="PFINNI_JOB_QUEUE_DATABASE_NAME")
    JOB_QUEUE_NAMESPACE: str = Field(default="jobs", env="PFINNI_JOB_QUEUE_NAMESPACE")
    BIRTHDAY_ALERT_HOUR: int = Field(default=6, env="PFINNI_BIRTHDAY_ALERT_HOUR")
    INSURANCE_SYNC_HOUR: int = Field(default=2, env="PFINNI_INSURANCE_SYNC_HOUR")

    # Audit & Compliance Settings
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=2555, env="AUDIT_LOG_RETENTION_DAYS")  # 7 years
    HIPAA_COMPLIANT_LOGGING: bool = Field(default=True, env="HIPAA_COMPLIANT_LOGGING")
    ENCRYPT_AUDIT_LOGS: bool = Field(default=True, env="ENCRYPT_AUDIT_LOGS")

    # Feature Flags
    ENABLE_INSURANCE_INTEGRATION: bool = Field(default=True, env="ENABLE_INSURANCE_INTEGRATION")
    ENABLE_REAL_TIME_ALERTS: bool = Field(default=True, env="ENABLE_REAL_TIME_ALERTS")
    ENABLE_BIRTHDAY_ALERTS: bool = Field(default=True, env="ENABLE_BIRTHDAY_ALERTS")
    ENABLE_WEBHOOK_ENDPOINTS: bool = Field(default=True, env="ENABLE_WEBHOOK_ENDPOINTS")

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as a list."""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        return [ftype.strip() for ftype in self.ALLOWED_FILE_TYPES.split(",")]

    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    @field_validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment."""
        valid_environments = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_environments:
            raise ValueError(f"ENVIRONMENT must be one of {valid_environments}")
        return v.lower()

    @field_validator("ENCRYPTION_KEY")
    def validate_encryption_key(cls, v):
        """Validate encryption key length."""
        if len(v) != 32:
            raise ValueError("ENCRYPTION_KEY must be exactly 32 characters")
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.ENVIRONMENT == "testing"

    @property
    def database_config(self) -> dict:
        """Get database configuration dictionary."""
        return {
            "url": self.DATABASE_URL,
            "user": self.DATABASE_USER,
            "password": self.DATABASE_PASS,
            "database": self.DATABASE_NAME,
            "namespace": self.DATABASE_NAMESPACE,
        }

    @property
    def cache_config(self) -> dict:
        """Get SurrealDB cache configuration dictionary."""
        return {
            "url": self.CACHE_DATABASE_URL,
            "database": self.CACHE_DATABASE_NAME,
            "namespace": self.CACHE_NAMESPACE,
            "ttl": self.CACHE_TTL,
        }

    @property
    def job_queue_config(self) -> dict:
        """Get SurrealDB job queue configuration dictionary."""
        return {
            "url": self.JOB_QUEUE_DATABASE_URL,
            "database": self.JOB_QUEUE_DATABASE_NAME,
            "namespace": self.JOB_QUEUE_NAMESPACE,
            "task_timeout": 30 * 60,  # 30 minutes
            "retry_attempts": 3,
            "birthday_alert_hour": self.BIRTHDAY_ALERT_HOUR,
            "insurance_sync_hour": self.INSURANCE_SYNC_HOUR,
        }

    @property
    def email_config(self) -> dict:
        """Get email configuration dictionary."""
        return {
            "smtp_host": self.SMTP_HOST,
            "smtp_port": self.SMTP_PORT,
            "from_email": self.FROM_EMAIL,
            "from_name": self.FROM_NAME,
            "api_key": self.RESEND_API_KEY,
        }

    @property
    def insurance_config(self) -> dict:
        """Get insurance integration configuration."""
        return {
            "client_id": self.INSURANCE_CLIENT_ID,
            "client_secret": self.INSURANCE_CLIENT_SECRET,
            "api_url": self.INSURANCE_API_URL,
            "webhook_secret": self.WEBHOOK_SECRET,
            "enabled": self.ENABLE_INSURANCE_INTEGRATION,
        }

    @property
    def better_auth_config(self) -> dict:
        """Get BetterAuth configuration dictionary."""
        return {
            "secret": self.BETTER_AUTH_SECRET,
            "url": self.BETTER_AUTH_URL,
            "database_url": self.BETTER_AUTH_DATABASE_URL or self.DATABASE_URL,
            "cookie_domain": self.BETTER_AUTH_COOKIE_DOMAIN,
            "cookie_secure": self.BETTER_AUTH_COOKIE_SECURE,
            "session_expires": self.BETTER_AUTH_SESSION_EXPIRES,
        }



@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment specific settings."""
    DEBUG: bool = True
    RELOAD: bool = True
    LOG_LEVEL: str = "DEBUG"
    RATE_LIMIT_ENABLED: bool = False


class ProductionSettings(Settings):
    """Production environment specific settings."""
    DEBUG: bool = False
    RELOAD: bool = False
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_ENABLED: bool = True


class TestingSettings(Settings):
    """Testing environment specific settings."""
    DEBUG: bool = True
    ENVIRONMENT: str = "testing"
    DATABASE_NAME: str = "patient_dashboard_test"
    RATE_LIMIT_ENABLED: bool = False
    ENABLE_METRICS: bool = False


def get_environment_settings() -> Settings:
    """Get environment-specific settings."""
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
