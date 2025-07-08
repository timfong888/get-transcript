#!/usr/bin/env python3
"""
Test script for the get-transcript Firebase Function
"""

import requests
import json
import sys
import os

# Test configuration
FUNCTION_URL = "https://get-transcript.fly.dev/get_transcript"
API_KEY = os.getenv("API_KEY", "YOUR_API_KEY_HERE")

# Test video IDs
TEST_VIDEOS = {
    "valid_with_transcript": "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
    "valid_short": "jNQXAC9IVRw",  # Me at the zoo (first YouTube video)
    "invalid_format": "invalid123",
    "nonexistent": "aaaaaaaaaaa"
}

def test_get_request(video_id: str, description: str):
    """Test GET request format"""
    print(f"\n--- Testing GET: {description} ---")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{FUNCTION_URL}?videoId={video_id}",
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code, response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response.text}")
        return response.status_code, None

def test_post_request(video_id: str, description: str):
    """Test POST request format"""
    print(f"\n--- Testing POST: {description} ---")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {"videoId": video_id}
    
    try:
        response = requests.post(
            FUNCTION_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code, response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response.text}")
        return response.status_code, None

def test_authentication():
    """Test authentication scenarios"""
    print("\n=== AUTHENTICATION TESTS ===")
    
    # Test without authorization header
    print("\n--- Testing without Authorization header ---")
    try:
        response = requests.get(f"{FUNCTION_URL}?videoId={TEST_VIDEOS['valid_with_transcript']}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with invalid API key
    print("\n--- Testing with invalid API key ---")
    headers = {"Authorization": "Bearer invalid-key"}
    try:
        response = requests.get(
            f"{FUNCTION_URL}?videoId={TEST_VIDEOS['valid_with_transcript']}",
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_cors():
    """Test CORS preflight request"""
    print("\n=== CORS TEST ===")
    
    try:
        response = requests.options(FUNCTION_URL)
        print(f"Status Code: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all tests"""
    print("=== GET-TRANSCRIPT FUNCTION TESTS ===")
    print(f"Function URL: {FUNCTION_URL}")
    print(f"API Key: {API_KEY[:10]}..." if API_KEY != "your-api-key-here" else "API Key: NOT SET")
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\nERROR: Please set the API_KEY environment variable or update the script")
        print("Usage: API_KEY=your_actual_key python test_function.py")
        sys.exit(1)
    
    if FUNCTION_URL == "https://your-region-your-project.cloudfunctions.net/get_transcript":
        print("\nERROR: Please update the FUNCTION_URL variable in this script")
        sys.exit(1)
    
    # Test authentication
    test_authentication()
    
    # Test CORS
    test_cors()
    
    # Test valid video with transcript
    test_get_request(TEST_VIDEOS["valid_with_transcript"], "Valid video with transcript (GET)")
    test_post_request(TEST_VIDEOS["valid_with_transcript"], "Valid video with transcript (POST)")
    
    # Test another valid video
    test_get_request(TEST_VIDEOS["valid_short"], "Another valid video (GET)")
    
    # Test invalid video ID format
    test_get_request(TEST_VIDEOS["invalid_format"], "Invalid video ID format")
    
    # Test nonexistent video
    test_get_request(TEST_VIDEOS["nonexistent"], "Nonexistent video ID")
    
    # Test missing video ID
    print("\n--- Testing missing video ID ---")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    try:
        response = requests.get(FUNCTION_URL, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== TESTS COMPLETED ===")

if __name__ == "__main__":
    main()
