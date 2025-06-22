# Get Transcript - YouTube Transcript Extraction Service

A Firebase Functions service that extracts transcripts from YouTube videos using rotating residential proxies. This service provides a REST API for retrieving video transcripts with proper authentication, error handling, and monitoring.

## Features

- 🎥 Extract transcripts from YouTube videos
- 🔒 Secure authentication with API keys
- 🌐 Rotating residential proxy support (Decodo)
- 📊 Comprehensive error handling and logging
- 🚀 Serverless deployment on Firebase Functions
- 🔐 Secure credential management with Google Secret Manager
- ✅ CORS support for web applications

## API Documentation

### Endpoint
```
GET/POST https://your-region-your-project.cloudfunctions.net/get_transcript
```

### Authentication
All requests require an API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

### Request Formats

#### GET Request
```bash
curl -X GET "https://your-function-url/get_transcript?videoId=dQw4w9WgXcQ" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### POST Request
```bash
curl -X POST "https://your-function-url/get_transcript" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"videoId": "dQw4w9WgXcQ"}'
```

### Response Format

#### Success Response (200)
```json
{
  "transcript": "Never gonna give you up, never gonna let you down...",
  "language": "en",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "RickAstleyVEVO",
  "videoId": "dQw4w9WgXcQ"
}
```

#### Error Responses

**400 - Bad Request**
```json
{
  "error": "INVALID_VIDEO_ID",
  "message": "Invalid video ID format"
}
```

**401 - Unauthorized**
```json
{
  "error": "UNAUTHORIZED",
  "message": "Invalid API key"
}
```

**404 - Not Found**
```json
{
  "error": "TRANSCRIPT_NOT_AVAILABLE",
  "message": "No transcript available for this video",
  "videoId": "example123"
}
```

**429 - Rate Limited**
```json
{
  "error": "RATE_LIMITED",
  "message": "Too many requests, please try again later",
  "videoId": "example123"
}
```

**500 - Internal Server Error**
```json
{
  "error": "INTERNAL_ERROR",
  "message": "An internal error occurred"
}
```

## Deployment Guide

### Prerequisites

1. **Firebase CLI**: Install the Firebase CLI
   ```bash
   npm install -g firebase-tools
   ```

2. **Google Cloud Project**: Create a new Google Cloud project or use existing one

3. **Firebase Project**: Initialize Firebase in your project
   ```bash
   firebase login
   firebase init functions
   ```

### Step-by-Step Deployment

1. **Clone and Setup**
   ```bash
   git clone https://github.com/your-username/get-transcript.git
   cd get-transcript
   ```

2. **Configure Firebase Project**
   ```bash
   # Update .firebaserc with your project ID
   firebase use your-project-id
   ```

3. **Set Up Secrets**
   ```bash
   # Run the setup script to configure secrets
   ./setup-secrets.sh
   ```
   
   This will set up:
   - `PROXY_USERNAME`: Webshare proxy username
   - `PROXY_PASSWORD`: Webshare proxy password
   - `API_KEY`: Your custom API key for authentication

4. **Deploy the Function**
   ```bash
   firebase deploy --only functions
   ```

5. **Test the Deployment**
   ```bash
   # Update test_function.py with your function URL and API key
   python3 test_function.py
   ```

### Manual Secret Setup

If you prefer to set up secrets manually:

```bash
# Set proxy credentials (replace with your actual Webshare credentials)
echo "YOUR_WEBSHARE_USERNAME" | firebase functions:secrets:set PROXY_USERNAME
echo "YOUR_WEBSHARE_PASSWORD" | firebase functions:secrets:set PROXY_PASSWORD

# Set your API key
echo "your-secure-api-key" | firebase functions:secrets:set API_KEY
```

## Configuration

### Environment Variables

The function uses the following configuration:
- **Memory**: 512MB
- **Timeout**: 60 seconds
- **Runtime**: Python 3.11

### Proxy Configuration

The service uses Webshare rotating residential proxies:
- **Provider**: Webshare
- **Endpoint**: p.webshare.io:80 (automatically configured)
- **Authentication**: Username/Password (stored in Secret Manager)
- **Features**: Automatic IP rotation, optimized for YouTube

## Testing

### Local Testing

1. **Install Dependencies**
   ```bash
   cd functions
   pip install -r requirements.txt
   ```

2. **Run Tests**
   ```bash
   # Update test_function.py with your function URL and API key
   python3 ../test_function.py
   ```

### Test Video IDs

Use these video IDs for testing:
- `dQw4w9WgXcQ` - Rick Astley (has transcript)
- `jNQXAC9IVRw` - Me at the zoo (first YouTube video)
- `invalid123` - Invalid format (for error testing)

## Monitoring and Logging

### Google Cloud Logging

All requests and errors are logged to Google Cloud Logging:
- **Info Level**: Successful requests
- **Warning Level**: Authentication failures, invalid requests
- **Error Level**: Internal errors, proxy failures

### Monitoring Setup

Set up alerts in Google Cloud Monitoring for:
- Error rate > 5% over 5 minutes
- Request rate > 100/minute  
- Function execution time > 30 seconds
- Memory usage > 80%

## Security

### Best Practices Implemented

- ✅ API key authentication
- ✅ Input validation
- ✅ Secure credential storage (Secret Manager)
- ✅ CORS configuration
- ✅ Error message sanitization
- ✅ Request logging for audit trails

### Security Considerations

- API keys should be rotated regularly
- Monitor for unusual request patterns
- Set up rate limiting if needed
- Review access logs periodically

## Troubleshooting

### Common Issues

1. **"Unauthorized" errors**
   - Check API key is correctly set in Secret Manager
   - Verify Authorization header format

2. **"Transcript not available" errors**
   - Video may not have transcripts enabled
   - Video may be private or deleted
   - Try with known working video IDs

3. **Proxy connection errors**
   - Verify proxy credentials in Secret Manager
   - Check Decodo service status
   - Review function logs for detailed error messages

4. **Deployment failures**
   - Ensure Firebase project is properly configured
   - Check that all required APIs are enabled
   - Verify Secret Manager permissions

### Getting Help

1. Check function logs: `firebase functions:log`
2. Review Google Cloud Logging for detailed error messages
3. Test with the provided test script
4. Verify all secrets are properly configured

## Changelog

### Version 1.1.0 - 2025-01-22
- **BREAKING**: Migrated from Decodo to Webshare proxy for improved reliability
- Enhanced proxy configuration with automatic IP rotation
- Comprehensive documentation updates and migration guides
- Successfully tested with Webshare proxy integration

For detailed changelog, see [changelog.md](./changelog.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
