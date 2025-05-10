"""
Module for searching and matching albums on Spotify.
"""

from .base import SpotifyMatcher


class SpotifyAlbumMatcher(SpotifyMatcher):
    """Class to handle matching and searching albums on Spotify"""
    
    def try_specific_album_search(self, album_name, artist_name):
        """Search for an album with specific album and artist information"""
        query = f"album:{album_name} artist:{artist_name}"
        print(f"Searching Spotify for album: {album_name} by {artist_name}")
        
        results = self.sp.search(q=query, type='album', limit=3)
        
        if not results['albums']['items']:
            return None
            
        # Get the first album result
        album = results['albums']['items'][0]
        
        # Check if artist matches
        if not self.check_artist_match(artist_name, album['artists'][0]['name']):
            print(f"  ⚠️ Artist mismatch: {album['artists'][0]['name']} vs {artist_name}")
            return self.create_album_result(album, low_confidence=True)
                
        return self.create_album_result(album)
    
    def try_freeform_album_search(self, album_name, artist_name):
        """Try a freeform search for the album"""
        query = f"{album_name} {artist_name}"
        print(f"  Trying freeform album search: {query}")
        
        results = self.sp.search(q=query, type='album', limit=3)
        
        if not results['albums']['items']:
            return None
            
        album = results['albums']['items'][0]
        print(f"  ⚠️ Found with freeform search: Album '{album['name']}' by {album['artists'][0]['name']}")
        return self.create_album_result(album, low_confidence=True)
    
    def try_artist_only_search(self, artist_name):
        """Try searching for albums by the artist"""
        print(f"  Trying artist-only search for albums by: {artist_name}")
        
        try:
            # Search for the artist first
            results = self.sp.search(q=f"artist:{artist_name}", type='artist', limit=1)
            
            if not results['artists']['items']:
                return None
                
            artist = results['artists']['items'][0]
            
            # Get the artist's albums
            albums = self.sp.artist_albums(artist['id'], limit=5)
            
            if not albums['items']:
                return None
                
            # Return the most popular/first album
            album = albums['items'][0]
            print(f"  ⚠️ Found album by artist search: '{album['name']}' by {album['artists'][0]['name']}")
            return self.create_album_result(album, low_confidence=True)
            
        except Exception as e:
            print(f"  Error in artist search: {e}")
            return None
    
    def create_album_result(self, album, low_confidence=False):
        """Create a standardized result from a Spotify album"""
        try:
            # Get the first track of the album
            album_tracks = self.sp.album_tracks(album['id'])
            
            if not album_tracks['items']:
                return None
                
            first_track = album_tracks['items'][0]
            result = self.create_track_result(first_track, low_confidence)
            
            # Add album information
            result['album_id'] = album['id']
            result['album_name'] = album['name']
            result['album_url'] = album['external_urls']['spotify']
            result['is_album'] = True
            
            return result
            
        except Exception as e:
            print(f"  Error creating album result: {e}")
            return None
    
    def search_for_album(self, album_info):
        """Search Spotify for an album based on title and artist"""
        if not self.sp:
            return None
            
        if 'track' not in album_info or 'artist' not in album_info:
            print(f"Insufficient info to search Spotify effectively for album: {album_info.get('url', 'unknown link')}")
            return None
            
        try:
            # For albums, the 'track' field contains the album name
            album_name = album_info['track']
            artist_name = album_info['artist']
            
            # Try different search strategies in order of precision
            
            # 1. Try specific search with album and artist fields
            result = self.try_specific_album_search(album_name, artist_name)
            if result:
                return result
                
            # 2. Try freeform search for the album
            result = self.try_freeform_album_search(album_name, artist_name)
            if result:
                return result
                
            # 3. Try finding any album by the artist
            result = self.try_artist_only_search(artist_name)
            if result:
                return result
                
            print(f"  ✗ No Spotify album found")
            return None
            
        except Exception as e:
            print(f"Error searching Spotify for album: {e}")
            return None 