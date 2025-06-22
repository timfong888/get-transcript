# Deployment Checklist for Get-Transcript Function

## Pre-Deployment Setup

### 1. Firebase Project Setup
- [ ] Create or select Google Cloud Project
- [ ] Enable required APIs:
  - [ ] Cloud Functions API
  - [ ] Cloud Build API
  - [ ] Secret Manager API
  - [ ] Cloud Logging API
  - [ ] Cloud Monitoring API
- [ ] Install Firebase CLI: `npm install -g firebase-tools`
- [ ] Login to Firebase: `firebase login`
- [ ] Initialize project: `firebase init functions`

### 2. Project Configuration
- [ ] Update `.firebaserc` with your actual project ID
- [ ] Verify `firebase.json` configuration
- [ ] Review `functions/requirements.txt` dependencies

### 3. Secrets Management
- [ ] Run `./setup-secrets.sh` or manually set secrets:
  - [ ] `PROXY_USERNAME`: Your Webshare proxy username
  - [ ] `PROXY_PASSWORD`: Your Webshare proxy password
  - [ ] `API_KEY`: Generate a secure API key
- [ ] Verify secrets are set: `firebase functions:secrets:access PROXY_USERNAME`

## Deployment Steps

### 4. Deploy Function
- [ ] Deploy: `firebase deploy --only functions`
- [ ] Note the function URL from deployment output
- [ ] Verify function is accessible in Firebase Console

### 5. Initial Testing
- [ ] Update `test_function.py` with:
  - [ ] Actual function URL
  - [ ] Your API key
- [ ] Run basic tests: `python3 test_function.py`
- [ ] Test with known working video ID: `dQw4w9WgXcQ`

## Post-Deployment Configuration

### 6. Monitoring Setup
- [ ] Set up Google Cloud Monitoring alerts:
  - [ ] Error rate > 5% over 5 minutes
  - [ ] Request rate > 100/minute
  - [ ] Function execution time > 30 seconds
  - [ ] Memory usage > 80%
- [ ] Configure notification channels (email, Slack, etc.)

### 7. Security Review
- [ ] Verify API key is secure and not exposed
- [ ] Test authentication with invalid API key
- [ ] Review CORS settings if needed for web apps
- [ ] Check function permissions and IAM roles

### 8. Performance Testing
- [ ] Test with multiple video types:
  - [ ] Short videos
  - [ ] Long videos
  - [ ] Videos with/without transcripts
  - [ ] Private/deleted videos
- [ ] Monitor function execution time and memory usage
- [ ] Test proxy connectivity and failover

## Production Readiness

### 9. Documentation
- [ ] Update README.md with actual function URL
- [ ] Document API key distribution process
- [ ] Create user guide for API consumers
- [ ] Document troubleshooting procedures

### 10. Backup and Recovery
- [ ] Document secret recovery procedures
- [ ] Set up function backup/versioning strategy
- [ ] Document rollback procedures
- [ ] Test disaster recovery scenarios

### 11. Operational Procedures
- [ ] Set up log monitoring and alerting
- [ ] Define incident response procedures
- [ ] Schedule regular security reviews
- [ ] Plan for API key rotation

## Validation Tests

### 12. End-to-End Testing
- [ ] Test GET requests with valid video IDs
- [ ] Test POST requests with JSON payload
- [ ] Test error scenarios:
  - [ ] Invalid video ID format
  - [ ] Missing video ID
  - [ ] Invalid API key
  - [ ] Video without transcript
  - [ ] Rate limiting (if applicable)
- [ ] Test CORS preflight requests
- [ ] Verify all error responses have proper format

### 13. Integration Testing
- [ ] Test integration with Pipedream (if applicable)
- [ ] Test integration with n8n (if applicable)
- [ ] Test with actual data pipeline workflows
- [ ] Verify webhook compatibility

## Go-Live Checklist

### 14. Final Verification
- [ ] All tests passing
- [ ] Monitoring alerts configured
- [ ] Documentation complete
- [ ] API keys distributed securely
- [ ] Support procedures documented

### 15. Launch
- [ ] Announce API availability
- [ ] Provide API documentation to users
- [ ] Monitor initial usage patterns
- [ ] Be ready for support requests

## Post-Launch

### 16. Ongoing Maintenance
- [ ] Monitor function performance daily
- [ ] Review logs for errors weekly
- [ ] Update dependencies monthly
- [ ] Rotate API keys quarterly
- [ ] Review and update documentation as needed

---

## Quick Commands Reference

```bash
# Deploy function
firebase deploy --only functions

# View logs
firebase functions:log

# Set secret
echo "value" | firebase functions:secrets:set SECRET_NAME

# Access secret (for testing)
firebase functions:secrets:access SECRET_NAME

# Test function
python3 test_function.py

# Check function status
firebase functions:list
```

## Emergency Contacts

- Firebase Support: [Firebase Console](https://console.firebase.google.com)
- Decodo Proxy Support: [Contact information]
- Project Owner: [Your contact information]
