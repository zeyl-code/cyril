import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup
import settings
import os
import re


def spotify_init():
    spotify_client_id = settings.SPOTIFY_API_ID
    spotify_client_secret = settings.SPOTIFY_API_SECRET

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri="http://localhost:8080",
        )
    )

    return sp


def search_playlist(playlist_url):
    sp = spotify_init()
    playlist_id = re.search(r"/playlist/(\w+)", playlist_url).group(1)
    
    playlist_info = {}
    
    # Retrieve the playlist name
    playlist = sp.playlist(playlist_id)
    playlist_name = playlist["name"]
    
    offset = 0
    limit = 100  # Adjust the limit as needed (maximum is 100)
    
    while True:
        playlist = sp.playlist_tracks(playlist_id, offset=offset, limit=limit)
        tracks = playlist["items"]
        
        if not tracks:
            break  # No more tracks to fetch
        
        offset += limit
        
        for track in tracks:
            track_name = track["track"]["name"]
            
            # Remove parentheses and their contents from the track_name
            track_name = re.sub(r'\([^)]*\)', '', track_name).strip()
            
            artists = track["track"]["artists"]
            main_artist = artists[0]["name"]
            featuring_artists = [artist["name"] for artist in artists[1:]]
            length = track["track"]["duration_ms"] // 1000  # Song length in seconds
            global_plays = track["track"]["popularity"]
            
            song_info = {
                'song_title': track_name,
                'main_artist': main_artist,
                'featuring_artists': featuring_artists,
                'length': length,
                'global_plays': global_plays
            }
            
            if playlist_name not in playlist_info:
                playlist_info[playlist_name] = []
                
            playlist_info[playlist_name].append(song_info)
    
    return playlist_info




def get_lyrics(song_title, main_artist):
    artist_name_genius = main_artist
    song_title_genius = re.sub(r"\([^)]*\)", "", song_title).strip()
    song_url_genius = f"https://genius.com/{artist_name_genius.replace(' ', '-')}-{song_title_genius.replace(' ', '-')}-lyrics"

    response = requests.get(song_url_genius)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})
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
    punctuation_marks = [".", "?", "!"]
    lines = lyrics.split("\n")
    formatted_lines = []
    for line in lines:
        new_line = ""
        prev_char = ""
        within_parentheses = False
        for char in line:
            if char == "[":
                new_line += "\n\n" + char
            elif char == "]":
                new_line += char + "\n"
            elif char == "(":
                within_parentheses = True
                new_line += char
            elif char == ")":
                within_parentheses = False
                new_line += char
            elif char in punctuation_marks and prev_char not in [
                ",",
                "'",
                '"',
                ";",
                ":",
                "’",
            ]:
                if prev_char == "'" or (
                    prev_char.isalpha()
                    and prev_char.lower() in ["m", "r", "s"]
                    and char == "."
                ):
                    new_line += char
                elif char == "?" and prev_char == "'":
                    new_line += char + "\n"
                else:
                    new_line += char + "\n"
            elif (
                char.isalpha()
                and char.isupper()
                and prev_char.isalpha()
                and prev_char.lower() != "("
            ):
                new_line += "\n" + char
            elif within_parentheses and char.isupper() and prev_char == ")":
                new_line += "\n" + char
            else:
                new_line += char
            prev_char = char
        formatted_lines.append(new_line)
    formatted_lyrics = "\n".join(formatted_lines)
    return formatted_lyrics


# Example usage:
# playlist_url = input("Enter the Spotify playlist share URL: ")
# playlist_info = search_playlist(playlist_url)
# for song_info in playlist_info:
#     lyrics_list = get_lyrics(song_info['song_title'], song_info['main_artist'])
#     # Process lyrics and save them as needed.
