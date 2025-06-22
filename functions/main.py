import json
import logging
from typing import Dict, Any
from firebase_functions import https_fn
from firebase_functions.params import SecretParam
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
    if not validate_video_id(video_id):
        raise ValueError("Invalid video ID format")

    try:
        # Initialize YouTube Transcript API with Webshare proxy
        logger.info(f"Using Webshare proxy with username: {proxy_username}")
        logger.info(f"Proxy username length: {len(proxy_username)}")
        logger.info(f"Proxy password length: {len(proxy_password)}")

        ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password,
            )
        )

        # Fetch transcript using the proxied API instance
        transcript_list = ytt_api.list_transcripts(video_id)

        # Try to get English transcript first, then any available transcript
        try:
            transcript = transcript_list.find_transcript(['en'])
        except NoTranscriptFound:
            # Get the first available transcript
            available_transcripts = list(transcript_list)
            if not available_transcripts:
                raise CouldNotRetrieveTranscript(video_id)
            transcript = available_transcripts[0]

        # Fetch the actual transcript data
        transcript_data = transcript.fetch()

        # Combine all transcript text
        full_text = ' '.join([entry.text for entry in transcript_data])

        # Get basic video info from transcript metadata if available
        video_title = getattr(transcript, 'video_title', f"Video {video_id}")

        result = {
            "transcript": full_text,
            "language": transcript.language_code,
            "title": video_title,
            "channel": "Unknown Channel",  # Channel info not available from transcript API
            "videoId": video_id
        }

        logger.info(f"Successfully retrieved transcript for video {video_id}")
        return result

    except Exception as e:
        logger.error(f"Error retrieving transcript for video {video_id}: {str(e)}")
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
        # Authentication check
        auth_header = req.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("Unauthorized request - missing or invalid Authorization header")
            return https_fn.Response(
                json.dumps({
                    "error": "UNAUTHORIZED",
                    "message": "Missing or invalid Authorization header"
                }),
                status=401,
                headers={**headers, 'Content-Type': 'application/json'}
            )

        # Extract and validate API key
        request_api_key = auth_header.split(' ')[1]
        expected_api_key = api_key_secret.value

        if request_api_key != expected_api_key:
            logger.warning("Unauthorized request - invalid API key")
            return https_fn.Response(
                json.dumps({
                    "error": "UNAUTHORIZED",
                    "message": "Invalid API key"
                }),
                status=401,
                headers={**headers, 'Content-Type': 'application/json'}
            )
        
        # Extract video ID from request
        video_id = None
        if req.method == 'GET':
            video_id = req.args.get('videoId')
        elif req.method == 'POST':
            try:
                data = req.get_json()
                video_id = data.get('videoId') if data else None
            except Exception:
                return https_fn.Response(
                    json.dumps({
                        "error": "INVALID_REQUEST",
                        "message": "POST request must contain valid JSON data"
                    }),
                    status=400,
                    headers={**headers, 'Content-Type': 'application/json'}
                )
        
        if not video_id:
            return https_fn.Response(
                json.dumps({
                    "error": "MISSING_VIDEO_ID",
                    "message": "videoId parameter is required"
                }),
                status=400,
                headers={**headers, 'Content-Type': 'application/json'}
            )

        # Get transcript using proxy
        result = get_video_transcript(video_id, proxy_username_secret.value, proxy_password_secret.value)

        logger.info(f"Successfully processed request for video {video_id}")
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
