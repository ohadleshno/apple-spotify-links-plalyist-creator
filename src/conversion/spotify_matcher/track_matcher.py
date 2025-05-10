"""
Module for searching and matching tracks on Spotify.
"""

from .base import SpotifyMatcher


class SpotifyTrackMatcher(SpotifyMatcher):
    """Class to handle matching and searching tracks on Spotify"""
    
    def try_specific_search(self, track_name, artist_name):
        """Search Spotify with specific track and artist information"""
        query = f"track:{track_name} artist:{artist_name}"
        print(f"Searching Spotify for track: {track_name} by {artist_name}")
        
        results = self.sp.search(q=query, type='track', limit=5)
        
        if not results['tracks']['items']:
            return None
        
        # Try to find a good match in the results
        for track in results['tracks']['items']:
            # Check both artist and track name match
            if self.check_artist_match(artist_name, track['artists'][0]['name']) and \
               self.check_track_match(track_name, track['name']):
                return self.create_track_result(track)
        
        # If no good match, try with less strict criteria (just artist match)
        for track in results['tracks']['items']:
            if self.check_artist_match(artist_name, track['artists'][0]['name']):
                return self.create_track_result(track, low_confidence=True)
                
        # Return the first result with low confidence flag
        track = results['tracks']['items'][0]
        print(f"  ⚠️ Low confidence match: {track['name']} by {track['artists'][0]['name']} - neither track nor artist match well")
        return self.create_track_result(track, low_confidence=True)
    
    def try_track_search(self, track_name):
        """Try a search with just the track name"""
        query = f"track:{track_name}"
        print(f"  Trying search with just track name: {track_name}")
        
        results = self.sp.search(q=query, type='track', limit=3)
        
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            print(f"  ⚠️ Found with track-only search: {track['name']} by {track['artists'][0]['name']}")
            return self.create_track_result(track, low_confidence=True)
            
        return None
    
    def try_freeform_search(self, track_name, artist_name):
        """Try a freeform search without field specifiers"""
        query = f"{track_name} {artist_name}"
        print(f"  Trying freeform search: {query}")
        
        results = self.sp.search(q=query, type='track', limit=3)
        
        if not results['tracks']['items']:
            return None
            
        track = results['tracks']['items'][0]
        if self.check_artist_match(artist_name, track['artists'][0]['name']):
            print(f"  ⚠️ Found with freeform search: {track['name']} by {track['artists'][0]['name']}")
            return self.create_track_result(track, low_confidence=True)
            
        return None
    
    def try_album_track_search(self, track_name, artist_name, album_name):
        """Try searching with track, artist, and album information"""
        if not album_name:
            return None
            
        print(f"  Trying search with album: {track_name} {album_name}")
        query = f"{track_name} album:{album_name}"
        results = self.sp.search(q=query, type='track', limit=3)
        
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            if self.check_artist_match(artist_name, track['artists'][0]['name']):
                print(f"  ⚠️ Found with album search: {track['name']} by {track['artists'][0]['name']}")
                return self.create_track_result(track, low_confidence=True)
                
        return None
    
    def try_lenient_search(self, track_name):
        """Try a more lenient search with just the track name"""
        print(f"  No match found, trying more lenient search for: {track_name}")
        results = self.sp.search(q=track_name, type='track', limit=3)
        
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            print(f"  ⚠️ Found with lenient search: {track['name']} by {track['artists'][0]['name']}")
            return self.create_track_result(track, low_confidence=True)
            
        return None
    
    def search_for_track(self, track_info):
        """Search Spotify for a track based on title and artist"""
        if not self.sp:
            return None
            
        if 'track' not in track_info or 'artist' not in track_info:
            print(f"Insufficient info to search Spotify effectively for: {track_info.get('url', 'unknown link')}")
            return None
            
        try:
            track_name = track_info['track']
            artist_name = track_info['artist']
            album_name = track_info.get('album', '')
            
            # Try different search strategies in order of precision
            
            # 1. Try specific search with track and artist fields
            result = self.try_specific_search(track_name, artist_name)
            if result:
                return result
                
            # 2. Try search with just track field
            result = self.try_track_search(track_name)
            if result:
                return result
                
            # 3. Try freeform search with track and artist
            result = self.try_freeform_search(track_name, artist_name)
            if result:
                return result
            
            # 4. If album name is available, try including it
            result = self.try_album_track_search(track_name, artist_name, album_name)
            if result:
                return result
                
            # 5. Last resort: lenient search with just track name as freeform
            result = self.try_lenient_search(track_name)
            if result:
                return result
                    
            print(f"  ✗ No Spotify track found")
            return None
            
        except Exception as e:
            print(f"Error searching Spotify: {e}")
            return None 