# Apple Music to Spotify Converter

This package provides functionality to convert Apple Music links to Spotify tracks.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd <repository-directory>

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Setting up credentials

Before using the converter, you need to set up your Spotify API credentials:

1. Create a Spotify Developer account at [https://developer.spotify.com/dashboard/](https://developer.spotify.com/dashboard/)
2. Create a new application to get your Client ID and Client Secret
3. Set the redirect URI to `http://localhost:8888/callback` in your application settings
4. Create a `.env` file in the root directory with the following content:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
```

### Running the converter

The input to the converter should be a JSON file containing Apple Music links in the following format:

```json
{
  "apple_music": {
    "links": [
      "https://music.apple.com/us/album/song-name/id123456789",
      "https://music.apple.com/us/album/another-song/id987654321"
    ]
  }
}
```

Run the converter using:

```bash
# Using the runner script
./apple_to_spotify_run.py path/to/music_links.json

# Or using the module directly
python -m apple_to_spotify.main path/to/music_links.json
```

The converter will output a JSON file named `apple_to_spotify_matches.json` with the results, including Spotify track information for the matched tracks.

## Package Structure

- `apple_music_parser.py` - Handles parsing Apple Music links and extracting track information
- `spotify_matcher.py` - Manages Spotify authentication and track matching logic
- `converter.py` - Controls the overall conversion process
- `main.py` - Main entry point for the package

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- spotipy
- python-dotenv 