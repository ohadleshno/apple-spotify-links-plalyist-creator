"""
Module for handling Spotify API interactions and track matching.
This file re-exports the classes from the spotify_matcher module for backward compatibility.
"""

from .spotify_matcher.base import SpotifyMatcher
from .spotify_matcher.track_matcher import SpotifyTrackMatcher
from .spotify_matcher.album_matcher import SpotifyAlbumMatcher

# Re-export for backward compatibility
__all__ = ['SpotifyMatcher', 'SpotifyTrackMatcher', 'SpotifyAlbumMatcher'] 