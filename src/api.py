from typing import Dict, List, Any, Tuple

from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from src.processing.link_extractor import extract_links_from_content
from src.processing.music_processor import process_music_content, create_playlist

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/health', methods=['GET'])
def health_check() -> Response:
    """Simple health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'API is running'
    })


@app.route('/api/extract-links', methods=['POST'])
def api_extract_links() -> Tuple[Response, int]:
    """Extract unique music links from text content."""
    if not request.json or 'content' not in request.json:
        return jsonify({'error': 'No content provided'}), 400

    content: str = request.json['content']

    extracted_data = extract_links_from_content(content)

    apple_links: set = set()
    spotify_links: set = set()

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


@app.route('/api/process-music-links', methods=['POST'])
def api_process_music_links() -> Tuple[Response, int]:
    """
    Process content with music links and return detailed information.
    
    Request body:
    {
        "content": string  # Text content containing music links
    }
    
    Response:
    {
        "results": [
            {
                "original_link": string,
                "platform": string,       # "Apple Music" or "Spotify"
                "type": string,           # "song" or "album"
                "title": string,          # Track or album title (may be null)
                "artist": string,         # Artist name (may be null)
                "album": string,          # Album name (may be null)
                "apple_music_link": string,
                "spotify_link": string    # May be null if no match found
            },
            ...
        ],
        "total": int
    }
    """
    if not request.json or 'content' not in request.json:
        return jsonify({'error': 'No content provided'}), 400

    content: str = request.json['content']
    result: Dict[str, Any] = process_music_content(content)
    return jsonify(result)


@app.route('/api/create-playlist-from-links', methods=['POST'])
def api_create_playlist_from_links() -> Tuple[Response, int]:
    """
    Create a Spotify playlist directly from links.
    
    Request body:
    {
        "links": List[string],           # Array of Apple Music and Spotify links
        "name": string,                  # Optional playlist name
        "description": string            # Optional playlist description
    }
    
    Response on success:
    {
        "playlist_id": string,
        "playlist_url": string,
        "success": true,
        "stats": {
            "total_links": int,
            "spotify_links": int,
            "apple_music_links": int,
            "other_links": int,
            "matched_apple_music": int,
            "total_tracks": int,
            "total_albums": int
        }
    }
    
    Response on failure:
    {
        "error": string,
        "success": false
    }
    """
    if not request.json or 'links' not in request.json:
        return jsonify({'error': 'No links provided'}), 400
    
    links: List[str] = request.json['links']
    playlist_name: str = request.json.get('name', 'API Created Playlist')
    description: str = request.json.get('description', 'Playlist created through API')
    
    result: Dict[str, Any] = create_playlist(links, playlist_name, description)
    return jsonify(result) if result.get('success') else (jsonify(result), 500)


if __name__ == '__main__':
    app.run(debug=True)
