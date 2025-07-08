import json
import logging
import os
import requests
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

class TranscriptResponse(BaseModel):
    transcript: str
    language: str
    title: str
    channel: str
    videoId: str

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

def get_video_transcript(video_id: str, proxy_username: str, proxy_password: str) -> Dict[str, Any]:
    """Retrieve transcript for a YouTube video."""
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
    check: Optional[str] = Query(None)
):
    """GET endpoint for transcript retrieval."""
    return await handle_transcript_request(request, videoId, check)

@app.post("/get_transcript")
async def get_transcript_post(request: Request, body: Optional[TranscriptRequest] = None):
    """POST endpoint for transcript retrieval."""
    video_id = body.videoId if body else None
    return await handle_transcript_request(request, video_id, None)

async def handle_transcript_request(request: Request, video_id: Optional[str], check: Optional[str]):
    """Handle transcript request logic."""
    logger.info("=== NEW REQUEST ===")
    logger.info(f"🌐 Request method: {request.method}")
    logger.info(f"🌐 Request URL: {request.url}")
    
    # Check authorization
    authorization = request.headers.get("authorization")
    logger.info("🔐 STEP 1: Checking API key authorization...")
    
    if not verify_api_key(authorization):
        logger.warning("❌ Unauthorized request - invalid or missing API key")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "UNAUTHORIZED",
                "message": "Valid API key required in Authorization header"
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
                return {"cloud_function_ip": cloud_ip}
            else:
                raise HTTPException(status_code=500, detail={"error": "Failed to get IP"})
        except Exception as e:
            logger.error(f"❌ Error getting IP: {str(e)}")
            raise HTTPException(status_code=500, detail={"error": "Failed to get IP"})
    
    # Validate video ID
    if not video_id:
        logger.error("❌ Missing video ID in request")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "MISSING_VIDEO_ID",
                "message": "videoId parameter is required"
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
                "message": "Proxy credentials not configured"
            }
        )
    
    logger.info(f"✅ Proxy credentials retrieved - username: {WEBSHARE_USERNAME}")
    
    try:
        logger.info("🎬 STEP 5: Calling get_video_transcript...")
        result = get_video_transcript(video_id, WEBSHARE_USERNAME, WEBSHARE_PASSWORD)
        
        logger.info(f"🎉 Successfully processed request for video {video_id}")
        return result
        
    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_VIDEO_ID",
                "message": str(e)
            }
        )
    
    except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript) as e:
        logger.info(f"No transcript available for video {video_id}: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "TRANSCRIPT_NOT_AVAILABLE",
                "message": "No transcript available for this video",
                "videoId": video_id
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
