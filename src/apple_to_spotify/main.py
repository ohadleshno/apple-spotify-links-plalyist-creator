"""
Main module for the Apple to Spotify converter.
"""

import os
import sys
from dotenv import load_dotenv
from converter import AppleToSpotifyConverter

# Load environment variables from .env file
load_dotenv()


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Please provide the path to the JSON file")
        print("Usage: python -m apple_to_spotify.main path/to/music_links.json")
        return

    json_file = sys.argv[1]

    # Check if file exists
    if not os.path.exists(json_file):
        print(f"File not found: {json_file}")
        return

    # Run the conversion process
    AppleToSpotifyConverter.convert(json_file)


if __name__ == "__main__":
    main() 