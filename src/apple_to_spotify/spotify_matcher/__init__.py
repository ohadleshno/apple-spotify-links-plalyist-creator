"""
Module for handling Spotify API interactions and track/album matching.
"""

from .base import SpotifyMatcher
from .track_matcher import SpotifyTrackMatcher
from .album_matcher import SpotifyAlbumMatcher

# Re-export the main classes to maintain the same import interface
__all__ = ['SpotifyMatcher', 'SpotifyTrackMatcher', 'SpotifyAlbumMatcher'] 