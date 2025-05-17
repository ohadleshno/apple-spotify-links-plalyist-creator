import re

from flask import Flask, request, jsonify

from src.apple_music.parser import AppleMusicParser
from src.conversion.spotify_matcher import SpotifyTrackMatcher
from src.processing.id_extractor import separate_links, extract_apple_music_ids, \
    extract_spotify_ids
from src.processing.link_extractor import extract_links_from_content
from src.spotify.playlist_creator import create_spotify_playlist

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'API is running'
    })


@app.route('/api/extract-links', methods=['POST'])
def api_extract_links():
    """Extract unique music links from text content."""
    if not request.json or 'content' not in request.json:
        return jsonify({'error': 'No content provided'}), 400

    content = request.json['content']

    extracted_data = extract_links_from_content(content)

    apple_links = set()
    spotify_links = set()

    for link, platform, _ in extracted_data: # Date is ignored here as per original endpoint
        if platform == "Apple Music":
            apple_links.add(link)
        elif platform == "Spotify":
            spotify_links.add(link)

    return jsonify({
        'apple_music': list(apple_links),
        'spotify': list(spotify_links),
        'total': len(apple_links) + len(spotify_links)
    })


@app.route('/api/extract-links-from-file', methods=['POST'])
def api_extract_links_from_file():
    """Extract music links from an uploaded text file, including dates."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        try:
            # Read file content as string
            content = file.read().decode('utf-8')
            
            # Use the refactored function from link_extractor
            extracted_data = extract_links_from_content(content)
            
            # Format the data for JSON response
            # The function returns a list of tuples: (link, platform, date)
            # We can convert this to a list of dictionaries for better JSON readability
            formatted_data = [
                {"link": item[0], "platform": item[1], "date": item[2]}
                for item in extracted_data
            ]
            
            return jsonify({
                'extracted_links': formatted_data,
                'total_found': len(formatted_data)
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
            
    return jsonify({'error': 'Unknown error occurred'}), 500


@app.route('/api/extract-ids', methods=['POST'])
def api_extract_ids():
    """Extract IDs from music links"""
    if not request.json or 'links' not in request.json:
        return jsonify({'error': 'No links provided'}), 400

    links = request.json['links']

    # Use existing functions
    apple_music_links, spotify_links, other_links = separate_links(links)
    apple_music_ids = extract_apple_music_ids(apple_music_links)
    spotify_ids = extract_spotify_ids(spotify_links)

    return jsonify({
        'apple_music': {
            'links': apple_music_links,
            'ids': apple_music_ids
        },
        'spotify': {
            'links': spotify_links,
            'ids': spotify_ids
        },
        'other': other_links
    })


@app.route('/api/parse-apple-music', methods=['POST'])
def api_parse_apple_music():
    """Parse Apple Music links to get track information"""
    if not request.json or 'link' not in request.json:
        return jsonify({'error': 'No link provided'}), 400

    link = request.json['link']

    # Use existing AppleMusicParser
    track_info = AppleMusicParser.get_track_info(link)
    return jsonify(track_info)


@app.route('/api/create-spotify-playlist', methods=['POST'])
def api_create_spotify_playlist():
    """Create a Spotify playlist from track and album IDs"""
    if not request.json:
        return jsonify({'error': 'No data provided'}), 400

    # Prepare spotify_data structure expected by create_spotify_playlist
    spotify_data = {
        'ids': {
            'tracks': request.json.get('track_ids', []),
            'albums': request.json.get('album_ids', [])
        }
    }

    playlist_name = request.json.get('name', 'API Created Playlist')
    description = request.json.get('description', 'Playlist created through API')

    # Call the existing function
    playlist_id = create_spotify_playlist(spotify_data, playlist_name, description)

    if playlist_id:
        return jsonify({
            'playlist_id': playlist_id,
            'playlist_url': f'https://open.spotify.com/playlist/{playlist_id}',
            'success': True
        })
    else:
        return jsonify({'error': 'Failed to create playlist'}), 500


@app.route('/api/convert-apple-to-spotify', methods=['POST'])
def api_convert_apple_to_spotify():
    """Convert Apple Music links to Spotify tracks"""
    if not request.json or 'links' not in request.json:
        return jsonify({'error': 'No links provided'}), 400

    apple_music_links = request.json['links']

    # Call SpotifyTrackMatcher directly instead of using the converter
    # which expects a file path
    matcher = SpotifyTrackMatcher()

    # Find Spotify equivalents
    results = matcher.find_equivalents(apple_music_links)

    if not results:
        return jsonify({'error': 'Failed to find any matches'}), 400

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
