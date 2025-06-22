#!/bin/bash

echo "=== Firebase Functions Deployment Script ==="

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Activate virtual environment and install dependencies
echo "Setting up Python environment..."
cd functions
source venv/bin/activate
python3.12 -m pip install -r requirements.txt

# Go back to root and deploy
cd ..
echo "Deploying to Firebase..."
firebase deploy --only functions

echo "Deployment complete!"
