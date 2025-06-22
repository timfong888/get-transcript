# Get Transcript PRD

## Context
You are an experienced Firebase functions developer with expertise in python.  You write concise, clearly understood code as an agent that has no human intervention.

## Overview
This function is responsible for retrieving transcripts from YouTube videos.  The function will receive the YouTube video ID and return the transcript.  The function will be called via Rest API from a data pipeline that could be called from Pipedream, n8n, or another function.  So it should operate as a stand-alone service but only allow authorized users to access it.

It should return the transcript as a JSON object with the following structure:
```json
{
  "transcript": "text of transcript",
  "language": "language code",
  "title": "title of video",
  "channel": "channel name",
  "videoId": "video id"
}
```
## Environment
The function will be deployed on Firebase Functions as a serverless function.

It will depend upon a python package called `youtube-transcript-api` that can be installed via pip.  The function will need to install this package at runtime.

## Public Github Repository
This repository will be the same name as the folder: `get-transcript`

The repository will be public, so all private keys and secrets must be secured (such as a functions secret or use the Google Secrets Manager)

## Rotating Residential Proxies
The function needs to use the rotating residential proxy configuration.  The API has a section with a sample code for proxies.

The application used to use Decodo, but it has not been successful.  

June 22, 2025, I set up a subscription to Webshare.

It has a specific API for WebShare:

```python
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username="<proxy-username>",
        proxy_password="<proxy-password>",
    )
)

# all requests done by ytt_api will now be proxied through Webshare
ytt_api.fetch(video_id)
```


## Security
The function should only be accessible to authorized users.  The function should use Google's recommended best practices for security. 

The function should securely store and retrieve the proxy credentials.  For example, Firebase CLI uses Google Secrets Manager (https://firebase.google.com/docs/functions/config-env?gen=2nd):

```
firebase functions:secrets:set SECRET_NAME
# You'll be prompted to enter the secret value
```

Credential that need to be communicated to the agent must be in a file covered by .gitignore.

But they should never be persisted to the repository.

## Logging
The function should log all errors to Google Cloud Logging.  It should also log all requests at the info level. 

Make sure to use the Exceptions from the `youtube-transcript-api` package to catch any errors.  The errors are documented here: https://github.com/jdepoix/youtube-transcript-api#exceptions



## Monitoring
The function should be monitored using Google Cloud Monitoring.  It should have alerts set up for high error rates and high request rates.  It should also have alerts set up for the function going offline.

## Testing
1. Use this as a test video_id: `5nBkQDPwSu0`
2. 