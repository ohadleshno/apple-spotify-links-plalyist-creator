"""
Module for handling the conversion from Apple Music to Spotify.
"""

import json

from spotify_matcher import SpotifyTrackMatcher


class AppleToSpotifyConverter:
    """Main class to handle the conversion process"""
    
    @staticmethod
    def load_json_data(file_path):
        """Load the extracted music data from the JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_results(results, output_file="apple_to_spotify_matches.json"):
        """Save results to a JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved match results to {output_file}")
    
    @staticmethod
    def convert(json_file):
        """Convert Apple Music links to Spotify tracks"""
        # Load data from JSON file
        data = AppleToSpotifyConverter.load_json_data(json_file)
        
        # Get Apple Music links
        apple_music_links = data['apple_music']['links']
        
        # Initialize the Spotify matcher
        matcher = SpotifyTrackMatcher()
        
        # Find Spotify equivalents
        results = matcher.find_equivalents(apple_music_links)
        
        if not results:
            print("Failed to find any matches. Please check the errors above.")
            return None
            
        # Save results to a file
        AppleToSpotifyConverter.save_results(results)
        return results 