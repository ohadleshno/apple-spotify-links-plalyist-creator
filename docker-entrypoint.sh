#!/bin/bash
set -e

# Check for required Spotify environment variables
if [ -z "$SPOTIPY_CLIENT_ID" ] || [ -z "$SPOTIPY_CLIENT_SECRET" ] || [ -z "$SPOTIPY_REDIRECT_URI" ]; then
  echo "WARNING: Missing required Spotify API credentials!"
  echo "Some API endpoints may not function properly."
  echo "Make sure to set SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI."
fi

# Create necessary directories if they don't exist
mkdir -p /app/resources

# Execute the command specified in CMD (from Dockerfile)
exec "$@" 