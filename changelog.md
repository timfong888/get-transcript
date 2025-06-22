# Changelog

All notable changes to this project will be documented in this file.

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
