import json
import logging
import requests
import random
from typing import Dict, Any
from firebase_functions import https_fn
from firebase_functions.params import SecretParam
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    RequestBlocked,
    CouldNotRetrieveTranscript
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_video_id(video_id: str) -> bool:
    """Validate YouTube video ID format."""
    if not video_id or not isinstance(video_id, str):
        return False

    # YouTube video IDs are typically 11 characters long
    # and contain alphanumeric characters, hyphens, and underscores
    if len(video_id) != 11:
        return False

    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
    return all(c in allowed_chars for c in video_id)


def get_backbone_proxy(proxy_username: str, proxy_password: str) -> tuple:
    """
    Get a random backbone proxy for stable endpoint with rotating IPs.

    Args:
        proxy_username: Base Webshare proxy username
        proxy_password: Webshare proxy password

    Returns:
        Tuple of (proxy_url, proxy_description) for the selected backbone proxy
    """
    try:
        logger.info("🏗️ Selecting random backbone proxy for stable endpoint...")

        # Select a random backbone proxy (1-25 based on Webshare API data)
        proxy_number = random.randint(1, 25)
        proxy_host = "p.webshare.io"
        proxy_port = 10000 + proxy_number - 1  # ports start at 10000
        full_username = f"{proxy_username}-{proxy_number}"

        # Create the backbone proxy URL
        proxy_url = f"http://{full_username}:{proxy_password}@{proxy_host}:{proxy_port}"
        proxy_description = f"{full_username}@{proxy_host}:{proxy_port}"

        logger.info(f"🎯 Selected backbone proxy: {proxy_description}")
        logger.info("📍 This provides stable endpoint with rotating residential IPs")

        return proxy_url, proxy_description

    except Exception as e:
        logger.error(f"❌ Error selecting backbone proxy: {str(e)}")
        # Fallback to first backbone proxy
        fallback_url = f"http://{proxy_username}-1:{proxy_password}@p.webshare.io:10000"
        return fallback_url, f"{proxy_username}-1@p.webshare.io:10000"


def test_proxy_ip(proxy_username: str, proxy_password: str) -> str:
    """
    Test a backbone proxy by making a request to httpbin.org/ip.

    Args:
        proxy_username: Webshare proxy username
        proxy_password: Webshare proxy password

    Returns:
        The IP address being used through the backbone proxy
    """
    try:
        logger.info("🌐 Testing Webshare backbone proxy...")

        # Get a backbone proxy for testing
        proxy_url, proxy_description = get_backbone_proxy(proxy_username, proxy_password)

        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        logger.info(f"📡 Making test request through backbone proxy: {proxy_description}")

        # Make request to httpbin.org/ip to get the IP address
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)

        if response.status_code == 200:
            ip_data = response.json()
            proxy_ip = ip_data.get('origin', 'Unknown')
            logger.info(f"✅ Backbone proxy test successful! Using IP: {proxy_ip}")
            return proxy_ip
        else:
            logger.error(f"❌ Backbone proxy test failed with status code: {response.status_code}")
            return "Unknown"

    except Exception as e:
        logger.error(f"❌ Backbone proxy test failed with exception: {str(e)}")
        return "Unknown"


def get_video_transcript(video_id: str, proxy_username: str, proxy_password: str) -> Dict[str, Any]:
    """
    Retrieve transcript for a YouTube video.

    Args:
        video_id: YouTube video ID
        proxy_username: Proxy username
        proxy_password: Proxy password

    Returns:
        Dictionary containing transcript data

    Raises:
        Various YouTube API exceptions
    """
    logger.info(f"=== STARTING get_video_transcript for video: {video_id} ===")

    if not validate_video_id(video_id):
        logger.error(f"Invalid video ID format: {video_id}")
        raise ValueError("Invalid video ID format")

    logger.info("✅ Video ID validation passed")

    try:
        # Initialize YouTube Transcript API with Webshare proxy
        logger.info(f"🔧 STEP 1: Configuring Webshare proxy")
        logger.info(f"📝 Proxy username: {proxy_username}")
        logger.info(f"📝 Proxy username length: {len(proxy_username)}")
        logger.info(f"📝 Proxy password length: {len(proxy_password)}")
        logger.info("🌐 Creating backbone proxy configuration...")

        # Get a backbone proxy for this request (stable endpoint + rotating IPs)
        proxy_url, proxy_description = get_backbone_proxy(proxy_username, proxy_password)

        # Test the proxy IP address before using it
        proxy_ip = test_proxy_ip(proxy_username, proxy_password)
        logger.info(f"🔍 Proxy IP test result: {proxy_ip}")

        # Use GenericProxyConfig with backbone proxy for stable endpoint
        proxy_config = GenericProxyConfig(
            http_url=proxy_url,
            https_url=proxy_url,
        )
        logger.info(f"✅ GenericProxyConfig created with backbone proxy: {proxy_description}")
        logger.info("📍 Stable endpoint with rotating residential IPs enabled")

        logger.info("🔧 STEP 2: Creating YouTubeTranscriptApi with proxy config")
        ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        logger.info("✅ YouTubeTranscriptApi instance created with Webshare proxy")

        # Fetch transcript using the proxied API instance
        logger.info("🔧 STEP 3: Fetching transcript list via proxy...")
        transcript_list = ytt_api.list_transcripts(video_id)
        logger.info("✅ Transcript list retrieved successfully via proxy")

        # Try to get English transcript first, then any available transcript
        logger.info("🔧 STEP 4: Finding appropriate transcript...")
        try:
            transcript = transcript_list.find_transcript(['en'])
            logger.info("✅ Found English transcript")
        except NoTranscriptFound:
            logger.info("⚠️ No English transcript found, looking for alternatives...")
            # Get the first available transcript
            available_transcripts = list(transcript_list)
            if not available_transcripts:
                logger.error("❌ No transcripts available for this video")
                raise CouldNotRetrieveTranscript(video_id)
            transcript = available_transcripts[0]
            logger.info(f"✅ Using alternative transcript: {transcript.language_code}")

        # Fetch the actual transcript data
        logger.info("🔧 STEP 5: Fetching transcript data...")
        transcript_data = transcript.fetch()
        logger.info(f"✅ Transcript data retrieved: {len(transcript_data)} entries")

        # Combine all transcript text
        logger.info("🔧 STEP 6: Processing transcript data...")
        full_text = ' '.join([entry.text for entry in transcript_data])
        logger.info(f"✅ Transcript text combined: {len(full_text)} characters")

        # Get basic video info from transcript metadata if available
        video_title = getattr(transcript, 'video_title', f"Video {video_id}")

        result = {
            "transcript": full_text,
            "language": transcript.language_code,
            "title": video_title,
            "channel": "Unknown Channel",  # Channel info not available from transcript API
            "videoId": video_id
        }

        logger.info(f"🎉 SUCCESS: Retrieved transcript for video {video_id} via Webshare proxy")
        logger.info(f"📊 Final result: {len(transcript_data)} entries, {len(full_text)} chars, language: {transcript.language_code}")
        return result

    except Exception as e:
        logger.error(f"❌ ERROR in get_video_transcript for video {video_id}: {str(e)}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        raise

# Define secrets
api_key_secret = SecretParam("API_KEY")
proxy_username_secret = SecretParam("PROXY_USERNAME")
proxy_password_secret = SecretParam("PROXY_PASSWORD")

@https_fn.on_request(secrets=[api_key_secret, proxy_username_secret, proxy_password_secret])
def get_transcript(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP Cloud Function to get YouTube video transcript.
    
    Expected request format:
    GET /get_transcript?videoId=VIDEO_ID
    or
    POST /get_transcript with JSON body: {"videoId": "VIDEO_ID"}
    
    Headers:
    Authorization: Bearer API_KEY
    """
    
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

    # Handle preflight requests
    if req.method == 'OPTIONS':
        return https_fn.Response('', status=204, headers=headers)
    
    try:
        logger.info("🚀 === FIREBASE FUNCTION STARTED ===")
        logger.info(f"📥 Request method: {req.method}")

        # Authentication check
        logger.info("🔐 STEP 1: Checking authentication...")
        auth_header = req.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("❌ Unauthorized request - missing or invalid Authorization header")
            return https_fn.Response(
                json.dumps({
                    "error": "UNAUTHORIZED",
                    "message": "Missing or invalid Authorization header"
                }),
                status=401,
                headers={**headers, 'Content-Type': 'application/json'}
            )

        # Extract and validate API key
        logger.info("🔑 STEP 2: Validating API key...")
        request_api_key = auth_header.split(' ')[1]
        expected_api_key = api_key_secret.value
        logger.info("✅ API key retrieved from secrets")

        if request_api_key != expected_api_key:
            logger.warning("❌ Unauthorized request - invalid API key")
            return https_fn.Response(
                json.dumps({
                    "error": "UNAUTHORIZED",
                    "message": "Invalid API key"
                }),
                status=401,
                headers={**headers, 'Content-Type': 'application/json'}
            )

        logger.info("✅ API key validation passed")
        
        # Check if this is an IP check request
        if req.method == 'GET' and req.args.get('check') == 'ip':
            logger.info("🔍 IP check request received - getting cloud function IP")
            try:
                response = requests.get('https://httpbin.org/ip', timeout=10)
                if response.status_code == 200:
                    ip_data = response.json()
                    cloud_ip = ip_data.get('origin', 'Unknown')
                    logger.info(f"☁️ Cloud function IP: {cloud_ip}")
                    return https_fn.Response(
                        json.dumps({"cloud_function_ip": cloud_ip}),
                        status=200,
                        headers={**headers, 'Content-Type': 'application/json'}
                    )
                else:
                    return https_fn.Response(
                        json.dumps({"error": "Failed to get IP"}),
                        status=500,
                        headers={**headers, 'Content-Type': 'application/json'}
                    )
            except Exception as e:
                logger.error(f"Error getting IP: {str(e)}")
                return https_fn.Response(
                    json.dumps({"error": str(e)}),
                    status=500,
                    headers={**headers, 'Content-Type': 'application/json'}
                )

        # Extract video ID from request
        logger.info("📹 STEP 3: Extracting video ID from request...")
        video_id = None
        if req.method == 'GET':
            video_id = req.args.get('videoId')
            logger.info(f"📥 GET request - video ID: {video_id}")
        elif req.method == 'POST':
            try:
                data = req.get_json()
                video_id = data.get('videoId') if data else None
                logger.info(f"📥 POST request - video ID: {video_id}")
            except Exception as e:
                logger.error(f"❌ Invalid JSON in POST request: {str(e)}")
                return https_fn.Response(
                    json.dumps({
                        "error": "INVALID_REQUEST",
                        "message": "POST request must contain valid JSON data"
                    }),
                    status=400,
                    headers={**headers, 'Content-Type': 'application/json'}
                )

        if not video_id:
            logger.error("❌ Missing video ID in request")
            return https_fn.Response(
                json.dumps({
                    "error": "MISSING_VIDEO_ID",
                    "message": "videoId parameter is required"
                }),
                status=400,
                headers={**headers, 'Content-Type': 'application/json'}
            )

        logger.info(f"✅ Video ID extracted: {video_id}")

        # Get transcript using proxy
        logger.info("🔧 STEP 4: Retrieving proxy credentials from secrets...")
        proxy_username = proxy_username_secret.value
        proxy_password = proxy_password_secret.value
        logger.info(f"✅ Proxy credentials retrieved - username: {proxy_username}")

        logger.info("🎬 STEP 5: Calling get_video_transcript...")
        result = get_video_transcript(video_id, proxy_username, proxy_password)

        logger.info(f"🎉 Successfully processed request for video {video_id}")
        return https_fn.Response(
            json.dumps(result),
            status=200,
            headers={**headers, 'Content-Type': 'application/json'}
        )
        
    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        return https_fn.Response(
            json.dumps({
                "error": "INVALID_VIDEO_ID",
                "message": str(e)
            }),
            status=400,
            headers={**headers, 'Content-Type': 'application/json'}
        )

    except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript) as e:
        logger.info(f"No transcript available for video {video_id}: {str(e)}")
        return https_fn.Response(
            json.dumps({
                "error": "TRANSCRIPT_NOT_AVAILABLE",
                "message": "No transcript available for this video",
                "videoId": video_id
            }),
            status=404,
            headers={**headers, 'Content-Type': 'application/json'}
        )

    except VideoUnavailable as e:
        logger.info(f"Video unavailable: {video_id}: {str(e)}")
        return https_fn.Response(
            json.dumps({
                "error": "VIDEO_UNAVAILABLE",
                "message": "Video is unavailable or private",
                "videoId": video_id
            }),
            status=404,
            headers={**headers, 'Content-Type': 'application/json'}
        )

    except RequestBlocked as e:
        logger.warning(f"Rate limited for video {video_id}: {str(e)}")
        return https_fn.Response(
            json.dumps({
                "error": "RATE_LIMITED",
                "message": "Too many requests, please try again later",
                "videoId": video_id
            }),
            status=429,
            headers={**headers, 'Content-Type': 'application/json'}
        )

    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        return https_fn.Response(
            json.dumps({
                "error": "INTERNAL_ERROR",
                "message": "An internal error occurred"
            }),
            status=500,
            headers={**headers, 'Content-Type': 'application/json'}
        )
