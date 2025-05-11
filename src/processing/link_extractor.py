import re
from datetime import datetime
from src.cache_manager.file_manager import file_manager
from src.cache_manager.file_constants import MUSIC_LINKS_CSV, CHAT_EXPORT

def clean_link(link):
    """Clean up a link by removing trailing punctuation or text"""
    # Remove closing quotes, parentheses, or other trailing characters
    for char in ['"', "'", ')', ']', '>', ',']:
        if char in link:
            link = link.split(char)[0]
    return link

def extract_links_from_content(content: str):
    """
    Extracts music.apple.com and open.spotify.com links from text content
    along with their associated dates.
    """
    apple_pattern = r'https://music\.apple\.com/\S+'
    spotify_pattern = r'https://open\.spotify\.com/\S+'
    date_pattern = r'\[(\d{2}/\d{2}/\d{4})[^\]]*\]'

    lines = content.split('\n')
    all_links_with_dates = []
    current_date = None

    for line in lines:
        date_match = re.search(date_pattern, line)
        if date_match:
            current_date = date_match.group(1)

        if not current_date:
            continue

        apple_matches = re.findall(apple_pattern, line)
        for link_match in apple_matches:
            all_links_with_dates.append((clean_link(link_match), "Apple Music", current_date))

        spotify_matches = re.findall(spotify_pattern, line)
        for link_match in spotify_matches:
            all_links_with_dates.append((clean_link(link_match), "Spotify", current_date))
            
    return all_links_with_dates

def _deduplicate_links_by_date(raw_links: list):
    """
    Removes duplicate links, keeping the one with the earliest date.
    """
    unique_links = {}
    for link, platform, date_str in raw_links:
        if link in unique_links:
            existing_date_str = unique_links[link][2]
            # Convert dates to datetime objects for comparison
            current_date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            existing_date_obj = datetime.strptime(existing_date_str, '%d/%m/%Y')
            
            # Keep the earlier date
            if current_date_obj < existing_date_obj:
                unique_links[link] = (link, platform, date_str)
        else:
            unique_links[link] = (link, platform, date_str)
    return list(unique_links.values())

def _save_links_to_csv_and_report(unique_links: list, raw_link_count: int, output_path: str):
    """
    Saves the unique links to a CSV file and prints a report.
    """
    # Count by platform
    apple_count = sum(1 for _, platform, _ in unique_links if platform == "Apple Music")
    spotify_count = sum(1 for _, platform, _ in unique_links if platform == "Spotify")
    
    try:
        csv_data = [['Link', 'Platform', 'Date']]  # Header
        csv_data.extend(unique_links)
        file_manager.write_csv(output_path, csv_data[1:], header=csv_data[0])
        
        print(f"Successfully extracted {len(unique_links)} unique links to {output_path}")
        print(f"- Apple Music: {apple_count}")
        print(f"- Spotify: {spotify_count}")
        print(f"- Duplicates removed: {raw_link_count - len(unique_links)}")
        return True
    except Exception as e:
        print(f"Error writing CSV: {e}")
        return False

def extract_music_links():
    """
    Extract music.apple.com and open.spotify.com links from the CHAT_EXPORT file,
    deduplicates them by earliest date, and saves them to a CSV file.
    """
    try:
        content = file_manager.read_text(CHAT_EXPORT)
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    raw_links = extract_links_from_content(content)
    if not raw_links: # Check if the list is empty
        print("No links found in the content.")
        return None

    unique_links = _deduplicate_links_by_date(raw_links)
    
    if _save_links_to_csv_and_report(unique_links, len(raw_links), MUSIC_LINKS_CSV):
        return MUSIC_LINKS_CSV
    else:
        return None

if __name__ == "__main__":
    if not file_manager.file_exists(CHAT_EXPORT):
        print(f"File not found: {CHAT_EXPORT}")
    else:
        output_file = extract_music_links()
        if output_file:
            pass 