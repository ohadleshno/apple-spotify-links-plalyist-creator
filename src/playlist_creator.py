import re
import os
import sys
import csv
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_links_from_file(file_path):
    """Extract all links from the CSV file"""
    links = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            if row and row[0].strip():  # Check if row exists and first column is not empty
                links.append(row[0].strip())
    return links

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

def save_to_json(data, filename):
    """Save the extracted data to a JSON file"""
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {filename}")

def main():
    # Check if file path is provided
    if len(sys.argv) < 2:
        print("Please provide the path to the CSV file")
        print("Usage: python playlist_creator.py path/to/links.csv")
        return
        
    file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    # Extract links from file
    links = extract_links_from_file(file_path)
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
    
    save_to_json(data, '../outputs/music_links.json')


if __name__ == "__main__":
    main() 