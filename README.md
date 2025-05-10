# Music Playlist Creator

A tool for extracting music links from chat exports and creating Spotify playlists.

## Overview

This application automates the process of:
1. Extracting music links (Spotify, Apple Music, etc.) from chat exports
2. Converting Apple Music links to their Spotify equivalents
3. Creating a Spotify playlist with all the matched songs

## Requirements

- Python 3.6 or higher
- Spotify Developer account (for API access)
- A chat export file containing music links

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd music-playlist-creator
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # Activate on macOS/Linux
   source venv/bin/activate
   
   # Activate on Windows (cmd)
   venv\Scripts\activate.bat
   
   # Activate on Windows (PowerShell)
   venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project root with your Spotify API credentials:
   ```
   SPOTIPY_CLIENT_ID="your_spotify_client_id"
   SPOTIPY_CLIENT_SECRET="your_spotify_client_secret"
   SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"
   ```

   To get these credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Create a new application
   - Set the redirect URI to `http://localhost:8888/callback`
   - Copy the Client ID and Client Secret to your `.env` file

2. Place your chat export file in the expected location:
   - The default location is in the `resources` directory with the filename specified by the `CHAT_EXPORT` constant (check `src/cache_manager/file_constants.py` for the exact path)

## Usage

Run the main pipeline with:

```bash
python src/app/main.py
```

This will:
1. Extract music links from your chat export
2. Extract track IDs from those links
3. Convert Apple Music links to Spotify and find matches
4. Create a Spotify playlist with all matched tracks

## How It Works

1. **Link Extraction**: The application parses your chat export file to find and extract music links.
2. **ID Extraction**: It processes these links to identify unique track identifiers for each song.
3. **Platform Conversion**: Apple Music links are converted to their Spotify equivalents using matching algorithms.
4. **Playlist Creation**: A Spotify playlist is created with all the matched tracks.

## Troubleshooting

- **Missing chat export file**: Ensure your chat export is placed in the correct location.
- **Authentication errors**: Verify your Spotify API credentials in the `.env` file.
- **Browser opens but no playlist created**: Make sure to complete the Spotify authentication when the browser window opens.

## License

[License information here] 