import json
import logging
import os
import requests
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
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

# FastAPI app
app = FastAPI(title="YouTube Transcript API", version="1.1.1")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TranscriptRequest(BaseModel):
    videoId: str
    compaction_id: Optional[str] = None

class TranscriptResponse(BaseModel):
    transcript: str
    language: str
    title: str
    channel: str
    videoId: str
    compaction_id: str
    status_code: int

# Environment variables
API_KEY = os.getenv("API_KEY")
WEBSHARE_USERNAME = os.getenv("WEBSHARE_USERNAME")
WEBSHARE_PASSWORD = os.getenv("WEBSHARE_PASSWORD")

def validate_video_id(video_id: str) -> bool:
    """Validate YouTube video ID format."""
    if not video_id or len(video_id) != 11:
        return False
    # Basic validation - YouTube video IDs are 11 characters of alphanumeric and some special chars
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
    return all(c in allowed_chars for c in video_id)

def test_proxy_ip(proxy_username: str, proxy_password: str) -> str:
    """Test the Webshare rotating proxy by making a request to httpbin.org/ip."""
    try:
        logger.info("🌐 Testing Webshare rotating proxy...")

        # Use the rotating proxy endpoint (same as WebshareProxyConfig uses)
        proxy_url = f"http://{proxy_username}-rotate:{proxy_password}@p.webshare.io:80"

        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        logger.info(f"📡 Making test request through rotating proxy: {proxy_username}-rotate@p.webshare.io:80")
        
        # Make request to httpbin.org/ip to get the IP address
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            ip_data = response.json()
            proxy_ip = ip_data.get('origin', 'Unknown')
            logger.info(f"✅ Rotating proxy test successful! Using IP: {proxy_ip}")
            return proxy_ip
        else:
            logger.error(f"❌ Rotating proxy test failed with status code: {response.status_code}")
            return "Unknown"

    except Exception as e:
        logger.error(f"❌ Rotating proxy test failed with exception: {str(e)}")
        return "Unknown"

def log_api_request_ip(session, proxy_username: str, proxy_password: str) -> str:
    """
    Log the actual IP address used by the YouTube Transcript API by intercepting requests.

    Args:
        session: The requests session used by the API
        proxy_username: Proxy username for logging context
        proxy_password: Proxy password for logging context

    Returns:
        The IP address used by the API, or "Unknown" if unable to determine
    """
    try:
        # Make a test request using the same session that the API will use
        logger.info("🔍 Testing actual API session IP...")
        response = session.get('https://httpbin.org/ip', timeout=10)

        if response.status_code == 200:
            ip_data = response.json()
            api_ip = ip_data.get('origin', 'Unknown')
            logger.info(f"✅ YouTube Transcript API will use IP: {api_ip}")
            return api_ip
        else:
            logger.error(f"❌ API session IP test failed with status code: {response.status_code}")
            return "Unknown"

    except Exception as e:
        logger.error(f"❌ API session IP test failed with exception: {str(e)}")
        return "Unknown"


def get_video_transcript(video_id: str, proxy_username: str, proxy_password: str, compaction_id: str) -> Dict[str, Any]:
    """Retrieve transcript for a YouTube video using the simplified 1.1.1 API."""
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
        logger.info("🌐 Creating WebshareProxyConfig for residential proxies...")

        # Test the proxy IP address before using it
        proxy_ip = test_proxy_ip(proxy_username, proxy_password)
        logger.info(f"🔍 Proxy IP test result: {proxy_ip}")

        # Use WebshareProxyConfig for proper Webshare residential proxy handling
        proxy_config = WebshareProxyConfig(
            proxy_username=proxy_username,
            proxy_password=proxy_password,
        )
        logger.info("✅ WebshareProxyConfig created for residential proxies")
        logger.info("📍 Using rotating endpoint with automatic residential IP rotation")

        logger.info("🔧 STEP 2: Creating YouTubeTranscriptApi with proxy config")
        ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        logger.info("✅ YouTubeTranscriptApi instance created with Webshare proxy")

        # Log the actual IP that will be used by the API
        if hasattr(ytt_api, '_http_client') and ytt_api._http_client:
            api_ip = log_api_request_ip(ytt_api._http_client, proxy_username, proxy_password)
            logger.info(f"🌐 Actual API IP: {api_ip}")
        else:
            logger.warning("⚠️ Unable to access API session for IP logging")

        # Use the simplified 1.1.1 API - fetch transcript directly
        logger.info("🔧 STEP 3: Fetching transcript using simplified API...")
        try:
            # Try English first, then fallback to any available language
            fetched_transcript = ytt_api.fetch(video_id, languages=['en'])
            logger.info("✅ Found English transcript using simplified API")
        except NoTranscriptFound:
            logger.info("⚠️ No English transcript found, trying any available language...")
            try:
                fetched_transcript = ytt_api.fetch(video_id)
                logger.info(f"✅ Found transcript in language: {fetched_transcript.language}")
            except Exception as e:
                logger.error(f"❌ No transcripts available for this video: {str(e)}")
                raise CouldNotRetrieveTranscript(video_id)

        logger.info(f"✅ Transcript retrieved: {len(fetched_transcript)} entries")

        # Process transcript data
        logger.info("🔧 STEP 4: Processing transcript data...")
        full_text = ' '.join([snippet.text for snippet in fetched_transcript])
        logger.info(f"✅ Transcript text combined: {len(full_text)} characters")

        result = {
            "transcript": full_text,
            "language": fetched_transcript.language_code,
            "title": f"Video {video_id}",  # Title not available in simplified API
            "channel": "Unknown Channel",  # Channel info not available from transcript API
            "videoId": video_id,
            "compaction_id": compaction_id,
            "status_code": 200
        }

        logger.info(f"🎉 SUCCESS: Retrieved transcript for video {video_id} via Webshare proxy")
        logger.info(f"📊 Final result: {len(fetched_transcript)} entries, {len(full_text)} chars, language: {fetched_transcript.language_code}")
        return result
        
    except Exception as e:
        logger.error(f"❌ ERROR in get_video_transcript for video {video_id}: {str(e)}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        raise

def verify_api_key(authorization: Optional[str]) -> bool:
    """Verify the API key from Authorization header."""
    if not authorization:
        return False
    
    # Extract Bearer token
    if not authorization.startswith("Bearer "):
        return False
    
    token = authorization[7:]  # Remove "Bearer " prefix
    return token == API_KEY

@app.get("/health")
async def health_check():
    """Health check endpoint for Fly.io load balancer."""
    return {"status": "healthy", "service": "youtube-transcript-api"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "YouTube Transcript API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "transcript": "/get_transcript"
        }
    }

@app.get("/get_transcript")
async def get_transcript_get(
    request: Request,
    videoId: Optional[str] = Query(None),
    compaction_id: Optional[str] = Query(None),
    check: Optional[str] = Query(None)
):
    """GET endpoint for transcript retrieval."""
    return await handle_transcript_request(request, videoId, compaction_id, check)

@app.post("/get_transcript")
async def get_transcript_post(request: Request, body: Optional[TranscriptRequest] = None):
    """POST endpoint for transcript retrieval."""
    video_id = body.videoId if body else None
    compaction_id = body.compaction_id if body else None
    return await handle_transcript_request(request, video_id, compaction_id, None)

async def handle_transcript_request(request: Request, video_id: Optional[str], compaction_id: Optional[str], check: Optional[str]):
    """Handle transcript request logic."""
    logger.info("=== NEW REQUEST ===")
    logger.info(f"🌐 Request method: {request.method}")
    logger.info(f"🌐 Request URL: {request.url}")

    # Generate compaction_id if not provided
    if not compaction_id:
        compaction_id = str(uuid.uuid4())
        logger.info(f"🆔 Generated compaction_id: {compaction_id}")
    else:
        logger.info(f"🆔 Using provided compaction_id: {compaction_id}")

    # Check authorization
    authorization = request.headers.get("authorization")
    logger.info("🔐 STEP 1: Checking API key authorization...")

    if not verify_api_key(authorization):
        logger.warning("❌ Unauthorized request - invalid or missing API key")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "UNAUTHORIZED",
                "message": "Valid API key required in Authorization header",
                "compaction_id": compaction_id,
                "status_code": 401
            }
        )

    logger.info("✅ API key authorization successful")
    
    # Check if this is an IP check request
    if check == 'ip':
        logger.info("🔍 IP check request received - getting cloud function IP")
        try:
            response = requests.get('https://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                ip_data = response.json()
                cloud_ip = ip_data.get('origin', 'Unknown')
                logger.info(f"☁️ Cloud function IP: {cloud_ip}")
                return {"cloud_function_ip": cloud_ip, "compaction_id": compaction_id, "status_code": 200}
            else:
                raise HTTPException(status_code=500, detail={"error": "Failed to get IP", "compaction_id": compaction_id, "status_code": 500})
        except Exception as e:
            logger.error(f"❌ Error getting IP: {str(e)}")
            raise HTTPException(status_code=500, detail={"error": "Failed to get IP", "compaction_id": compaction_id, "status_code": 500})
    
    # Validate video ID
    if not video_id:
        logger.error("❌ Missing video ID in request")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "MISSING_VIDEO_ID",
                "message": "videoId parameter is required",
                "compaction_id": compaction_id,
                "status_code": 400
            }
        )
    
    logger.info(f"✅ Video ID extracted: {video_id}")
    
    # Get transcript using proxy
    logger.info("🔧 STEP 4: Retrieving proxy credentials from environment...")
    
    if not WEBSHARE_USERNAME or not WEBSHARE_PASSWORD:
        logger.error("❌ Missing proxy credentials in environment variables")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CONFIGURATION_ERROR",
                "message": "Proxy credentials not configured",
                "compaction_id": compaction_id,
                "status_code": 500
            }
        )
    
    logger.info(f"✅ Proxy credentials retrieved - username: {WEBSHARE_USERNAME}")
    
    try:
        logger.info("🎬 STEP 5: Calling get_video_transcript...")
        result = get_video_transcript(video_id, WEBSHARE_USERNAME, WEBSHARE_PASSWORD, compaction_id)

        logger.info(f"🎉 Successfully processed request for video {video_id}")
        return result

    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_VIDEO_ID",
                "message": str(e),
                "compaction_id": compaction_id,
                "status_code": 400
            }
        )

    except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript) as e:
        logger.info(f"No transcript available for video {video_id}: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "TRANSCRIPT_NOT_AVAILABLE",
                "message": "No transcript available for this video",
                "videoId": video_id,
                "compaction_id": compaction_id,
                "status_code": 404
            }
        )

    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "compaction_id": compaction_id,
                "status_code": 500
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
