import re
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from src.cache_manager.output_cache import cache
from src.cache_manager.file_constants import (
    MUSIC_LINKS_JSON,
    MUSIC_LINKS_CSV
)

# Load environment variables from .env file
load_dotenv()

def extract_links_from_file():
    """Extract all links from the CSV file"""
    try:
        # Read CSV using cache with header
        csv_data = cache.read_csv(MUSIC_LINKS_CSV, has_header=True)
        # Get the first column (links) from each row
        links = []
        for row in csv_data.values():
            if row and row[0].strip():  # Check if row exists and first value is not empty
                links.append(row[0].strip())
        return links
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def separate_links(links):
    """Separate links into Apple Music, Spotify, and other links"""
    apple_music_links = []
    spotify_links = []
    other_links = []
    
    for link in links:
        if 'music.apple.com' in link:
            apple_music_links.append(link)
        elif 'open.spotify.com' in link:
            spotify_links.append(link)
        else:
            other_links.append(link)
            
    return apple_music_links, spotify_links, other_links

def extract_apple_music_ids(links):
    """Extract track/album IDs from Apple Music links"""
    track_ids = []
    album_ids = []
    playlist_ids = []
    
    for link in links:
        # Extract the ID
        if 'i=' in link:
            # It's a track
            match = re.search(r'i=(\d+)', link)
            if match:
                track_ids.append(match.group(1))
        elif 'pl.' in link:
            # It's a playlist
            match = re.search(r'(pl\.[a-zA-Z0-9-]+)', link)
            if match:
                playlist_ids.append(match.group(1))
        else:
            # It's probably an album
            # Extract the last part of the URL path which is typically the album ID
            parsed_url = urlparse(link)
            path_parts = parsed_url.path.split('/')
            # Find a numeric ID in the path
            for part in path_parts:
                if part.isdigit():
                    album_ids.append(part)
                    break
    
    return {
        'tracks': list(set(track_ids)),
        'albums': list(set(album_ids)),
        'playlists': list(set(playlist_ids))
    }

def extract_spotify_ids(links):
    """Extract track/album/playlist IDs from Spotify links"""
    track_ids = []
    album_ids = []
    playlist_ids = []
    
    for link in links:
        parsed_url = urlparse(link)
        path_parts = parsed_url.path.split('/')
        
        if len(path_parts) >= 3:
            item_type = path_parts[1]  # track, album, playlist
            item_id = path_parts[2].split('?')[0]  # Remove query parameters
            
            if item_type == 'track':
                track_ids.append(item_id)
            elif item_type == 'album':
                album_ids.append(item_id)
            elif item_type == 'playlist':
                playlist_ids.append(item_id)
    
    return {
        'tracks': list(set(track_ids)),
        'albums': list(set(album_ids)),
        'playlists': list(set(playlist_ids))
    }

def save_to_json(data):
    """Save the extracted data to a JSON file"""
    cache.write_json(MUSIC_LINKS_JSON, data)
    print(f"Data saved to {MUSIC_LINKS_JSON}")

def main():
    # Check if input file exists
    if not cache.file_exists(MUSIC_LINKS_CSV):
        print(f"File not found: {MUSIC_LINKS_CSV}")
        return
    
    # Extract links from file
    links = extract_links_from_file()
    print(f"Found {len(links)} links in the file")
    
    # Separate links
    apple_music_links, spotify_links, other_links = separate_links(links)
    print(f"Apple Music links: {len(apple_music_links)}")
    print(f"Spotify links: {len(spotify_links)}")
    print(f"Other links: {len(other_links)}")
    
    # Extract IDs
    apple_music_ids = extract_apple_music_ids(apple_music_links)
    spotify_ids = extract_spotify_ids(spotify_links)
    
    # Save extracted data
    data = {
        'apple_music': {
            'links': apple_music_links,
            'ids': apple_music_ids
        },
        'spotify': {
            'links': spotify_links,
            'ids': spotify_ids
        },
        'other': other_links
    }
    
    save_to_json(data)

if __name__ == "__main__":
    main() 