# Music Conversion REST API

A REST API that exposes the main features of the music conversion application.

## Setup and Installation

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables for Spotify API:
   ```
   export SPOTIPY_CLIENT_ID='your-spotify-client-id'
   export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
   export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
   ```
   You can get these by creating an app at https://developer.spotify.com/dashboard/

3. Run the API server:
   ```
   python src/api.py
   ```

## API Endpoints

### 1. Extract Music Links

Extract Apple Music and Spotify links from text content.

**Endpoint:** `POST /api/extract-links`

**Request Body:**
```json
{
  "content": "Check out this song https://music.apple.com/us/album/song-name/123456789?i=987654321 and this one https://open.spotify.com/track/abc123def456"
}
```

**Response:**
```json
{
  "apple_music": ["https://music.apple.com/us/album/song-name/123456789?i=987654321"],
  "spotify": ["https://open.spotify.com/track/abc123def456"],
  "total": 2
}
```

### 2. Extract IDs

Extract track, album, and playlist IDs from Apple Music and Spotify links.

**Endpoint:** `POST /api/extract-ids`

**Request Body:**
```json
{
  "links": [
    "https://music.apple.com/us/album/song-name/123456789?i=987654321",
    "https://open.spotify.com/track/abc123def456"
  ]
}
```

**Response:**
```json
{
  "apple_music": {
    "links": ["https://music.apple.com/us/album/song-name/123456789?i=987654321"],
    "ids": {
      "tracks": ["987654321"],
      "albums": ["123456789"],
      "playlists": []
    }
  },
  "spotify": {
    "links": ["https://open.spotify.com/track/abc123def456"],
    "ids": {
      "tracks": ["abc123def456"],
      "albums": [],
      "playlists": []
    }
  },
  "other": []
}
```

### 3. Parse Apple Music

Parse an Apple Music link to get track information.

**Endpoint:** `POST /api/parse-apple-music`

**Request Body:**
```json
{
  "link": "https://music.apple.com/us/album/song-name/123456789?i=987654321"
}
```

**Response:**
```json
{
  "url": "https://music.apple.com/us/album/song-name/123456789?i=987654321",
  "track_id": "987654321",
  "is_song": true,
  "track": "Song Name",
  "artist": "Artist Name",
  "album": "Album Name"
}
```

### 4. Create Spotify Playlist

Create a Spotify playlist from track and album IDs.

**Endpoint:** `POST /api/create-spotify-playlist`

**Request Body:**
```json
{
  "track_ids": ["abc123def456", "ghi789jkl012"],
  "album_ids": ["mno345pqr678"],
  "name": "My Playlist",
  "description": "A playlist created via API"
}
```

**Response:**
```json
{
  "playlist_id": "xyz987654321",
  "playlist_url": "https://open.spotify.com/playlist/xyz987654321",
  "tracks_added": 15,
  "errors": []
}
```

### 5. Convert Apple Music to Spotify

Convert Apple Music links to Spotify tracks.

**Endpoint:** `POST /api/convert-apple-to-spotify`

**Request Body:**
```json
{
  "links": [
    "https://music.apple.com/us/album/song-name/123456789?i=987654321"
  ]
}
```

**Response:**
```json
{
  "matches": [
    {
      "apple_music_link": "https://music.apple.com/us/album/song-name/123456789?i=987654321",
      "spotify_id": "abc123def456",
      "track": "Song Name",
      "artist": "Artist Name"
    }
  ],
  "no_matches": []
}
``` 