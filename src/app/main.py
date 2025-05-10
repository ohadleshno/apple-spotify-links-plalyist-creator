"""
Main application entry point.
Orchestrates the process of extracting links, matching songs, and creating playlists.
"""
import os
from dotenv import load_dotenv

from src.processing.link_extractor import extract_music_links
from src.processing.id_extractor import main as extract_ids_main
from src.conversion.apple_to_spotify_converter import AppleToSpotifyConverter
from src.app.create_matched_playlist import main as create_playlist_main
from src.cache_manager.file_constants import MUSIC_LINKS_JSON, CHAT_EXPORT, APPLE_TO_SPOTIFY_MATCHES
from src.cache_manager.file_manager import file_manager

# Load environment variables from .env file
load_dotenv()

def run_pipeline():
    """Runs the full music processing and playlist creation pipeline."""
    print("Starting music processing pipeline...")

    # 1. Extract music links from chat export
    print("\nStep 1: Extracting music links...")
    if not file_manager.file_exists(CHAT_EXPORT):
        print(f"Chat export file '{CHAT_EXPORT}' not found in resources directory by FileManager. Aborting.")
        return
    
    music_links_csv = extract_music_links()
    if not music_links_csv:
        print("Link extraction failed. Aborting pipeline.")
        return

    # 2. Extract IDs from the collected links
    print("\nStep 2: Extracting IDs from links...")
    extract_ids_main()
    if not file_manager.file_exists(MUSIC_LINKS_JSON):
        print(f"File '{MUSIC_LINKS_JSON}' not found in resources directory after ID extraction. Aborting pipeline.")
        return

    # 3. Convert Apple Music links to Spotify and find matches
    print("\nStep 3: Converting Apple Music to Spotify and finding matches...")
    conversion_results = AppleToSpotifyConverter.convert(MUSIC_LINKS_JSON)
    if not conversion_results or not file_manager.file_exists(APPLE_TO_SPOTIFY_MATCHES):
        print(f"Apple to Spotify conversion failed or output file '{APPLE_TO_SPOTIFY_MATCHES}' not found. Aborting pipeline.")
        return

    # 4. Create the final matched playlist
    print("\nStep 4: Creating the final matched Spotify playlist...")
    create_playlist_main()
    
    print("\nMusic processing pipeline finished!")

if __name__ == "__main__":
    run_pipeline() 