import os
from youtube_transcript_api import YoutubeTranscriptAPI
from yt_dlp import YoutubeDL
from openai import OpenAI
import chromadb
from dotenv import load_dotenv

load_dotenv()
OPEN_API_KEY = os.getenv("API_KEY")

client = OpenAI(api_key=os.environ["OPEN_API_KEY"])
chromadb = chromadb.Client()
collection = chroma.create_collection("youtube_channel")

def get_channel_video_ids(channel_url: str) -> list[str]:
    ydl_opts={
        'extract_flat' : True,
        'quiet' : True,
        'playlistend': 100
    }
    with YoutubeDL(ydl_opts) as ydl:
        info =  ydl.extract_info(channel_url, download=False)
        return [entry['id'] for entry in info ['entires']]