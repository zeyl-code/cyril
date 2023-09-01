from dotenv import load_dotenv
import os

load_dotenv()

SPOTIFY_API_ID = os.getenv("SPOTIFY_API_ID")
SPOTIFY_API_SECRET = os.getenv("SPOTIFY_API_SECRET")