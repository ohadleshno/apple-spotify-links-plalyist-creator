import re
import csv
import os
from datetime import datetime

def extract_music_links(filepath):
    """
    Extract music.apple.com and open.spotify.com links from a text file
    and save them to a CSV file with date information.
    """
    # Define regex patterns for the links
    apple_pattern = r'https://music\.apple\.com/\S+'
    spotify_pattern = r'https://open\.spotify\.com/\S+'
    
    # Date pattern - looking for [DD/MM/YYYY, HH:MM:SS] format
    date_pattern = r'\[(\d{2}/\d{2}/\d{4})[^\]]*\]'
    
    # Read the file
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    # Split content by lines to process dates and links together
    lines = content.split('\n')
    
    all_links_with_dates = []
    current_date = None
    
    for line in lines:
        # Check if line contains date
        date_match = re.search(date_pattern, line)
        if date_match:
            current_date = date_match.group(1)
        
        if not current_date:
            continue  # Skip lines without a date context
        
        # Extract Apple Music links
        apple_matches = re.findall(apple_pattern, line)
        for link in apple_matches:
            all_links_with_dates.append((clean_link(link), "Apple Music", current_date))
        
        # Extract Spotify links
        spotify_matches = re.findall(spotify_pattern, line)
        for link in spotify_matches:
            all_links_with_dates.append((clean_link(link), "Spotify", current_date))
    
    # Remove duplicates but keep earliest date
    unique_links = {}
    for link, platform, date in all_links_with_dates:
        if link in unique_links:
            existing_date = unique_links[link][2]
            # Convert dates to datetime objects for comparison
            current_date_obj = datetime.strptime(date, '%d/%m/%Y')
            existing_date_obj = datetime.strptime(existing_date, '%d/%m/%Y')
            
            # Keep the earlier date
            if current_date_obj < existing_date_obj:
                unique_links[link] = (link, platform, date)
        else:
            unique_links[link] = (link, platform, date)
    
    # Convert unique_links dictionary values back to a list
    all_unique_links = list(unique_links.values())
    
    # Count by platform
    apple_count = sum(1 for _, platform, _ in all_unique_links if platform == "Apple Music")
    spotify_count = sum(1 for _, platform, _ in all_unique_links if platform == "Spotify")
    
    # Save to CSV
    output_file = "../music_links.csv"
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Link', 'Platform', 'Date'])
            writer.writerows(all_unique_links)
        
        print(f"Successfully extracted {len(all_unique_links)} unique links to {output_file}")
        print(f"- Apple Music: {apple_count}")
        print(f"- Spotify: {spotify_count}")
        print(f"- Duplicates removed: {len(all_links_with_dates) - len(all_unique_links)}")
        return output_file
    except Exception as e:
        print(f"Error writing CSV: {e}")
        return None

def clean_link(link):
    """Clean up a link by removing trailing punctuation or text"""
    # Remove closing quotes, parentheses, or other trailing characters
    for char in ['"', "'", ')', ']', '>', ',']:
        if char in link:
            link = link.split(char)[0]
    return link

if __name__ == "__main__":
    chat_file = "../_chat.txt"
    
    if not os.path.exists(chat_file):
        print(f"File not found: {chat_file}")
    else:
        output_file = extract_music_links(chat_file)
        if output_file:
            print(f"CSV file created: {output_file}") 