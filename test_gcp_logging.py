#!/usr/bin/env python3
"""
Test script to verify Google Cloud Logging integration.
Run this locally or on Fly.io to test the logging setup.
"""

import os
import sys
import time
from logging_config import setup_logging, log_with_context, get_request_id, set_request_id

def test_local_logging():
    """Test local structured logging."""
    print("=== Testing Local Structured Logging ===")
    
    # Set up logging in development mode
    os.environ["ENVIRONMENT"] = "development"
    logger = setup_logging("test-local", "INFO")
    
    # Generate test request ID
    request_id = get_request_id()
    set_request_id(request_id)
    
    # Test various log levels with context
    log_with_context(logger, "info", "Test info message", 
                     request_id=request_id, test_type="local")
    
    log_with_context(logger, "warning", "Test warning message", 
                     request_id=request_id, test_type="local", warning_code="TEST_001")
    
    log_with_context(logger, "error", "Test error message", 
                     request_id=request_id, test_type="local", error_code="TEST_002")
    
    print("✅ Local logging test completed")

def test_gcp_logging():
    """Test Google Cloud Logging integration."""
    print("=== Testing Google Cloud Logging ===")
    
    # Set up logging in production mode
    os.environ["ENVIRONMENT"] = "production"
    logger = setup_logging("test-gcp", "INFO")
    
    # Generate test request ID
    request_id = get_request_id()
    set_request_id(request_id)
    
    # Test various log levels with context
    log_with_context(logger, "info", "GCP test info message", 
                     request_id=request_id, test_type="gcp", video_id="test123")
    
    log_with_context(logger, "warning", "GCP test warning message", 
                     request_id=request_id, test_type="gcp", api_key_valid=False)
    
    log_with_context(logger, "error", "GCP test error message", 
                     request_id=request_id, test_type="gcp", 
                     error_type="TEST_ERROR", exception="Test exception details")
    
    print("✅ Google Cloud Logging test completed")
    print(f"📋 Request ID for correlation: {request_id}")

def test_environment_detection():
    """Test environment detection logic."""
    print("=== Testing Environment Detection ===")
    
    # Test development environment
    os.environ["ENVIRONMENT"] = "development"
    logger1 = setup_logging("test-env-dev", "INFO")
    logger1.info("This should use local logging")
    
    # Test production environment
    os.environ["ENVIRONMENT"] = "production"
    logger2 = setup_logging("test-env-prod", "INFO")
    logger2.info("This should attempt Google Cloud Logging")
    
    print("✅ Environment detection test completed")

def check_credentials():
    """Check if Google Cloud credentials are available."""
    print("=== Checking Google Cloud Credentials ===")
    
    creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    print(f"GOOGLE_APPLICATION_CREDENTIALS_JSON: {'✅ Set' if creds_json else '❌ Not set'}")
    print(f"GOOGLE_CLOUD_PROJECT: {'✅ Set' if project_id else '❌ Not set'}")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {'✅ Set' if creds_file else '❌ Not set'}")
    
    if creds_json and project_id:
        print("✅ JSON credentials available for Fly.io deployment")
    elif creds_file:
        print("✅ File-based credentials available for local development")
    else:
        print("⚠️ No Google Cloud credentials found")
    
    # Test Google Cloud client initialization
    try:
        from google.cloud import logging as gcp_logging
        client = gcp_logging.Client()
        print("✅ Google Cloud Logging client initialized successfully")
        print(f"📋 Project ID: {client.project}")
    except Exception as e:
        print(f"❌ Failed to initialize Google Cloud Logging client: {e}")

def main():
    """Run all tests."""
    print("🧪 Google Cloud Logging Integration Test")
    print("=" * 50)
    
    # Check credentials first
    check_credentials()
    print()
    
    # Test environment detection
    test_environment_detection()
    print()
    
    # Test local logging
    test_local_logging()
    print()
    
    # Test GCP logging
    test_gcp_logging()
    print()
    
    print("🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Check Fly.io logs: flyctl logs")
    print("2. Check Google Cloud Logs: gcloud logging read 'jsonPayload.service=\"test-gcp\"'")
    print("3. Look for the request ID in both log sources for correlation")

if __name__ == "__main__":
    main()
