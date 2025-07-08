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

### **Deployment Setup & Commands**

#### **Initial Fly.io Setup**
```bash
# 1. Install Fly.io CLI
brew install flyctl

# 2. Login to Fly.io (opens browser for authentication)
flyctl auth login

# 3. Initialize app (creates fly.toml)
flyctl launch --name get-transcript --region sjc

# 4. Set required secrets (replace with your actual values)
flyctl secrets set API_KEY=your_secure_api_key_here
flyctl secrets set WEBSHARE_USERNAME=your_webshare_username
flyctl secrets set WEBSHARE_PASSWORD=your_webshare_password

# 5. Deploy the application
flyctl deploy
```

#### **Ongoing Deployment Commands**
```bash
# Deploy updates
flyctl deploy

# View live logs
flyctl logs

# Check app status
flyctl status

# Update secrets (when needed)
flyctl secrets set API_KEY=new_api_key_here

# Scale app (cost optimization)
flyctl scale count 1 --region sjc
```

#### **🔐 Secrets Management**

**Setting Secrets:**
```bash
# Set individual secrets
flyctl secrets set API_KEY=your_secure_api_key_here
flyctl secrets set WEBSHARE_USERNAME=your_username
flyctl secrets set WEBSHARE_PASSWORD=your_password

# Set multiple secrets at once
flyctl secrets set API_KEY=key WEBSHARE_USERNAME=user WEBSHARE_PASSWORD=pass
```

**Managing Secrets:**
```bash
# List all secrets (names only, values are encrypted)
flyctl secrets list

# Remove a secret
flyctl secrets unset SECRET_NAME

# Import secrets from file (format: NAME=VALUE per line)
flyctl secrets import < secrets.txt
```

**⚠️ Important Notes:**
- **Secret values cannot be retrieved** once set (security feature)
- **Deployment required**: Run `flyctl deploy` after setting secrets to apply changes
- **Case sensitive**: Secret names are stored exactly as provided
- **Environment variables**: Secrets are available as ENV vars in the app
- **Automatic restart**: Setting secrets triggers machine restart

**Backbone Connection Update:**
For Webshare backbone connections, the username does NOT need the `-rotate` suffix:
```bash
# Backbone connection (no -rotate suffix)
flyctl secrets set WEBSHARE_USERNAME=pafkmsbh

# After updating secrets, redeploy to apply changes
flyctl deploy
```

#### **Development Workflow**
```bash
# 1. Make code changes
# 2. Test locally (optional)
python app.py

# 3. Deploy to Fly.io
flyctl deploy

# 4. Monitor deployment
flyctl logs --follow
```

### **Required Files for Fly.io Deployment**
```
├── fly.toml              # Fly.io configuration
├── Dockerfile            # Container build instructions
├── app.py               # FastAPI application
├── requirements.txt     # Python dependencies
└── README.md           # This documentation
```

#### **Key Configuration Files**

**fly.toml** - Fly.io app configuration:
```toml
app = "get-transcript"
primary_region = "sjc"

[build]

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  memory = "1gb"
  cpu_kind = "shared"
  cpus = 1
```

**Dockerfile** - Container configuration:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
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
4. **Deployment Fails**: Verify secrets are set correctly
5. **App Won't Start**: Check Dockerfile and requirements.txt

### **Fly.io Specific Troubleshooting**
```bash
# Check app status
flyctl status

# View live logs
flyctl logs --follow

# Check secrets (lists names only, not values)
flyctl secrets list

# Restart app
flyctl machine restart

# Check machine status
flyctl machine list

# SSH into running container (for debugging)
flyctl ssh console
```

### **Quick Diagnostics**
```bash
# Test health endpoint (public)
curl "https://get-transcript.fly.dev/health"

# Test with your API key (authenticated)
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     "https://get-transcript.fly.dev/get_transcript?videoId=dQw4w9WgXcQ"

# Check if secrets are properly set
flyctl secrets list
# Should show: API_KEY, WEBSHARE_USERNAME, WEBSHARE_PASSWORD
```

### **Common Deployment Issues**
1. **Secret Not Set**: `flyctl secrets set KEY=value` then `flyctl deploy`
2. **Secret Not Applied**: Must run `flyctl deploy` after setting secrets
3. **Wrong Username Format**:
   - Backbone connection: `pafkmsbh` (no suffix)
   - Rotating proxy: `pafkmsbh-rotate` (with suffix)
4. **Wrong Region**: App deployed in `sjc` (San Jose)
5. **Port Issues**: App runs on port 8080 internally
6. **Memory Limits**: 1GB RAM allocated (increase if needed)
7. **Auto-scaling**: Min 0 machines (cost optimized)

### **Secrets Troubleshooting**
```bash
# Check if secrets exist
flyctl secrets list

# Verify secret names (case sensitive)
# Should show: API_KEY, WEBSHARE_USERNAME, WEBSHARE_PASSWORD

# If secrets are set but not working:
flyctl deploy  # Redeploy to apply secret changes

# Check if app is using secrets correctly
flyctl logs --follow  # Look for authentication errors
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
