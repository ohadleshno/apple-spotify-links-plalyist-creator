import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from src.cache_manager.file_manager import file_manager
from src.cache_manager.file_constants import MUSIC_LINKS_JSON, INVALID_ALBUM_IDS

def load_json_data(file_path):
    """Load the extracted music data from the JSON file"""
    return file_manager.read_json(file_path)

def create_spotify_playlist(spotify_data, playlist_name, description):
    """Create a Spotify playlist with the extracted tracks"""
    # Set up authentication
    # You need to set these environment variables:
    # SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope="playlist-modify-public",
                redirect_uri=os.environ.get('SPOTIPY_REDIRECT_URI', 'http://localhost:8888/callback')
            )
        )
    except Exception as e:
        print(f"Error authenticating with Spotify: {e}")
        print("\nPlease make sure you've set the following environment variables:")
        print("SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI")
        print("\nYou can get these by creating an app at https://developer.spotify.com/dashboard/")
        return None

    # Get current user's ID
    try:
        current_user = sp.current_user()
        user_id = current_user['id']
        print(f"Authenticated as {user_id}")
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None

    # Create playlist
    try:
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=True,
            description=description
        )
        playlist_id = playlist['id']
        print(f"Created playlist: {playlist_name} (ID: {playlist_id})")
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None

    # Add tracks to playlist
    track_ids = spotify_data['ids']['tracks']
    
    # Spotify requires the track URIs to be in the format spotify:track:id
    track_uris = [f"spotify:track:{track_id}" for track_id in track_ids]
    
    # Add tracks in batches (Spotify limits to 100 tracks per request)
    batch_size = 100
    for i in range(0, len(track_uris), batch_size):
        batch = track_uris[i:i + batch_size]
        try:
            sp.playlist_add_items(playlist_id, batch)
            print(f"Added {len(batch)} tracks to playlist (batch {i//batch_size + 1})")
        except Exception as e:
            print(f"Error adding tracks to playlist: {e}")
    
    # Handle albums - get all tracks from each album and add them
    album_ids = spotify_data['ids']['albums']
    if album_ids:
        album_tracks = []
        invalid_album_ids = []
        
        for album_id in album_ids:
            try:
                results = sp.album_tracks(album_id)
                album_track_uris = [item['uri'] for item in results['items']]
                album_tracks.extend(album_track_uris)
                print(f"Found {len(album_track_uris)} tracks in album {album_id}")
            except Exception as e:
                print(f"Error getting tracks from album {album_id}: {e}")
                if "404" in str(e):
                    # Keep track of invalid album IDs
                    invalid_album_ids.append(album_id)
        
        # Add album tracks in batches
        if album_tracks:
            for i in range(0, len(album_tracks), batch_size):
                batch = album_tracks[i:i+batch_size]
                try:
                    sp.playlist_add_items(playlist_id, batch)
                    print(f"Added {len(batch)} album tracks to playlist (batch {i//batch_size + 1})")
                except Exception as e:
                    print(f"Error adding album tracks to playlist: {e}")
        
        # Report on invalid albums
        if invalid_album_ids:
            print(f"\nFound {len(invalid_album_ids)} invalid album IDs:")
            for album_id in invalid_album_ids:
                print(f"- {album_id}")
            
            # Save invalid IDs to a file for future reference
            try:
                invalid_data = {"invalid_album_ids": invalid_album_ids}
                file_manager.write_json(INVALID_ALBUM_IDS, invalid_data)
                print("Invalid album IDs saved to invalid_album_ids.json")
            except Exception as e:
                print(f"Error saving invalid album IDs: {e}")

    return playlist_id

def main():
    """Main function"""
    playlist_name = sys.argv[1] if len(sys.argv) > 1 else "My Collection Playlist"
    description = sys.argv[2] if len(sys.argv) > 2 else "Playlist created from my music collection"

    # Check if file exists
    if not file_manager.file_exists(MUSIC_LINKS_JSON):
        print(f"File not found: {MUSIC_LINKS_JSON}")
        return

    # Load data from JSON file
    data = load_json_data(MUSIC_LINKS_JSON)
    spotify_data = data['spotify']

    # Create Spotify playlist
    playlist_id = create_spotify_playlist(spotify_data, playlist_name, description)
    
    if playlist_id:
        print(f"\nPlaylist created successfully!")
        print(f"Playlist URL: https://open.spotify.com/playlist/{playlist_id}")
    else:
        print("\nFailed to create playlist. Please check the errors above.")

if __name__ == "__main__":
    main() 