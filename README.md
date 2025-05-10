# Music Playlist Creator

This project helps you create playlists on both Apple Music and Spotify from a list of links.

## Prerequisites

- Python 3.6 or higher
- PIP (Python package manager)

## Installation

1. Clone or download this repository
2. Install the required packages:

```
pip install -r requirements.txt
```

## Usage

### Step 1: Parse the Music Links

First, you need to parse your music links and extract the track IDs:

```
python playlist_creator.py path/to/your/links.csv
```

This will generate a `music_links.json` file with all the extracted data.

### Step 2: Create a Spotify Playlist

To create a playlist on Spotify, you'll need to:

1. Create a Spotify Developer account at [developer.spotify.com](https://developer.spotify.com/)
2. Create a new application
3. Set the redirect URI to `http://localhost:8888/callback` (or any other URL you prefer)
4. Get your Client ID and Client Secret
5. Set the following environment variables:

```bash
export SPOTIPY_CLIENT_ID="your_client_id"
export SPOTIPY_CLIENT_SECRET="your_client_secret"
export SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"
```

6. Run the script:

```
python spotify_playlist_creator.py music_links.json "My Awesome Playlist" "My playlist description"
```

The script will authenticate you with Spotify (opening a browser window), create the playlist, and add all the tracks.

### Step 3: Create an Apple Music Playlist

Creating an Apple Music playlist is more complex and requires additional setup:

#### Option 1: Manual Playlist Creation

The easiest way is to create the playlist manually:

1. Run the script to get a list of track IDs:

```
python apple_music_playlist_creator.py music_links.json "My Awesome Playlist" "My playlist description"
```

2. Follow the manual instructions displayed by the script

#### Option 2: Using Apple Music API (Advanced)

For programmatic creation using the Apple Music API:

1. Enroll in the Apple Developer Program
2. Create a MusicKit identifier in your developer account
3. Generate a private key
4. Get your Team ID and Key ID
5. Run the script with these parameters:

```
python apple_music_playlist_creator.py music_links.json "My Awesome Playlist" "My playlist description" "your_key_id" "your_team_id" "path/to/private_key.p8"
```

Alternatively, set these environment variables:

```bash
export APPLE_MUSIC_KEY_ID="your_key_id"
export APPLE_MUSIC_TEAM_ID="your_team_id"
export APPLE_MUSIC_KEY_FILE="path/to/private_key.p8"
```

## Additional Information

- The Apple Music API requires both a developer token and a user token. The user token requires user authentication.
- For more information about the Apple Music API, see the [official documentation](https://developer.apple.com/documentation/applemusicapi).
- For more information about the Spotify Web API, see the [official documentation](https://developer.spotify.com/documentation/web-api/).

## Requirements

Create a `requirements.txt` file with:

```
spotipy>=2.19.0
pyjwt>=2.1.0
cryptography>=35.0.0
requests>=2.26.0
```

## Virtual Environment

To use the virtual environment, first activate it:

```
source venv/bin/activate
``` 