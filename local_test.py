#!/usr/bin/env python3
"""
Local testing script for the get-transcript function
This allows testing the core functionality without deploying to Firebase
"""

import os
import sys
import json
from unittest.mock import Mock, patch

# Add the functions directory to the path
sys.path.insert(0, 'functions')

# Mock environment variables for local testing
os.environ['GCP_PROJECT'] = 'test-project'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'

def mock_secret_manager():
    """Mock Secret Manager for local testing"""
    secrets = {
        'PROXY_USERNAME': 'spm8v50ymm',
        'PROXY_PASSWORD': 'gVxie4oev28muJwZM3',
        'API_KEY': 'test-api-key-12345'
    }
    
    def mock_access_secret_version(request):
        secret_name = request['name'].split('/')[-3]  # Extract secret name
        if secret_name in secrets:
            mock_response = Mock()
            mock_response.payload.data.decode.return_value = secrets[secret_name]
            return mock_response
        else:
            raise Exception(f"Secret {secret_name} not found")
    
    return mock_access_secret_version

def test_transcript_service():
    """Test the TranscriptService class locally"""
    
    # Mock the Secret Manager
    with patch('google.cloud.secretmanager.SecretManagerServiceClient') as mock_client:
        mock_client.return_value.access_secret_version = mock_secret_manager()
        
        # Import after mocking
        from main import TranscriptService
        
        service = TranscriptService()
        
        # Test video ID validation
        print("Testing video ID validation...")
        assert service._validate_video_id("dQw4w9WgXcQ") == True
        assert service._validate_video_id("invalid123") == False
        assert service._validate_video_id("") == False
        assert service._validate_video_id(None) == False
        print("✓ Video ID validation tests passed")
        
        # Test proxy configuration
        print("\nTesting proxy configuration...")
        try:
            proxy_config = service._get_proxy_config()
            print(f"✓ Proxy configuration created successfully")
            print(f"  HTTP URL: {proxy_config.http_url}")
            print(f"  HTTPS URL: {proxy_config.https_url}")
        except Exception as e:
            print(f"✗ Proxy configuration failed: {e}")
        
        # Test transcript retrieval (this will make actual API calls)
        print("\nTesting transcript retrieval...")
        test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        
        try:
            result = service.get_transcript(test_video_id)
            print(f"✓ Transcript retrieved successfully")
            print(f"  Video ID: {result['videoId']}")
            print(f"  Language: {result['language']}")
            print(f"  Title: {result['title']}")
            print(f"  Transcript length: {len(result['transcript'])} characters")
            print(f"  First 100 chars: {result['transcript'][:100]}...")
        except Exception as e:
            print(f"✗ Transcript retrieval failed: {e}")
            print(f"  This might be due to proxy issues or YouTube blocking")

def test_flask_request_simulation():
    """Test the Flask request handling"""
    
    with patch('google.cloud.secretmanager.SecretManagerServiceClient') as mock_client:
        mock_client.return_value.access_secret_version = mock_secret_manager()
        
        from main import get_transcript
        
        # Mock Flask request for GET
        print("\nTesting GET request simulation...")
        mock_request = Mock()
        mock_request.method = 'GET'
        mock_request.headers = {'Authorization': 'Bearer test-api-key-12345'}
        mock_request.args = {'videoId': 'dQw4w9WgXcQ'}
        
        try:
            with patch('functions_framework.http'):
                response = get_transcript(mock_request)
                print(f"✓ GET request handled successfully")
                print(f"  Response type: {type(response)}")
        except Exception as e:
            print(f"✗ GET request failed: {e}")
        
        # Mock Flask request for POST
        print("\nTesting POST request simulation...")
        mock_request.method = 'POST'
        mock_request.is_json = True
        mock_request.get_json.return_value = {'videoId': 'dQw4w9WgXcQ'}
        
        try:
            response = get_transcript(mock_request)
            print(f"✓ POST request handled successfully")
        except Exception as e:
            print(f"✗ POST request failed: {e}")

def main():
    """Run local tests"""
    print("=== LOCAL TESTING FOR GET-TRANSCRIPT FUNCTION ===")
    print("This script tests the core functionality without deploying to Firebase")
    print()
    
    # Test the service class
    test_transcript_service()
    
    # Test Flask request handling
    test_flask_request_simulation()
    
    print("\n=== LOCAL TESTING COMPLETED ===")
    print("\nNote: Some tests may fail due to network restrictions or proxy issues.")
    print("This is normal for local testing. Deploy to Firebase for full functionality.")

if __name__ == "__main__":
    main()
