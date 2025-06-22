# Firebase Secret Manager - Credential Verification Guide

## Overview
This guide shows how to retrieve and verify the Webshare proxy credentials stored in Firebase Secret Manager.

## Current Credentials Stored

### Webshare Proxy Configuration
- **Domain**: p.webshare.io
- **Port**: 80
- **Protocol**: HTTP (handles both HTTP and HTTPS traffic)
- **Username**: pafkmsbh (stored without -rotate suffix)
- **Password**: mb73d2wpp3rl

## CLI Commands to Retrieve Credentials

### 1. Retrieve Proxy Username
```bash
firebase functions:secrets:access PROXY_USERNAME
```

### 2. Retrieve Proxy Password
```bash
firebase functions:secrets:access PROXY_PASSWORD
```

### 3. Retrieve API Key (if needed)
```bash
firebase functions:secrets:access API_KEY
```

## Verification Commands

### List All Secrets
```bash
firebase functions:secrets:list
```

### Get Secret Metadata
```bash
# Get username secret info
firebase functions:secrets:describe PROXY_USERNAME

# Get password secret info
firebase functions:secrets:describe PROXY_PASSWORD
```

### Verify Secret Versions
```bash
# List all versions of username secret
firebase functions:secrets:versions PROXY_USERNAME

# List all versions of password secret
firebase functions:secrets:versions PROXY_PASSWORD
```

## Expected Output

When you run `firebase functions:secrets:access PROXY_USERNAME`, you should see:
```
pafkmsbh
```

When you run `firebase functions:secrets:access PROXY_PASSWORD`, you should see:
```
mb73d2wpp3rl
```

## How the Credentials Are Used

The `WebshareProxyConfig` class automatically:
1. Takes the username `pafkmsbh`
2. Adds the `-rotate` suffix to become `pafkmsbh-rotate`
3. Constructs the proxy URL: `http://pafkmsbh-rotate:mb73d2wpp3rl@p.webshare.io:80/`

## Testing the Configuration

### Local Test
Update `test_local.py` with the credentials:
```python
proxy_username = "pafkmsbh"
proxy_password = "mb73d2wpp3rl"
```

Then run:
```bash
python test_local.py
```

### Firebase Function Test
After deploying, test the function:
```bash
curl -X GET "https://us-central1-sophia-db784.cloudfunctions.net/get_transcript?videoId=dQw4w9WgXcQ" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Deployment

After updating secrets, deploy the function:
```bash
firebase deploy --only functions
```

## Security Notes

1. **Secret Versions**: Firebase automatically creates new versions when secrets are updated
2. **Access Control**: Only authorized users can access these secrets
3. **Audit Trail**: All secret access is logged in Google Cloud
4. **Environment Isolation**: Secrets are isolated per Firebase project

## Troubleshooting

### If credentials don't work:
1. Verify the credentials are correct using the CLI commands above
2. Check that the function is using the latest secret version (deploy after updating)
3. Verify your Webshare account is active and has sufficient quota
4. Check Firebase Function logs for detailed error messages

### Common Issues:
- **Old secret version**: Deploy the function after updating secrets
- **Wrong username format**: Ensure username is stored without `-rotate` suffix
- **Quota exceeded**: Check your Webshare account usage
- **Network issues**: Verify proxy connectivity

## Additional Commands

### Update Secrets (if needed)
```bash
# Update username
echo "new_username" | firebase functions:secrets:set PROXY_USERNAME

# Update password  
echo "new_password" | firebase functions:secrets:set PROXY_PASSWORD
```

### Delete Secret Versions (if needed)
```bash
# Delete specific version
firebase functions:secrets:destroy PROXY_USERNAME --version-id=VERSION_NUMBER
```

## HTTPS Clarification

**Question**: Will the lack of HTTPS cause problems?
**Answer**: No. This is normal for proxy configurations:

- **Proxy Connection**: HTTP (your app ↔ Webshare proxy)
- **End-to-End**: HTTPS (Webshare proxy ↔ YouTube servers)
- **Security**: End-to-end encryption is maintained for HTTPS requests

The proxy handles both HTTP and HTTPS traffic through the HTTP connection, which is the standard approach for residential proxy services.
