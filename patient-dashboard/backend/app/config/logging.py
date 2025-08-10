"""
Logging configuration with Logfire integration for HIPAA-compliant audit logging.
"""
import os
import logging
import structlog
from typing import Any, Dict

# Set LOGFIRE_TOKEN before importing logfire
from dotenv import load_dotenv
load_dotenv('.env')  # Load from current directory
if os.getenv('PFINNI_LOGFIRE_TOKEN'):
    os.environ['LOGFIRE_TOKEN'] = os.getenv('PFINNI_LOGFIRE_TOKEN')

import logfire

def configure_logging() -> None:
    """Configure structured logging with Logfire integration."""
    
    # Get environment settings directly
    log_level = os.getenv("LOG_LEVEL", "INFO")
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Configure Logfire using Ptolemies pattern - simple and automatic
    try:
        # Token already set before import
        token = os.getenv('LOGFIRE_TOKEN')
        if not token:
            print("❌ No LOGFIRE_TOKEN found!")
            raise ValueError("No LOGFIRE_TOKEN found")
            
        # Get settings for other config
        from app.config.settings import get_settings
        settings = get_settings()
            
        # Configure with settings from environment
        service_name = settings.LOGFIRE_SERVICE_NAME
        project_name = settings.LOGFIRE_PROJECT_NAME
        
        # Set environment variables for Logfire
        os.environ['LOGFIRE_PROJECT_NAME'] = project_name
        
        logfire.configure(
            service_name=service_name,
            service_version='1.0.0',
            console=False,  # Disable console output in production
            send_to_logfire=True,  # Explicitly enable sending to Logfire
            inspect_arguments=False  # Disable argument inspection to avoid warnings
        )
        
        # Send startup log
        logfire.info(
            "Logfire initialized", 
            service="pfinni-patient-dashboard",
            environment=environment,
            version="1.0.0",
            token_preview=token[:20] + "..." if token else "None"
        )
        
        # Don't print in production to avoid cluttering logs
        if environment == "development":
            print(f"✅ Logfire configured successfully with token: {token[:20]}...")
    except Exception as e:
        if environment == "development":
            print(f"❌ Logfire configuration failed: {e}")
            print("Continuing without Logfire cloud logging...")
        # Continue without Logfire to prevent blocking the app
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s"
    )
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_app_context,
        filter_sensitive_data,
    ]
    
    if environment == "development":
        # Pretty printing for development
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # JSON for production
        processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def add_app_context(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add application context to all log entries."""
    event_dict["service"] = "pfinni-patient-dashboard"
    event_dict["environment"] = os.getenv("ENVIRONMENT", "development")
    event_dict["version"] = "1.0.0"  # TODO: Get from package version
    return event_dict

def filter_sensitive_data(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Filter out sensitive data to ensure HIPAA compliance."""
    
    # List of sensitive field names to redact
    sensitive_fields = {
        "password", "password_hash", "ssn", "social_security_number",
        "date_of_birth", "dob", "medical_record_number", "mrn",
        "credit_card", "card_number", "cvv", "pin",
        "api_key", "secret", "token", "authorization"
    }
    
    def redact_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively redact sensitive fields in a dictionary."""
        redacted = {}
        for key, value in d.items():
            # Check if key contains sensitive field name
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = [
                    redact_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                redacted[key] = value
        return redacted
    
    # Apply redaction
    return redact_dict(event_dict)

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)

class AuditLogger:
    """Special logger for HIPAA-compliant audit logging."""
    
    def __init__(self):
        self.logger = structlog.get_logger("audit")
    
    def log_access(
        self,
        user_id: str,
        user_email: str,
        user_role: str,
        action: str,
        resource_type: str,
        resource_id: str = None,
        success: bool = True,
        error_message: str = None,
        **kwargs
    ) -> None:
        """Log a data access event for audit trail."""
        self.logger.info(
            "data_access",
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            success=success,
            error_message=error_message,
            **kwargs
        )
    
    def log_authentication(
        self,
        email: str,
        action: str,
        success: bool,
        ip_address: str = None,
        user_agent: str = None,
        error_message: str = None
    ) -> None:
        """Log authentication events."""
        self.logger.info(
            "authentication",
            email=email,
            action=action,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message
        )
    
    def log_status_change(
        self,
        user_id: str,
        patient_id: str,
        old_status: str,
        new_status: str,
        reason: str = None
    ) -> None:
        """Log patient status changes."""
        self.logger.info(
            "status_change",
            user_id=user_id,
            patient_id=patient_id,
            old_status=old_status,
            new_status=new_status,
            reason=reason
        )

# Global audit logger instance
audit_logger = AuditLogger()