"""
Module for processing music content and links.
"""
from src.processing.link_extractor import extract_links_from_content
from src.processing.id_extractor import separate_links, extract_spotify_ids
from src.apple_music.parser import AppleMusicParser
from src.conversion.spotify_matcher import SpotifyTrackMatcher
from src.conversion.spotify_matcher.album_matcher import SpotifyAlbumMatcher
from src.spotify.playlist_creator import create_spotify_playlist

def process_music_content(content):
    """Process content with music links and return detailed information."""
    extracted_data = extract_links_from_content(content)
    all_links = [item[0] for item in extracted_data]
    return process_music_links(all_links)

def process_music_links(links):
    """Process a list of music links and return detailed information."""
    apple_music_links, spotify_links, _ = separate_links(links)
    detailed_results = []
    
    process_spotify_links(spotify_links, detailed_results)
    process_apple_music_links(apple_music_links, detailed_results)
    
    return {'results': detailed_results, 'total': len(detailed_results)}

def process_spotify_links(spotify_links, results):
    """Process Spotify links and add to results."""
    for link in spotify_links:
        try:
            spotify_id_data = extract_spotify_ids([link])
            is_song = bool(spotify_id_data['tracks'])
            results.append(create_spotify_result(link, is_song))
        except Exception as e:
            print(f"Error processing Spotify link {link}: {e}")

def create_spotify_result(link, is_song):
    """Create result object for a Spotify link."""
    return {
        'original_link': link,
        'platform': 'Spotify',
        'type': 'song' if is_song else 'album',
        'spotify_link': link,
        'apple_music_link': None
    }

def process_apple_music_links(apple_music_links, results):
    """Process Apple Music links and add to results."""
    matcher = SpotifyTrackMatcher()
    for link in apple_music_links:
        try:
            track_info = AppleMusicParser.get_track_info(link)
            spotify_link = find_spotify_equivalent(track_info, matcher)
            results.append(create_apple_result(link, track_info, spotify_link))
        except Exception as e:
            print(f"Error processing Apple Music link {link}: {e}")

def find_spotify_equivalent(track_info, matcher):
    """Find Spotify equivalent for Apple Music track info."""
    if not matcher.sp:
        return None
        
    is_song = track_info.get('is_song', 'i=' in track_info.get('url', ''))
    if is_song:
        spotify_result = matcher.search_for_track(track_info)
    else:
        album_matcher = SpotifyAlbumMatcher()
        spotify_result = album_matcher.search_for_album(track_info)
        
    return spotify_result['url'] if spotify_result else None

def create_apple_result(link, track_info, spotify_link):
    """Create result object for an Apple Music link."""
    is_song = track_info.get('is_song', 'i=' in link)
    return {
        'original_link': link,
        'platform': 'Apple Music',
        'type': 'song' if is_song else 'album',
        'title': track_info.get('track'),
        'artist': track_info.get('artist'),
        'album': track_info.get('album'),
        'apple_music_link': link,
        'spotify_link': spotify_link
    }

def create_playlist(links, playlist_name, description):
    """Create a Spotify playlist from a list of links."""
    apple_music_links, spotify_links, other_links = separate_links(links)
    spotify_ids = extract_spotify_ids(spotify_links)
    
    apple_music_track_ids, apple_music_album_ids = get_apple_music_ids(apple_music_links)
    
    spotify_data = prepare_spotify_data(spotify_ids, apple_music_track_ids, apple_music_album_ids)
    playlist_id = create_spotify_playlist(spotify_data, playlist_name, description)
    
    return create_playlist_result(playlist_id, links, spotify_links, apple_music_links, 
                                  other_links, apple_music_track_ids, apple_music_album_ids,
                                  spotify_ids)

def get_apple_music_ids(apple_music_links):
    """Get Spotify IDs from Apple Music links."""
    if not apple_music_links:
        return [], []
        
    matcher = SpotifyTrackMatcher()
    apple_music_matches = matcher.find_equivalents(apple_music_links)
    
    track_ids, album_ids = [], []
    if apple_music_matches and 'matched' in apple_music_matches:
        extract_ids_from_matches(apple_music_matches['matched'], track_ids, album_ids)
        
    return track_ids, album_ids

def extract_ids_from_matches(matches, track_ids, album_ids):
    """Extract track and album IDs from matches."""
    for match in matches:
        spotify_url = match.get('spotify_url')
        match_type = match.get('type')
        
        if not spotify_url or len(spotify_url.split('/')) < 5:
            continue
            
        item_id = spotify_url.split('/')[-1].split('?')[0]
        
        if match_type == 'song':
            track_ids.append(item_id)
        elif match_type == 'album':
            album_ids.append(item_id)

def prepare_spotify_data(spotify_ids, additional_track_ids, additional_album_ids):
    """Prepare data structure for Spotify playlist creation."""
    all_track_ids = spotify_ids['tracks'] + additional_track_ids
    all_album_ids = spotify_ids['albums'] + additional_album_ids
    
    return {
        'ids': {
            'tracks': all_track_ids,
            'albums': all_album_ids
        }
    }

def create_playlist_result(playlist_id, links, spotify_links, apple_music_links, 
                          other_links, additional_track_ids, additional_album_ids,
                          spotify_ids):
    """Create result object for playlist creation."""
    if not playlist_id:
        return {'error': 'Failed to create playlist', 'success': False}
        
    return {
        'playlist_id': playlist_id,
        'playlist_url': f'https://open.spotify.com/playlist/{playlist_id}',
        'success': True,
        'stats': create_stats_object(links, spotify_links, apple_music_links, 
                                    other_links, additional_track_ids, additional_album_ids,
                                    spotify_ids)
    }

def create_stats_object(links, spotify_links, apple_music_links, other_links,
                       additional_track_ids, additional_album_ids, spotify_ids):
    """Create stats object for playlist creation result."""
    return {
        'total_links': len(links),
        'spotify_links': len(spotify_links),
        'apple_music_links': len(apple_music_links),
        'other_links': len(other_links),
        'matched_apple_music': len(additional_track_ids) + len(additional_album_ids),
        'total_tracks': len(spotify_ids['tracks'] + additional_track_ids),
        'total_albums': len(spotify_ids['albums'] + additional_album_ids)
    } 