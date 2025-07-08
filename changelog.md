# Changelog

All notable changes to this project will be documented in this file.

## Version 2.0.0 - 2025-07-08

### Major Platform Migration
- **BREAKING**: Migrated from Firebase Functions to Fly.io platform
- **BRANCH**: Migration performed in `migrate-to-fly` branch for safe deployment
- **FRAMEWORK**: Converted from Firebase Functions to FastAPI with Uvicorn
- **DEPLOYMENT**: Now running on Fly.io with Docker containerization

### Changes
- ✅ **FIXED**: Resolved 407 Proxy Authentication errors that occurred with Google Cloud Functions
- 🚀 **IMPROVED**: Better proxy support and network freedom on Fly.io
- 💰 **COST**: Lower operational costs compared to Firebase Functions
- 🔄 **MAINTAINED**: Same API interface, endpoints, and authentication system
- 📦 **ADDED**: Docker containerization for consistent deployment
- 🌐 **REGION**: Deployed in San Jose, California (US) region
- ⚙️ **MACHINE**: Running on shared-cpu-1x with 1GB RAM (cost optimized)

### Technical Details
- **Runtime**: Python 3.12 in Docker container
- **Framework**: FastAPI with Uvicorn server
- **Port**: 8080 (Fly.io standard)
- **Auto-scaling**: Min 0, Max 1 instances
- **Proxy**: Webshare residential proxies (working perfectly on Fly.io)
- **Secrets**: Migrated to Fly.io secrets management
- **Logging**: Integrated with Fly.io logging system

### Migration Benefits
- ✅ **Proxy Authentication**: No more 407 errors with Webshare proxies
- ✅ **Network Freedom**: Full container control without Google Cloud restrictions
- ✅ **Fast Deployment**: ~10 minute migration time
- ✅ **Cost Effective**: Lower costs than Firebase Functions
- ✅ **Same API**: No changes required for existing integrations

### Deployment Commands
```bash
# Install Fly.io CLI
brew install flyctl

# Deploy application
flyctl deploy

# Set secrets
flyctl secrets set WEBSHARE_USERNAME=xxx WEBSHARE_PASSWORD=xxx API_KEY=xxx
```

## Version 1.1.0 - 2025-01-22

### Changes
- **BREAKING**: Migrated from Decodo proxy to Webshare proxy for improved reliability and YouTube optimization
- Updated `functions/main.py` to use `WebshareProxyConfig` instead of `GenericProxyConfig`
- Simplified proxy configuration by removing manual HTTP/HTTPS URL construction
- Updated `test_local.py` to use Webshare proxy configuration
- Added automatic IP rotation with Webshare's `-rotate` suffix functionality
- Improved error handling and retry logic (10 retries when blocked by default)
- Updated all documentation to reflect Webshare proxy usage:
  - `README.md`: Updated proxy configuration section and setup instructions
  - `DEPLOYMENT_CHECKLIST.md`: Updated secret management for Webshare credentials
  - `setup-secrets.sh.template`: Updated to reference Webshare credentials
- Created comprehensive migration documentation:
  - `WEBSHARE_MIGRATION.md`: Detailed migration guide and technical details
  - `CREDENTIAL_VERIFICATION.md`: CLI commands for credential verification and troubleshooting
- Cleaned up unused imports in Python files
- Successfully tested local configuration with Webshare proxy
- Secured Webshare credentials in Firebase Secret Manager:
  - Username: `pafkmsbh` (without -rotate suffix)
  - Password: `mb73d2wpp3rl`
  - Domain: `p.webshare.io:80`

### Technical Improvements
- Enhanced proxy reliability with Webshare's residential proxy network
- Automatic IP rotation for better YouTube API access
- Simplified configuration reduces potential for proxy URL construction errors
- Better integration with YouTube Transcript API's recommended proxy solution

### Migration Notes
- Webshare proxy uses HTTP connection (port 80) but maintains HTTPS security for end-to-end encryption
- No changes required to API endpoints or authentication
- Existing API keys and function signatures remain unchanged
- Local testing confirmed successful transcript retrieval with new proxy configuration

## Version 1.0.0 - 2025-01-21

### Initial Release
- Firebase Cloud Function for YouTube transcript retrieval
- Decodo proxy integration for bypassing YouTube restrictions
- API key authentication system
- Support for multiple video formats and languages
- Comprehensive error handling for various YouTube API exceptions
- Local testing capabilities
- Firebase Secret Manager integration for secure credential storage
