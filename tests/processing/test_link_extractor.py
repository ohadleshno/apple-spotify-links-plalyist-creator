import pytest
from unittest.mock import patch, mock_open
from src.processing.link_extractor import clean_link, extract_links_from_content, extract_music_links
from src.cache_manager.file_constants import CHAT_EXPORT, MUSIC_LINKS_CSV


# Tests for clean_link
def test_clean_link_no_cleaning_needed():
    assert clean_link("http://example.com/path") == "http://example.com/path"


def test_clean_link_with_trailing_quote():
    assert clean_link("http://example.com/path'''") == "http://example.com/path"


def test_clean_link_with_trailing_parenthesis():
    assert clean_link("http://example.com/path)") == "http://example.com/path"


def test_clean_link_with_trailing_bracket():
    assert clean_link("http://example.com/path]") == "http://example.com/path"


def test_clean_link_with_trailing_comma():
    assert clean_link("http://example.com/path,") == "http://example.com/path"


def test_clean_link_with_mixed_trailing_chars():
    assert clean_link("http://example.com/path),'''") == "http://example.com/path"


def test_extract_links_from_content_empty():
    assert extract_links_from_content("") == []


def test_extract_links_from_content_no_links():
    content = "[10/10/2023, 10:00:00] User: Hello world\nNo links here."
    assert extract_links_from_content(content) == []


def test_extract_links_from_content_only_apple_music():
    content = "[10/10/2023, 10:00:00] User: Check this https://music.apple.com/us/album/song/123"
    expected = [("https://music.apple.com/us/album/song/123", "Apple Music", "10/10/2023")]
    assert extract_links_from_content(content) == expected


def test_extract_links_from_content_only_spotify():
    content = "[11/11/2023, 11:00:00] User: Listen to https://open.spotify.com/track/456"
    expected = [("https://open.spotify.com/track/456", "Spotify", "11/11/2023")]
    assert extract_links_from_content(content) == expected


def test_extract_links_from_content_mixed_links():
    content = """
[10/10/2023, 10:00:00] User1: Apple song https://music.apple.com/us/album/song/123
[10/10/2023, 10:05:00] User2: Spotify one https://open.spotify.com/track/456 next to apple https://music.apple.com/us/album/another/789
[11/11/2023, 11:00:00] User1: Old link, but new date context https://music.apple.com/us/album/song/123
    """
    expected = [
        ("https://music.apple.com/us/album/song/123", "Apple Music", "10/10/2023"),
        ("https://music.apple.com/us/album/another/789", "Apple Music", "10/10/2023"),
        ("https://open.spotify.com/track/456", "Spotify", "10/10/2023"),
        ("https://music.apple.com/us/album/song/123", "Apple Music", "11/11/2023")
    ]
    assert extract_links_from_content(content) == expected


def test_extract_links_from_content_links_need_cleaning():
    content = "[12/12/2023, 12:00:00] User: https://music.apple.com/us/album/song/123), some text"
    expected = [("https://music.apple.com/us/album/song/123", "Apple Music", "12/12/2023")]
    assert extract_links_from_content(content) == expected


def test_extract_links_from_content_no_date_context():
    content = "User: https://music.apple.com/us/album/song/123"
    assert extract_links_from_content(content) == []


def test_extract_links_from_content_date_after_link():
    content = "User: https://music.apple.com/us/album/song/123 [12/12/2023, 12:00:00]"
    expected = [("https://music.apple.com/us/album/song/123", "Apple Music", "12/12/2023")]
    assert extract_links_from_content(content) == expected


@patch('src.processing.link_extractor.file_manager.read_text')
@patch('src.processing.link_extractor.file_manager.write_csv')
def test_extract_music_links_success(mock_write_csv, mock_read_text):
    mock_content = """
[01/01/2023, 10:00:00] msg1: https://music.apple.com/a/1
[01/01/2023, 10:00:00] msg2: https://open.spotify.com/s/1
[02/01/2023, 10:00:00] msg3: https://music.apple.com/a/1
[03/01/2023, 10:00:00] msg4: https://music.apple.com/a/2
    """
    mock_read_text.return_value = mock_content

    result = extract_music_links()

    assert result == MUSIC_LINKS_CSV
    mock_read_text.assert_called_once_with(CHAT_EXPORT)

    args, kwargs = mock_write_csv.call_args
    assert args[0] == MUSIC_LINKS_CSV

    written_data = args[1]
    written_data_sorted = sorted(written_data, key=lambda x: x[0])
    expected_data_sorted = sorted([
        ('https://music.apple.com/a/1', 'Apple Music', '01/01/2023'),
        ('https://open.spotify.com/s/1', 'Spotify', '01/01/2023'),
        ('https://music.apple.com/a/2', 'Apple Music', '03/01/2023')
    ], key=lambda x: x[0])

    assert written_data_sorted == expected_data_sorted
    assert kwargs['header'] == ['Link', 'Platform', 'Date']


@patch('src.processing.link_extractor.file_manager.read_text')
def test_extract_music_links_read_error(mock_read_text):
    mock_read_text.side_effect = Exception("File read error")
    assert extract_music_links() is None


@patch('src.processing.link_extractor.file_manager.read_text')
@patch('src.processing.link_extractor.file_manager.write_csv')
def test_extract_music_links_write_error(mock_write_csv, mock_read_text):
    mock_read_text.return_value = "[01/01/2023, 10:00:00] msg1: https://music.apple.com/a/1"
    mock_write_csv.side_effect = Exception("CSV write error")
    assert extract_music_links() is None


@patch('src.processing.link_extractor.file_manager.read_text')
def test_extract_music_links_no_links_in_file(mock_read_text):
    mock_read_text.return_value = "[01/01/2023, 10:00:00] msg1: Just text, no links."
    assert extract_music_links() is None
    mock_read_text.assert_called_once_with(CHAT_EXPORT)
