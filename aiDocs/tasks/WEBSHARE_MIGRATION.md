# Migration from Decodo to Webshare Proxy

## Overview

This document outlines the changes made to migrate the YouTube Transcript API from using Decodo proxy to Webshare proxy, following the documentation in `aiDocs/mcp_servers.md` and the YouTube Transcript API documentation.

## Changes Made

### 1. Code Changes

#### `functions/main.py`
- **Import Change**: Replaced `GenericProxyConfig` with `WebshareProxyConfig`
- **Proxy Configuration**: Simplified proxy setup using Webshare's dedicated configuration class
- **Removed**: Manual HTTP/HTTPS URL construction for Decodo
- **Added**: Direct username/password configuration for Webshare

**Before:**
```python
from youtube_transcript_api.proxies import GenericProxyConfig

http_proxy_url = f"http://{proxy_username}:{proxy_password}@gate.decodo.com:10001"
https_proxy_url = f"https://{proxy_username}:{proxy_password}@gate.decodo.com:10001"

ytt_api = YouTubeTranscriptApi(
    proxy_config=GenericProxyConfig(
        http_url=http_proxy_url,
        https_url=https_proxy_url,
    )
)
```

**After:**
```python
from youtube_transcript_api.proxies import WebshareProxyConfig

ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username=proxy_username,
        proxy_password=proxy_password,
    )
)
```

#### `test_local.py`
- Updated to use `WebshareProxyConfig` instead of `GenericProxyConfig`
- Changed placeholder credentials to indicate Webshare credentials needed
- Simplified proxy configuration logic

### 2. Documentation Updates

#### `README.md`
- Updated proxy provider information from Decodo to Webshare
- Changed credential setup instructions
- Updated proxy configuration section with Webshare details

#### `DEPLOYMENT_CHECKLIST.md`
- Updated secret management section to reference Webshare credentials

#### `setup-secrets.sh.template`
- Updated comments to reference Webshare credentials
- Added link to Webshare dashboard for credential retrieval

### 3. Benefits of Webshare Migration

1. **Optimized for YouTube**: Webshare's `WebshareProxyConfig` is specifically designed for YouTube API access
2. **Automatic IP Rotation**: Built-in rotating residential proxies
3. **Simplified Configuration**: No need to manually construct proxy URLs
4. **Better Reliability**: Webshare is recommended by the YouTube Transcript API documentation
5. **Automatic Retry Logic**: Built-in retry mechanism when requests are blocked (default: 10 retries)

## Required Actions

### For Deployment
1. **Get Webshare Credentials**: 
   - Sign up at https://www.webshare.io/
   - Purchase a "Residential" proxy package (NOT "Proxy Server" or "Static Residential")
   - Get credentials from https://dashboard.webshare.io/proxy/settings

2. **Update Firebase Secrets**:
   ```bash
   echo "YOUR_WEBSHARE_USERNAME" | firebase functions:secrets:set PROXY_USERNAME
   echo "YOUR_WEBSHARE_PASSWORD" | firebase functions:secrets:set PROXY_PASSWORD
   ```

3. **Deploy Updated Function**:
   ```bash
   firebase deploy --only functions
   ```

### For Local Testing
1. Update `test_local.py` with your actual Webshare credentials
2. Run the test script to verify functionality

## Technical Details

### Webshare Proxy Configuration
- **Default Domain**: p.webshare.io
- **Default Port**: 80
- **Protocol**: HTTP with automatic HTTPS support
- **Authentication**: Username/Password with automatic "-rotate" suffix for IP rotation
- **Retry Logic**: 10 retries when blocked (configurable)

### Proxy URL Format
Webshare automatically constructs URLs in the format:
```
http://username-rotate:password@p.webshare.io:80/
```

The "-rotate" suffix enables automatic IP rotation for better reliability.

## Testing

After migration, test the function with:
1. Local testing using `test_local.py`
2. Firebase Functions testing using the deployed endpoint
3. Monitor logs for any proxy-related errors

## Rollback Plan

If issues occur, the previous Decodo configuration can be restored by:
1. Reverting the import back to `GenericProxyConfig`
2. Restoring the manual proxy URL construction
3. Using the original Decodo credentials

However, Webshare is the recommended approach per the YouTube Transcript API documentation.
