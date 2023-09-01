import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup
import settings
import os
import re

def get_lyrics(song_url):
    response = requests.get(song_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all div elements with the custom attribute
        lyrics_divs = soup.find_all('div', attrs={'data-lyrics-container': 'true'})
        
        if lyrics_divs:
            lyrics_list = []
            for lyrics_div in lyrics_divs:
                lyrics = lyrics_div.get_text()
                lyrics_list.append(lyrics.strip())
            return lyrics_list
        else:
            return ["Lyrics not found with the specified attribute."]
    else:
        return ["Failed to fetch page content."]

def format_lyrics(lyrics):
    # Define a list of punctuation marks to consider
    punctuation_marks = ['.', '?', '!']
    
    # Split lines and process each line
    lines = lyrics.split('\n')
    formatted_lines = []
    
    for line in lines:
        new_line = ''
        prev_char = ''
        within_parentheses = False
        
        for char in line:
            if char == '[':
                new_line += '\n\n' + char  # Add two new lines before a "["
            elif char == ']':
                new_line += char + '\n'
            elif char == '(':
                within_parentheses = True
                new_line += char
            elif char == ')':
                within_parentheses = False
                new_line += char
            elif char in punctuation_marks and prev_char not in [',', "'", '"', ';', ':', '`']:
                # Handle cases where punctuation is after a "'" or is part of abbreviations like Mr., Ms., Mrs.
                if prev_char == "'" or (prev_char.isalpha() and prev_char.lower() in ['m', 'r', 's'] and char == '.'):
                    new_line += char
                elif char == '?' and prev_char == "'":  # Handle '?' after "'"
                    new_line += char + '\n'
                else:
                    new_line += char + '\n'
            elif char.isalpha() and char.isupper() and prev_char.isalpha() and prev_char.lower() != '(':  # Add condition for capital letter after '('
                new_line += '\n' + char
            elif within_parentheses and char.isupper() and prev_char == ')':
                new_line += '\n' + char
            else:
                new_line += char
            prev_char = char
        
        formatted_lines.append(new_line)
    
    formatted_lyrics = '\n'.join(formatted_lines)
    return formatted_lyrics


# Replace with your Spotify client ID and client secret
spotify_client_id = settings.SPOTIFY_API_ID
spotify_client_secret = settings.SPOTIFY_API_SECRET

# Initialize the Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_client_id, client_secret=spotify_client_secret, redirect_uri="http://localhost:8080"))

# Prompt the user for the share URL
playlist_url = input("Enter the Spotify playlist share URL: ")

# Extract playlist ID from the URL
playlist_id = re.search(r'/playlist/(\w+)', playlist_url).group(1)

# Create a new folder for the files
output_folder = "lyric_files"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Retrieve playlist information
playlist = sp.playlist_tracks(playlist_id)
for track in playlist['items']:
    track_name = track['track']['name']
    artists = ", ".join(artist['name'] for artist in track['track']['artists'])
    print(f"Track: {track_name} | Artists: {artists}")
    
    # Use the first artist name for naming the file and searching for lyrics
    artist_name_genius = track['track']['artists'][0]['name']
    
    # Trim song title to remove additional artists in parentheses
    song_title_genius = re.sub(r'\([^)]*\)', '', track_name).strip()
    
    # Construct the Genius.com URL
    song_url_genius = f"https://genius.com/{artist_name_genius.replace(' ', '-')}-{song_title_genius.replace(' ', '-')}-lyrics"
    
    # Retrieve and format lyrics from Genius.com
    lyrics_list = get_lyrics(song_url_genius)
    if lyrics_list[0]:
        merged_lyrics = ""
        for idx, lyrics in enumerate(lyrics_list):
            formatted_lyrics = format_lyrics(lyrics)
            merged_lyrics += formatted_lyrics + "\n\n"  # Separate with two new lines
        
        filename = f"{artist_name_genius}_{song_title_genius}.txt"
        filepath = os.path.join(output_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(merged_lyrics)
            print(f"Lyrics saved to '{filepath}'")
    else:
        print("Lyrics not available or not found.")