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

def get_embeddings(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model="text_embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]

def index_chanel (chanel_url: str):
    print(f"Fetching video IDs from {chanel_url}...")
    video_ids = get_channel_video_ids(chanel_url)
    print(f"Found {len(video_ids)} videos")

    indexed = 0
    for video_id in video_ids:
        print(f"Processing video {video_id}...")
        transcript = get_transcript(video_id)
        if transcript:
            continue

        chunks = chunk_text(transcript)
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"{video_id}_chunk_{i}"],
                metadatas=[{"video_id": video_id,
                            "url": f"https://www.youtube.com/watch?v={video_id}"}]
            )
            indexed += 1
            print(f" Indexed Video {indexed}/{len(video_ids)}: {video_id}")
            print(f" Indexed {indexed} videos successfully")