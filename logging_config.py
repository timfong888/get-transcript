"""
Centralized logging configuration for Google Cloud Logging integration.
Supports both local development and production environments.
"""

import os
import logging
import json
from typing import Optional, Dict, Any
import uuid
from contextvars import ContextVar

# Context variable for request correlation
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging with Google Cloud Logging compatibility."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Get request ID from context
        request_id = request_id_context.get()
        
        # Create structured log entry
        log_entry = {
            'timestamp': self.formatTime(record),
            'severity': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add request ID if available
        if request_id:
            log_entry['request_id'] = request_id
            
        # Add extra fields from record
        if hasattr(record, 'video_id'):
            log_entry['video_id'] = record.video_id
        if hasattr(record, 'proxy_ip'):
            log_entry['proxy_ip'] = record.proxy_ip
        if hasattr(record, 'api_key_valid'):
            log_entry['api_key_valid'] = record.api_key_valid
        if hasattr(record, 'external_request_id'):
            log_entry['external_request_id'] = record.external_request_id
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def setup_google_cloud_logging() -> bool:
    """
    Set up Google Cloud Logging if credentials are available.
    Returns True if successful, False otherwise.
    """
    try:
        from google.cloud import logging as gcp_logging
        from google.auth.exceptions import DefaultCredentialsError
        import json
        import tempfile

        # Check if we have JSON credentials in environment
        creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

        if creds_json and project_id:
            # Write credentials to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(creds_json)
                temp_creds_path = f.name

            # Set environment variable for Google Cloud client
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_creds_path

            # Initialize client with explicit project
            client = gcp_logging.Client(project=project_id)
        else:
            # Try default credentials
            client = gcp_logging.Client()

        # Set up logging integration
        client.setup_logging()

        print("✅ Google Cloud Logging configured successfully")
        return True

    except ImportError:
        print("⚠️ google-cloud-logging not installed, using local logging only")
        return False
    except DefaultCredentialsError:
        print("⚠️ Google Cloud credentials not found, using local logging only")
        return False
    except Exception as e:
        print(f"⚠️ Failed to setup Google Cloud Logging: {e}")
        return False

def setup_logging(service_name: str = "get-transcript", log_level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the application with Google Cloud Logging integration.
    
    Args:
        service_name: Name of the service for logging context
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    # Determine environment
    environment = os.getenv("ENVIRONMENT", "development")
    is_production = environment.lower() in ["production", "prod"]
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Try to set up Google Cloud Logging for production
    gcp_logging_enabled = False
    if is_production:
        gcp_logging_enabled = setup_google_cloud_logging()
    
    # Always set up console logging as fallback or for development
    console_handler = logging.StreamHandler()
    
    if gcp_logging_enabled:
        # Use simple format for GCP (it handles structured logging)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        # Use structured format for local development
        console_formatter = StructuredFormatter()
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Create service-specific logger
    logger = logging.getLogger(service_name)
    
    # Add service context to all log records
    old_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.service = service_name
        record.environment = environment
        return record
    
    logging.setLogRecordFactory(record_factory)
    
    logger.info(f"Logging configured for {service_name} in {environment} environment")
    if gcp_logging_enabled:
        logger.info("Google Cloud Logging enabled")
    else:
        logger.info("Using local logging only")
    
    return logger

def get_request_id() -> str:
    """Get or generate a request ID for correlation."""
    request_id = request_id_context.get()
    if not request_id:
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)
    return request_id

def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context."""
    request_id_context.set(request_id)

def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs) -> None:
    """
    Log a message with additional context fields.
    
    Args:
        logger: Logger instance
        level: Log level (info, warning, error, debug)
        message: Log message
        **kwargs: Additional context fields
    """
    # Get the logging method
    log_method = getattr(logger, level.lower())
    
    # Create a log record with extra fields
    extra = {}
    for key, value in kwargs.items():
        extra[key] = value
    
    log_method(message, extra=extra)
