import os
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
from openai import OpenAI
import chromadb
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Check .env file.")
client = OpenAI(api_key=OPENAI_API_KEY)

chroma_client = chromadb.Client()
collection = chroma_client.create_collection("youtube_channel")

def get_channel_video_ids(channel_url: str) -> list[str]:
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'playlistend': 100
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        entries = info.get('entries', [])
        return [entry['id'] for entry in entries if entry]

def get_transcript(video_id: str):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk['text'] for chunk in transcript])
    except Exception as e:
        print(f"Transcript error for {video_id}: {e}")
        return None

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        model="text_embedding-3-small",
        input=text
    )
    return response.data[0].embedding