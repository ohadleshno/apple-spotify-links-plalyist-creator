import pytest
import json
from io import BytesIO
from src.api import app # Assuming your Flask app instance is named 'app' in src/api.py

@pytest.fixture
def client():
    # Create a test client using the Flask application configured for testing
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Tests for /api/extract-links (existing endpoint, takes JSON content)
def test_api_extract_links_success(client):
    payload = {
        'content': "[01/01/2024, 12:00:00] User: Check https://music.apple.com/album/123 and https://open.spotify.com/track/456"
    }
    response = client.post('/api/extract-links', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "https://music.apple.com/album/123" in data['apple_music']
    assert "https://open.spotify.com/track/456" in data['spotify']
    assert data['total'] == 2

def test_api_extract_links_no_content(client):
    response = client.post('/api/extract-links', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'No content provided'

def test_api_extract_links_empty_content(client):
    payload = {'content': ""}
    response = client.post('/api/extract-links', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['apple_music'] == []
    assert data['spotify'] == []
    assert data['total'] == 0

def test_api_extract_links_from_file_success(client):
    file_content = b"[02/02/2024, 14:30:00] Alice: Here is an Apple Music link https://music.apple.com/us/album/song/abc\n[02/02/2024, 14:35:00] Bob: And a Spotify one https://open.spotify.com/album/def?si=123"
    data = {'file': (BytesIO(file_content), 'test_chat.txt')}
    
    response = client.post('/api/extract-links-from-file', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    json_data = json.loads(response.data)
    
    assert 'extracted_links' in json_data
    assert json_data['total_found'] == 2
    
    links = json_data['extracted_links']
    assert len(links) == 2
    
    assert {"link": "https://music.apple.com/us/album/song/abc", "platform": "Apple Music", "date": "02/02/2024"} in links
    assert {"link": "https://open.spotify.com/album/def?si=123", "platform": "Spotify", "date": "02/02/2024"} in links

def test_api_extract_links_from_file_no_file_part(client):
    response = client.post('/api/extract-links-from-file', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'No file part in the request'

def test_api_extract_links_from_file_no_selected_file(client):
    data = {'file': (BytesIO(b''), '')}
    response = client.post('/api/extract-links-from-file', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'No selected file'

def test_api_extract_links_from_file_empty_file(client):
    data = {'file': (BytesIO(b''), 'empty.txt')}
    response = client.post('/api/extract-links-from-file', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert json_data['extracted_links'] == []
    assert json_data['total_found'] == 0

def test_api_extract_links_from_file_no_links_in_file(client):
    file_content = b"[03/03/2024, 10:00:00] Test: This file has text but no music links."
    data = {'file': (BytesIO(file_content), 'no_links.txt')}
    response = client.post('/api/extract-links-from-file', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert json_data['extracted_links'] == []
    assert json_data['total_found'] == 0

