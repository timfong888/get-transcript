# Google Cloud Logging Setup for Fly.io

This guide explains how to configure your Fly.io application to send logs to Google Cloud Logging.

## Prerequisites

1. **Google Cloud Project**: You need an active Google Cloud project
2. **Google Cloud CLI**: Install and configure `gcloud` CLI
3. **Fly.io CLI**: Install and configure `flyctl`

## Step 1: Create Google Cloud Service Account

### 1.1 Create Service Account
```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create service account
gcloud iam service-accounts create fly-logging \
    --description="Service account for Fly.io app logging" \
    --display-name="Fly.io Logging Service Account" \
    --project=$PROJECT_ID
```

### 1.2 Grant Required Permissions
```bash
# Grant logging write permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:fly-logging@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"

# Grant monitoring metric writer (optional, for custom metrics)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:fly-logging@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/monitoring.metricWriter"
```

### 1.3 Create and Download Service Account Key
```bash
# Create key file
gcloud iam service-accounts keys create fly-logging-key.json \
    --iam-account=fly-logging@$PROJECT_ID.iam.gserviceaccount.com \
    --project=$PROJECT_ID

# Verify the key was created
ls -la fly-logging-key.json
```

## Step 2: Configure Fly.io Secrets

### 2.1 Set Google Cloud Credentials
```bash
# Set the service account key as a secret
flyctl secrets set GOOGLE_APPLICATION_CREDENTIALS_JSON="$(cat fly-logging-key.json)"

# Set the project ID
flyctl secrets set GOOGLE_CLOUD_PROJECT="$PROJECT_ID"

# Optional: Set log level
flyctl secrets set LOG_LEVEL="INFO"

# Optional: Set environment
flyctl secrets set ENVIRONMENT="production"
```

### 2.2 Verify Secrets
```bash
# List all secrets (values will be hidden)
flyctl secrets list
```

## Step 3: Update Application Configuration

The application is already configured to use Google Cloud Logging. The `logging_config.py` module will:

1. **Auto-detect environment**: Uses `ENVIRONMENT` variable to determine if running in production
2. **Authenticate automatically**: Uses `GOOGLE_APPLICATION_CREDENTIALS_JSON` for authentication
3. **Fallback gracefully**: Falls back to local logging if Google Cloud is unavailable
4. **Structure logs**: Provides structured logging with request correlation

### Environment Variables Used:
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`: Service account key (JSON string)
- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
- `ENVIRONMENT`: Set to "production" for Google Cloud Logging
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Step 4: Deploy and Test

### 4.1 Deploy Application
```bash
# Deploy with new logging configuration
flyctl deploy

# Monitor deployment
flyctl logs --follow
```

### 4.2 Test Logging
```bash
# Make a test request to generate logs
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://get-transcript.fly.dev/get_transcript?videoId=dQw4w9WgXcQ"

# Check Fly.io logs
flyctl logs

# Check Google Cloud Logs (see next section)
```

## Step 5: View Logs in Google Cloud

### 5.1 Using Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Logging > Logs Explorer**
3. Use this filter to find your app logs:
   ```
   resource.type="global"
   jsonPayload.service="get-transcript"
   ```

### 5.2 Using gcloud CLI
```bash
# View recent logs
gcloud logging read "jsonPayload.service=\"get-transcript\"" \
    --limit=50 \
    --format=json \
    --project=$PROJECT_ID

# View logs with specific request ID
gcloud logging read "jsonPayload.request_id=\"REQUEST_ID_HERE\"" \
    --format=json \
    --project=$PROJECT_ID

# View error logs only
gcloud logging read "jsonPayload.service=\"get-transcript\" AND severity>=ERROR" \
    --limit=20 \
    --format=json \
    --project=$PROJECT_ID
```

## Step 6: Log Structure

Your logs will have this structure in Google Cloud:

```json
{
  "timestamp": "2025-01-08T12:00:00.000Z",
  "severity": "INFO",
  "message": "✅ Successfully processed request for video dQw4w9WgXcQ",
  "logger": "get-transcript",
  "module": "app",
  "function": "handle_transcript_request",
  "line": 327,
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "video_id": "dQw4w9WgXcQ",
  "service": "get-transcript",
  "environment": "production",
  "success": true
}
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Verify service account key is valid
   gcloud auth activate-service-account --key-file=fly-logging-key.json
   gcloud auth list
   ```

2. **Permission Errors**
   ```bash
   # Check service account permissions
   gcloud projects get-iam-policy $PROJECT_ID \
       --flatten="bindings[].members" \
       --filter="bindings.members:fly-logging@$PROJECT_ID.iam.gserviceaccount.com"
   ```

3. **Logs Not Appearing**
   - Check Fly.io logs for error messages: `flyctl logs`
   - Verify environment variables: `flyctl secrets list`
   - Check Google Cloud Logging quotas and limits

### Debug Commands

```bash
# Check if Google Cloud Logging is working
flyctl ssh console
python3 -c "
from google.cloud import logging
client = logging.Client()
print('Google Cloud Logging client created successfully')
"

# Test log entry
flyctl ssh console
python3 -c "
from logging_config import setup_logging
logger = setup_logging('test')
logger.info('Test log entry from Fly.io')
"
```

## Security Notes

1. **Rotate Keys Regularly**: Service account keys should be rotated periodically
2. **Minimal Permissions**: Only grant necessary IAM roles
3. **Monitor Usage**: Set up billing alerts for logging costs
4. **Secure Storage**: Never commit service account keys to version control

## Cost Considerations

- Google Cloud Logging has free tier limits
- Monitor your logging volume in Google Cloud Console
- Consider log retention policies to manage costs
- Use log-based metrics for monitoring instead of storing all logs long-term

## Alternative: Vector Log Shipping

If you prefer using Vector (as mentioned in your issue), you can:

1. Set up Vector as a sidecar container in Fly.io
2. Configure Vector to read from your app's stdout/stderr
3. Use Vector's Google Cloud Logging sink
4. This approach provides more advanced log processing capabilities

Let me know if you'd like instructions for the Vector approach as well!
