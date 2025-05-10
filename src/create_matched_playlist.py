import os
from datetime import datetime
from dotenv import load_dotenv
from src.cache_manager.output_cache import cache
from src.cache_manager.file_constants import (
    APPLE_TO_SPOTIFY_MATCHES,
    MUSIC_LINKS_JSON,
    INVALID_ALBUM_IDS
)
from spotify_playlist_creator import create_spotify_playlist

# Load environment variables from .env file
load_dotenv()

def remove_invalid_album_ids(invalid_ids_file, matches_file, music_links_file):
    """Remove invalid album IDs from the data sources"""
    if not os.path.exists(invalid_ids_file):
        print("No invalid album IDs file found.")
        return
    
    # Load invalid IDs
    invalid_data = cache.read_json(invalid_ids_file)
    
    invalid_ids = invalid_data.get("invalid_album_ids", [])
    if not invalid_ids:
        print("No invalid album IDs to remove.")
        return
    
    print(f"Found {len(invalid_ids)} invalid album IDs to remove.")
    
    # Update matches file
    if cache.file_exists(matches_file):
        matches_data = cache.read_json(matches_file)
        
        # Filter out matches with invalid album IDs
        filtered_matches = []
        removed_count = 0
        
        for match in matches_data.get("matched", []):
            spotify_url = match.get("spotify_url", "")
            match_type = match.get("type", "")
            
            if match_type == "album" and "open.spotify.com/album/" in spotify_url:
                # Extract the ID from the spotify URL
                parts = spotify_url.split("/")
                spotify_id = parts[-1].split("?")[0]  # Remove any query parameters
                
                if spotify_id in invalid_ids:
                    removed_count += 1
                    continue  # Skip this match
            
            # Keep valid matches
            filtered_matches.append(match)
        
        if removed_count > 0:
            matches_data["matched"] = filtered_matches
            cache.write_json(matches_file, matches_data)
            print(f"Removed {removed_count} invalid album references from {matches_file}")
    
    # Update music links file
    if cache.file_exists(music_links_file):
        music_data = cache.read_json(music_links_file)
        
        # Remove invalid album IDs
        album_ids = music_data.get("spotify", {}).get("ids", {}).get("albums", [])
        filtered_album_ids = [album_id for album_id in album_ids if album_id not in invalid_ids]
        
        if len(filtered_album_ids) < len(album_ids):
            music_data["spotify"]["ids"]["albums"] = filtered_album_ids
            print(f"Removed {len(album_ids) - len(filtered_album_ids)} invalid album IDs from {music_links_file}")
            
            # Also filter links
            links = music_data.get("spotify", {}).get("links", [])
            filtered_links = []
            removed_links = 0
            
            for link in links:
                if "open.spotify.com/album/" in link:
                    parts = link.split("/")
                    if len(parts) >= 5:
                        album_id = parts[-1].split("?")[0]
                        if album_id in invalid_ids:
                            removed_links += 1
                            continue
                
                filtered_links.append(link)
            
            if removed_links > 0:
                music_data["spotify"]["links"] = filtered_links
                print(f"Removed {removed_links} invalid album links from {music_links_file}")
            
            cache.write_json(music_links_file, music_data)
    
    # Remove the invalid IDs file
    try:
        os.remove(invalid_ids_file)
        print(f"Removed {invalid_ids_file} file.")
    except:
        print(f"Could not remove {invalid_ids_file} file.")

def extract_spotify_ids_from_matches(matches_file):
    """Extract Spotify track and album IDs from the matches file"""
    matches_data = cache.read_json(matches_file)
    
    # Initialize IDs
    spotify_data = {
        "ids": {
            "tracks": [],
            "albums": []
        }
    }
    
    # Process each match
    for match in matches_data["matched"]:
        spotify_url = match["spotify_url"]
        match_type = match["type"]
        
        # Extract the ID from the spotify URL
        # Format: https://open.spotify.com/track/ID or https://open.spotify.com/album/ID
        parts = spotify_url.split("/")
        spotify_id = parts[-1].split("?")[0]  # Remove any query parameters
        
        if match_type == "song":
            spotify_data["ids"]["tracks"].append(spotify_id)
        elif match_type == "album":
            spotify_data["ids"]["albums"].append(spotify_id)
    
    return spotify_data

def extract_spotify_ids_from_music_links(music_links_file):
    """Extract Spotify track and album IDs directly from music_links.json"""
    music_data = cache.read_json(music_links_file)
    
    # Get Spotify IDs that are already in the file
    spotify_data = {
        "ids": {
            "tracks": music_data.get("spotify", {}).get("ids", {}).get("tracks", []),
            "albums": music_data.get("spotify", {}).get("ids", {}).get("albums", []),
            "playlists": music_data.get("spotify", {}).get("ids", {}).get("playlists", [])
        }
    }
    
    # Also process any Spotify links
    spotify_links = music_data.get("spotify", {}).get("links", [])
    for link in spotify_links:
        # Skip if not a Spotify URL
        if not "open.spotify.com" in link:
            continue
            
        # Extract the type and ID
        parts = link.split("/")
        if len(parts) >= 5:
            item_type = parts[-2]  # track, album, or playlist
            item_id = parts[-1].split("?")[0]  # Remove query parameters
            
            if item_type == "track" and item_id not in spotify_data["ids"]["tracks"]:
                spotify_data["ids"]["tracks"].append(item_id)
            elif item_type == "album" and item_id not in spotify_data["ids"]["albums"]:
                spotify_data["ids"]["albums"].append(item_id)
            elif item_type == "playlist" and item_id not in spotify_data["ids"]["playlists"]:
                spotify_data["ids"]["playlists"].append(item_id)
    
    return spotify_data

def combine_spotify_data(data1, data2):
    """Combine two sets of Spotify data, removing duplicates"""
    combined = {
        "ids": {
            "tracks": [],
            "albums": [],
            "playlists": []
        }
    }
    
    # Add tracks without duplicates
    track_ids = set(data1["ids"].get("tracks", []) + data2["ids"].get("tracks", []))
    combined["ids"]["tracks"] = list(track_ids)
    
    # Add albums without duplicates
    album_ids = set(data1["ids"].get("albums", []) + data2["ids"].get("albums", []))
    combined["ids"]["albums"] = list(album_ids)
    
    # Add playlists without duplicates
    playlist_ids = set(data1["ids"].get("playlists", []) + data2["ids"].get("playlists", []))
    combined["ids"]["playlists"] = list(playlist_ids)
    
    return combined

def split_data_into_chunks(spotify_data, max_per_playlist=200):
    """Split the Spotify data into multiple chunks to avoid exceeding API limits"""
    chunks = []
    
    # We need to split both tracks and albums
    tracks = spotify_data["ids"]["tracks"]
    albums = spotify_data["ids"]["albums"]
    
    # Assume each album is approximately 10 songs
    songs_per_album = 10
    
    # Create chunks with a mix of tracks and albums
    current_chunk_tracks = []
    current_chunk_albums = []
    current_chunk_size = 0
    
    # First add tracks
    for track in tracks:
        if current_chunk_size >= max_per_playlist:
            # This chunk is full, save it and start a new one
            chunks.append({
                "ids": {
                    "tracks": current_chunk_tracks,
                    "albums": current_chunk_albums,
                    "playlists": spotify_data["ids"].get("playlists", [])
                }
            })
            current_chunk_tracks = []
            current_chunk_albums = []
            current_chunk_size = 0
        
        # Add track to current chunk
        current_chunk_tracks.append(track)
        current_chunk_size += 1
    
    # Now add albums, treating each album as approximately 10 songs
    for album in albums:
        if current_chunk_size + songs_per_album > max_per_playlist:
            # This chunk would overflow with the album, save it and start a new one
            chunks.append({
                "ids": {
                    "tracks": current_chunk_tracks,
                    "albums": current_chunk_albums,
                    "playlists": spotify_data["ids"].get("playlists", [])
                }
            })
            current_chunk_tracks = []
            current_chunk_albums = []
            current_chunk_size = 0
        
        # Add album to current chunk
        current_chunk_albums.append(album)
        current_chunk_size += songs_per_album
    
    # Don't forget to add the last chunk if it has any tracks or albums
    if current_chunk_tracks or current_chunk_albums:
        chunks.append({
            "ids": {
                "tracks": current_chunk_tracks,
                "albums": current_chunk_albums,
                "playlists": spotify_data["ids"].get("playlists", [])
            }
        })
    
    return chunks

def main():
    """Main function"""
    # Check if the invalid album IDs file exists and clean up if needed
    if os.path.exists(INVALID_ALBUM_IDS):
        print("\nFound invalid album IDs file from a previous run.")
        choice = input("Do you want to clean up invalid album IDs from your data sources? (y/n): ").strip().lower()
        if choice == 'y':
            remove_invalid_album_ids(INVALID_ALBUM_IDS, APPLE_TO_SPOTIFY_MATCHES, MUSIC_LINKS_JSON)
    
    # Check if files exist
    for file_path in [APPLE_TO_SPOTIFY_MATCHES, MUSIC_LINKS_JSON]:
        if not cache.file_exists(file_path):
            print(f"File not found: {file_path}")
            return
    
    # Extract Spotify IDs from matches
    match_spotify_data = extract_spotify_ids_from_matches(APPLE_TO_SPOTIFY_MATCHES)
    print(f"From matches: {len(match_spotify_data['ids']['tracks'])} tracks and {len(match_spotify_data['ids']['albums'])} albums")
    
    # Extract Spotify IDs from music links
    music_spotify_data = extract_spotify_ids_from_music_links(MUSIC_LINKS_JSON)
    print(f"From music links: {len(music_spotify_data['ids']['tracks'])} tracks and {len(music_spotify_data['ids']['albums'])} albums")
    
    # Combine the data
    combined_data = combine_spotify_data(match_spotify_data, music_spotify_data)
    print(f"Combined unique IDs: {len(combined_data['ids']['tracks'])} tracks and {len(combined_data['ids']['albums'])} albums")
    
    # Split the data into chunks of 200 songs per playlist
    chunks = split_data_into_chunks(combined_data, 150)
    print(f"Splitting into {len(chunks)} playlists with max 150 songs each (counting each album as ~10 songs)")
    
    # Create playlists for each chunk
    date_str = datetime.now().strftime("%Y-%m-%d")
    base_name = "Voice from the east"
    description = "Created with love and hate to apple music API"
    
    created_playlists = []
    
    for i, chunk in enumerate(chunks):
        # Create playlist name with part number
        playlist_name = f"{base_name} {date_str} (Part {i+1}/{len(chunks)})"
        
        print(f"\nCreating playlist {i+1} of {len(chunks)}: {playlist_name}")
        print(f"Contains {len(chunk['ids']['tracks'])} tracks and {len(chunk['ids']['albums'])} albums")
        
        # Create the playlist
        playlist_id = create_spotify_playlist(chunk, playlist_name, description)
        
        if playlist_id:
            print(f"Playlist {i+1} created successfully!")
            print(f"Playlist URL: https://open.spotify.com/playlist/{playlist_id}")
            created_playlists.append(playlist_id)
        else:
            print(f"Failed to create playlist {i+1}. Please check the errors above.")
    
    # Summary
    if created_playlists:
        print(f"\nCreated {len(created_playlists)} playlists out of {len(chunks)} attempted.")
        for i, playlist_id in enumerate(created_playlists):
            print(f"Playlist {i+1}: https://open.spotify.com/playlist/{playlist_id}")
    else:
        print("\nFailed to create any playlists. Please check the errors above.")

if __name__ == "__main__":
    main() 