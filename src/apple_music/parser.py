"""
Simple module for parsing Apple Music links using Playwright.
"""

import asyncio
import json
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright


class AppleMusicParser:
    """Simplified parser for Apple Music links using Playwright"""

    @classmethod
    async def get_track_info_async(cls, link):
        """Get track information from Apple Music link using Playwright"""
        try:
            # Initialize basic info from URL
            track_info = {'url': link}

            # Extract track ID from URL query parameters if present
            parsed_url = urlparse(link)
            query_params = parse_qs(parsed_url.query)
            track_id = query_params.get('i', [None])[0]
            if track_id:
                track_info['track_id'] = track_id
                track_info['is_song'] = True
            else:
                track_info['is_song'] = False
                track_info['is_album'] = True

            # Use Playwright to get JSON-LD data which contains all the info we need
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
                page = await context.new_page()

                # Navigate to the Apple Music link
                await page.goto(link, wait_until="domcontentloaded", timeout=30000)

                # Get JSON-LD data which contains all track information
                json_ld = await page.evaluate("""
                () => {
                    const script = document.querySelector('script[type="application/ld+json"]');
                    return script ? script.textContent : null;
                }
                """)

                # Get metadata as fallback
                meta_info = await page.evaluate("""
                () => {
                    const title = document.querySelector('meta[property="og:title"]');
                    const desc = document.querySelector('meta[property="og:description"]');
                    const type = document.querySelector('meta[property="og:type"]');
                    return {
                        title: title ? title.getAttribute('content') : null,
                        description: desc ? desc.getAttribute('content') : null,
                        type: type ? type.getAttribute('content') : null
                    };
                }
                """)

                # Clean up browser
                await browser.close()

                # Try to determine content type from meta information
                if meta_info and meta_info.get('type'):
                    content_type = meta_info.get('type')
                    if 'music.song' in content_type:
                        track_info['is_song'] = True
                        track_info['is_album'] = False
                    elif 'music.album' in content_type:
                        track_info['is_song'] = False
                        track_info['is_album'] = True

                # Parse the JSON-LD data
                if json_ld:
                    try:
                        data = json.loads(json_ld)

                        # Determine content type from JSON-LD
                        if '@type' in data:
                            content_type = data['@type']
                            if content_type == 'MusicRecording':
                                track_info['is_song'] = True
                                track_info['is_album'] = False
                            elif content_type == 'MusicAlbum':
                                track_info['is_song'] = False
                                track_info['is_album'] = True

                        # Extract track name - directly available in top level 'name'
                        if 'name' in data:
                            track_info['track'] = data['name']

                        # Extract artist info - might be in 'audio.byArtist' array
                        if 'audio' in data and 'byArtist' in data['audio']:
                            artists = data['audio']['byArtist']
                            if isinstance(artists, list) and len(artists) > 0:
                                track_info['artist'] = artists[0].get('name')
                            elif isinstance(artists, dict):
                                track_info['artist'] = artists.get('name')

                        # Direct byArtist at top level is also possible
                        elif 'byArtist' in data:
                            artists = data['byArtist']
                            if isinstance(artists, list) and len(artists) > 0:
                                track_info['artist'] = artists[0].get('name')
                            elif isinstance(artists, dict):
                                track_info['artist'] = artists.get('name')
                            else:
                                track_info['artist'] = str(artists)

                        # Extract album info - typically in 'audio.inAlbum'
                        if 'audio' in data and 'inAlbum' in data['audio']:
                            album = data['audio']['inAlbum']
                            if isinstance(album, dict):
                                track_info['album'] = album.get('name')

                        # Direct inAlbum at top level is also possible
                        elif 'inAlbum' in data:
                            album = data['inAlbum']
                            if isinstance(album, dict):
                                track_info['album'] = album.get('name')

                    except json.JSONDecodeError:
                        print("Failed to parse JSON-LD data")

                # Use meta info as fallback
                if meta_info and ('track' not in track_info or 'artist' not in track_info):
                    title = meta_info.get('title')
                    description = meta_info.get('description')

                    if title and ' מאת ' in title and 'track' not in track_info:
                        parts = title.split(' מאת ')
                        if len(parts) >= 2:
                            track_info['track'] = parts[0].strip()
                            artist_part = parts[1].split(' ב‑')[0].strip()
                            if 'artist' not in track_info:
                                track_info['artist'] = artist_part

                return track_info

        except Exception as e:
            print(f"Error fetching Apple Music track info: {e}")
            return {'url': link, 'error': str(e)}

    @classmethod
    def get_track_info(cls, link):
        """Synchronous wrapper for the async get_track_info method"""
        return asyncio.run(cls.get_track_info_async(link))


if __name__ == "__main__":
    link = "https://music.apple.com/il/album/centerfold/1452302453?i=1452302709"
    track_info = AppleMusicParser.get_track_info(link)
    print(f"Track: {track_info.get('track')}")
    print(f"Artist: {track_info.get('artist')}")
    print(f"Album: {track_info.get('album')}")
    print(f"All data: {track_info}")
