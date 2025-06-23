# 🚨 Bug Report: 407 Proxy Authentication Required in Google Cloud Functions with Webshare Proxies

## 📋 **Issue Summary**
YouTube Transcript API with Webshare residential proxies works perfectly locally but fails in Google Cloud Functions (Firebase Functions) with `407 Proxy Authentication Required` error, despite correct credentials and configuration.

## 🔧 **Environment**
- **Platform**: Google Cloud Functions (Firebase Functions Python 3.12 2nd Gen)
- **YouTube Transcript API**: v1.1.0
- **Webshare Plan**: Residential proxies (30M available)
- **Authentication**: Username/password (no IP authorization)
- **Local Environment**: macOS - ✅ **Works perfectly**
- **Cloud Environment**: Google Cloud Functions - ❌ **Fails with 407 error**

## 🚨 **Error Details**

### **Cloud Function Logs:**
```
❌ Proxy test failed with exception: HTTPSConnectionPool(host='httpbin.org', port=443): Max retries exceeded with url: /ip (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 407 Proxy Authentication Required')))

❌ ERROR in get_video_transcript for video: Could not retrieve a transcript for the video! This is most likely caused by: YouTube is blocking requests from your IP.
```

### **Error occurs with both proxy configurations:**
1. **WebshareProxyConfig** (rotating endpoint): `pafkmsbh-rotate@p.webshare.io:80`
2. **GenericProxyConfig** (backbone): `pafkmsbh-1@p.webshare.io:10000`

## ✅ **What Works (Local Environment)**

### **Test 1: WebshareProxyConfig**
```python
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

proxy_config = WebshareProxyConfig(
    proxy_username="pafkmsbh",
    proxy_password="mb73d2wpp3rl"
)
ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
transcript_list = ytt_api.list_transcripts('jNQXAC9IVRw')
# ✅ SUCCESS: Works perfectly locally
```

### **Test 2: Direct Proxy Test**
```python
import requests
proxy_url = "http://pafkmsbh-rotate:mb73d2wpp3rl@p.webshare.io:80"
proxies = {'http': proxy_url, 'https': proxy_url}
response = requests.get('https://httpbin.org/ip', proxies=proxies)
# ✅ SUCCESS: Returns residential IP (e.g., 37.19.195.75)
```

### **Test 3: Backbone Proxy Test**
```python
import requests
proxy_url = "http://pafkmsbh-25:mb73d2wpp3rl@p.webshare.io:10024"
proxies = {'http': proxy_url, 'https': proxy_url}
response = requests.get('https://httpbin.org/ip', proxies=proxies)
# ✅ SUCCESS: Returns residential IP (e.g., 103.121.170.150)
```

## ❌ **What Fails (Google Cloud Functions)**

**Identical code fails in Google Cloud Functions with:**
- `407 Proxy Authentication Required`
- Both WebshareProxyConfig and GenericProxyConfig approaches fail
- Same credentials work perfectly locally

## 🔍 **Investigation Results**

### **Webshare Account Verification:**
- ✅ **Account Status**: Active with 30M residential proxies
- ✅ **Credentials**: Correct (`pafkmsbh` / `mb73d2wpp3rl`)
- ✅ **Proxy Type**: `"proxy_subtype": "residential"`
- ✅ **Authentication**: Username/password (no IP authorization restrictions)

### **Google Cloud Functions Network Behavior:**
- **Dynamic IP addresses**: Function IP changes between requests
  - Request 1: `34.96.45.150`
  - Request 2: `34.96.44.147`
- **IP Authorization**: Removed all IP restrictions to use pure username/password auth
- **Network Environment**: Something in GCF prevents proxy authentication

## 🔧 **Code Implementation**

### **Current Implementation (Fails in Cloud):**
```python
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

def get_video_transcript(video_id: str, proxy_username: str, proxy_password: str):
    # This works locally but fails in Google Cloud Functions
    proxy_config = WebshareProxyConfig(
        proxy_username=proxy_username,
        proxy_password=proxy_password,
    )
    ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
    transcript_list = ytt_api.list_transcripts(video_id)
    # 407 Proxy Authentication Required in cloud
```

## 🚨 **Webshare Support Feedback**

**From Webshare Support:**
> "The '407 Proxy Authentication Required' error typically occurs when proxy credentials are missing or incorrect. Since your proxy works locally but not in Firebase Functions, the issue might be related to how the credentials are being passed in the cloud environment."

**Key Points:**
- Using a proxy IP for more than 5 minutes can trigger this error
- Backbone connection recommended for avoiding rotation interruptions
- Issue appears specific to Google Cloud Functions environment

## 🎯 **Expected Behavior**
Webshare residential proxies should work in Google Cloud Functions with username/password authentication, just as they work locally.

## 🔄 **Actual Behavior**
Google Cloud Functions consistently returns `407 Proxy Authentication Required` despite correct credentials and configuration.

## 📱 **Reproduction Steps**
1. Set up Google Cloud Function with YouTube Transcript API
2. Configure Webshare residential proxies with WebshareProxyConfig
3. Deploy to Google Cloud Functions
4. Make request to function
5. Observe 407 error in logs

## 🔧 **Workaround Attempts**
- ❌ **IP Authorization**: Tried adding GCF IPs (limited to 1 IP, GCF uses dynamic IPs)
- ❌ **Backbone Proxies**: Tried GenericProxyConfig with backbone endpoints
- ❌ **Different Proxy Endpoints**: Tested multiple backbone proxy numbers
- ✅ **Local Testing**: All approaches work perfectly locally

## 💡 **Potential Root Cause**
Google Cloud Functions network environment appears to have restrictions or configurations that prevent proxy authentication from working properly, even with correct credentials.

## 🙏 **Request**
Investigation into compatibility between YouTube Transcript API proxy configurations and Google Cloud Functions network environment, or guidance on proper proxy configuration for cloud environments.

---

**Environment Details:**
- Google Cloud Functions Python 3.12 (2nd Gen)
- Firebase Functions framework
- Webshare residential proxy plan
- YouTube Transcript API v1.1.0
