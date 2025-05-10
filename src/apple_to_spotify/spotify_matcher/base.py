"""
Base Spotify matcher module containing common functionality.
"""

import os
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from src.apple_to_spotify.apple_music_parser import AppleMusicParser


class SpotifyMatcher:
    """Base class for Spotify matching operations"""
    
    def __init__(self):
        """Initialize the Spotify client"""
        try:
            self.sp = spotipy.Spotify(
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
            print("Or create a .env file in the same directory with these variables.")
            self.sp = None
    
    def normalize_name(self, name):
        """Normalize track or artist name for better matching"""
        if not name:
            return ""
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove featuring artists in various formats
        name = re.sub(r'\s*[\(\[]feat\.?.*?[\)\]]', '', name)
        name = re.sub(r'\s*ft\.?.*?$', '', name)
        
        # Remove special versions
        name = re.sub(r'\s*[\(\[].*?(remix|version|edit|remaster).*?[\)\]]', '', name, flags=re.IGNORECASE)
        
        # Remove common punctuation and extra spaces
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def check_artist_match(self, source_artist, result_artist):
        """Check if the source and result artists match"""
        if not source_artist or not result_artist:
            return False
            
        # Normalize artist names
        source_artist = self.normalize_name(source_artist)
        result_artist = self.normalize_name(result_artist)
        
        # Check for exact match
        if source_artist == result_artist:
            return True
            
        # Check if one contains the other
        if source_artist in result_artist or result_artist in source_artist:
            return True
            
        # Check individual artist names (for collaborations)
        source_artists = [a.strip() for a in source_artist.split('&')]
        result_artists = [a.strip() for a in result_artist.split('&')]
        
        # Check if any source artist matches any result artist
        for s_artist in source_artists:
            for r_artist in result_artists:
                if s_artist in r_artist or r_artist in s_artist:
                    return True
                    
        return False
    
    def check_track_match(self, source_track, result_track):
        """Check if track names match reasonably well"""
        source_track = self.normalize_name(source_track)
        result_track = self.normalize_name(result_track)
        
        # Check for exact match after normalization
        if source_track == result_track:
            return True
            
        # Check if one contains the other
        if source_track in result_track or result_track in source_track:
            return True
            
        # Check for significant word overlap
        source_words = set(source_track.split())
        result_words = set(result_track.split())
        
        # If at least 70% of words match
        if len(source_words) > 0 and len(result_words) > 0:
            overlap_ratio = len(source_words.intersection(result_words)) / max(len(source_words), len(result_words))
            if overlap_ratio >= 0.7:
                return True
                
        return False
    
    def create_track_result(self, track, low_confidence=False):
        """Create a standardized result from a Spotify track"""
        return {
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'uri': track['uri'],
            'url': track['external_urls']['spotify'],
            'low_confidence': low_confidence
        }
    
    def find_equivalents(self, apple_music_links):
        """Find Spotify equivalents for all Apple Music links"""
        if not self.sp:
            return None
            
        # Import here to avoid circular imports
        from .track_matcher import SpotifyTrackMatcher
        from .album_matcher import SpotifyAlbumMatcher
            
        results = {
            'matched': [],
            'not_found': []
        }
        
        print(f"Finding Spotify equivalents for {len(apple_music_links)} Apple Music links...")
        
        # Create instances of our specialized matchers
        track_matcher = SpotifyTrackMatcher()
        album_matcher = SpotifyAlbumMatcher()
        
        for link in apple_music_links:
            track_info = AppleMusicParser.get_track_info(link)
            
            is_song = track_info.get('is_song', 'i=' in link)  # Fallback to URL check if not available

            if is_song:
                spotify_result = track_matcher.search_for_track(track_info)
            else:
                spotify_result = album_matcher.search_for_album(track_info)
            
            # Process the search result
            if spotify_result:
                confidence = "⚠️ Low confidence" if spotify_result.get('low_confidence', False) else "✓ High confidence"
                if spotify_result.get('is_album', False):
                    print(f"{confidence} match: Album '{spotify_result['album_name']}' by {spotify_result['artist']}")
                else:
                    print(f"{confidence} match: {spotify_result['name']} by {spotify_result['artist']}")
                    
                results['matched'].append({
                    'apple_music_link': link,
                    'spotify_url': spotify_result['url'],
                    'type': 'album' if spotify_result.get('is_album', False) else 'song'
                })
            else:
                print(f"✗ Not found: {track_info}")
                results['not_found'].append({
                    'apple_music_link': link,
                    'apple_music_info': track_info
                })
                
        print(f"\nSummary: Found {len(results['matched'])} matches, {len(results['not_found'])} not found")
        return results 