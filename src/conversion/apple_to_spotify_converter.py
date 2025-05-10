"""
Module for handling the conversion from Apple Music to Spotify.
"""

from src.cache_manager.file_manager import file_manager
from src.cache_manager.file_constants import APPLE_TO_SPOTIFY_MATCHES
from .spotify_matcher import SpotifyTrackMatcher


class AppleToSpotifyConverter:
    """Main class to handle the conversion process"""
    
    @staticmethod
    def load_json_data(file_path):
        """Load the extracted music data from the JSON file"""
        return file_manager.read_json(file_path)
    
    @staticmethod
    def save_results(results):
        """Save results to a JSON file"""
        file_manager.write_json(APPLE_TO_SPOTIFY_MATCHES, results)
    
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