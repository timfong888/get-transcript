# Get Transcript - YouTube Transcript API

A FastAPI service deployed on Fly.io that extracts transcripts from YouTube videos using Webshare residential proxies. Provides a REST API with authentication, error handling, and proxy support that works reliably without 407 authentication errors.

## 🚀 **Live API Endpoint**
```
https://get-transcript.fly.dev/get_transcript
```

## 🔑 **Authentication Policy**

**Required**: All requests must include an API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY_HERE
```

⚠️ **Security Note**: Replace `YOUR_API_KEY_HERE` with your actual API key. Never commit real API keys to public repositories.

**Security**:
- API key is required for all transcript requests
- Health check endpoint (`/health`) is public
- CORS enabled for web browser requests
- No rate limiting currently implemented

## 📋 **How to Use**

### **Method 1: GET Request**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     "https://get-transcript.fly.dev/get_transcript?videoId=dQw4w9WgXcQ"
```

### **Method 2: POST Request**
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     -H "Content-Type: application/json" \
     -d '{"videoId": "dQw4w9WgXcQ"}' \
     "https://get-transcript.fly.dev/get_transcript"
```

### **JavaScript Example**
```javascript
const response = await fetch('https://get-transcript.fly.dev/get_transcript?videoId=dQw4w9WgXcQ', {
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY_HERE'
  }
});
const data = await response.json();
console.log(data.transcript);
```

### **Python Example**
```python
import requests

response = requests.get(
    'https://get-transcript.fly.dev/get_transcript',
    params={'videoId': 'dQw4w9WgXcQ'},
    headers={'Authorization': 'Bearer YOUR_API_KEY_HERE'}
)
data = response.json()
print(data['transcript'])
```

## 📊 **Response Format**

### **Success Response (200)**
```json
{
  "transcript": "♪ We're no strangers to love ♪ ♪ You know the rules and so do I ♪...",
  "language": "en",
  "title": "Video dQw4w9WgXcQ",
  "channel": "Unknown Channel",
  "videoId": "dQw4w9WgXcQ"
}
```

### **Error Responses**

**401 - Unauthorized**
```json
{
  "detail": {
    "error": "UNAUTHORIZED",
    "message": "Valid API key required in Authorization header"
  }
}
```

**400 - Bad Request**
```json
{
  "detail": {
    "error": "MISSING_VIDEO_ID",
    "message": "videoId parameter is required"
  }
}
```

**404 - Not Found**
```json
{
  "detail": {
    "error": "TRANSCRIPT_NOT_AVAILABLE",
    "message": "No transcript available for this video",
    "videoId": "someVideoId"
  }
}
```

## 🔍 **Additional Endpoints**

### **Health Check** (Public)
```bash
curl "https://get-transcript.fly.dev/health"
# Returns: {"status": "healthy", "service": "youtube-transcript-api"}
```

### **IP Check** (Authenticated)
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     "https://get-transcript.fly.dev/get_transcript?check=ip"
# Returns: {"cloud_function_ip": "xxx.xxx.xxx.xxx"}
```

## 🧪 **Test Video IDs**
- `dQw4w9WgXcQ` - Rick Astley "Never Gonna Give You Up" (has transcript)
- `jNQXAC9IVRw` - "Me at the zoo" (first YouTube video)
- `invalid123` - Invalid format (for error testing)

## 🚀 **Deployment Architecture**

### **Current Deployment: Fly.io**
- **Platform**: Fly.io (migrated from Firebase Functions)
- **Framework**: FastAPI (converted from Firebase Functions)
- **Region**: San Jose, California (US)
- **Machine**: shared-cpu-1x, 1GB RAM (smallest/cheapest)
- **Proxy**: Webshare residential proxies (working perfectly!)

### **Why Fly.io?**
✅ **Solved 407 Proxy Authentication Errors**: Google Cloud Functions blocked proxy auth, Fly.io allows it
✅ **Cost Effective**: Lower costs than Firebase Functions
✅ **Full Container Control**: No network restrictions
✅ **Fast Deployment**: ~10 minute migration time

### **Deployment Commands** (for reference)
```bash
# Install Fly.io CLI
brew install flyctl

# Login and deploy (already done)
flyctl auth login
flyctl deploy

# Set secrets (already configured)
flyctl secrets set WEBSHARE_USERNAME=xxx WEBSHARE_PASSWORD=xxx API_KEY=xxx
```

### **Branch Structure**
- `main` - Original Firebase Functions version
- `migrate-to-fly` - Current Fly.io deployment (✅ ACTIVE)

## ⚙️ **Technical Details**

### **Current Configuration**
- **Runtime**: Python 3.12 (Docker container)
- **Framework**: FastAPI with Uvicorn
- **Memory**: 1GB RAM
- **CPU**: Shared CPU (cost optimized)
- **Port**: 8080 (Fly.io standard)
- **Auto-scaling**: Min 0, Max 1 (cost optimized)

### **Proxy Configuration**
- **Provider**: Webshare residential proxies
- **Endpoint**: p.webshare.io:80 (rotating backbone)
- **Authentication**: Username/Password (stored in Fly.io secrets)
- **Features**: Automatic IP rotation, residential IPs, optimized for YouTube
- **Status**: ✅ Working perfectly (no more 407 errors!)

### **Dependencies**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
youtube-transcript-api==1.1.0
requests==2.31.0
pydantic==2.5.0
```

## 📊 **Monitoring & Logs**

### **Fly.io Logs**
```bash
# View live logs
flyctl logs

# View app status
flyctl status
```

### **Application Logging**
- **Info Level**: Successful requests, proxy IP rotation
- **Warning Level**: Authentication failures, invalid requests
- **Error Level**: Internal errors, proxy failures
- **Integration**: Can be configured to send to Google Cloud Logging if needed

## 🔒 **Security**

### **Implemented Security**
- ✅ API key authentication (Bearer token)
- ✅ Input validation (video ID format)
- ✅ Secure credential storage (Fly.io secrets)
- ✅ CORS enabled for web applications
- ✅ Error message sanitization
- ✅ Request logging for audit trails

### **Security Notes**
- ⚠️ **NEVER commit real API keys to repositories** - use environment variables or secure storage
- No rate limiting currently implemented
- Proxy credentials stored securely in Fly.io secrets
- All traffic over HTTPS
- Rotate API keys regularly for security

## 🐛 **Troubleshooting**

### **Common Issues**
1. **401 Unauthorized**: Check Authorization header format
2. **404 Not Found**: Video may not have transcripts or be private
3. **500 Internal Error**: Check Fly.io logs with `flyctl logs`

### **Quick Diagnostics**
```bash
# Test health endpoint
curl "https://get-transcript.fly.dev/health"

# Test with known working video
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     "https://get-transcript.fly.dev/get_transcript?videoId=dQw4w9WgXcQ"
```

## 📝 **Changelog**

### **Version 2.0.0 - June 2025**
- 🚀 **MAJOR**: Migrated from Firebase Functions to Fly.io
- ✅ **FIXED**: Resolved 407 Proxy Authentication errors
- 🔄 **CHANGED**: Framework from Firebase Functions to FastAPI
- 💰 **IMPROVED**: Lower costs than Firebase Functions
- 📦 **ADDED**: Docker containerization
- 🌐 **MAINTAINED**: Same API interface and authentication

### **Version 1.1.0 - January 2025**
- Migrated from Decodo to Webshare proxy
- Enhanced proxy configuration with automatic IP rotation

## 📄 **License**

MIT License - see LICENSE file for details.
