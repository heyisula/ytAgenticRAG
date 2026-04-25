import sys
import youtube_transcript_api
from typing import Any
import time
import random
import os
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
from openai import OpenAI
import chromadb
from dotenv import load_dotenv
print("Python executable:", sys.executable)
print("Transcript API location:", youtube_transcript_api.__file__)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Check .env file.")
client = OpenAI(api_key=OPENAI_API_KEY)

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("youtube_channel")
def get_channel_video_ids(channel_url: str) -> list[str]:
    ydl_opts: dict[str, Any] = {
        'extract_flat': True,
        'quiet': True,
        'playlistend': 5,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0'
        }
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        entries = info.get('entries', [])
        return [entry['id'] for entry in entries if entry]

def get_transcript(video_id: str, retries=3):
    cookies_file = "cookies.txt" if os.path.exists("cookies.txt") else None
    
    for attempt in range(retries):
        try:
            if cookies_file:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, cookies=cookies_file)
            else:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([chunk['text'] for chunk in transcript])
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {video_id}: {e}")
            sleep_time = (2 ** attempt) + random.uniform(2, 5)  # longer backoff
            time.sleep(sleep_time)
    return None

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def get_embeddings(texts: list[str]) -> list[Any]:
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [item.embedding for item in response.data]

def index_chanel (chanel_url: str):
    print(f"Fetching video IDs from {chanel_url}...")
    video_ids = get_channel_video_ids(chanel_url)
    print(f"Found {len(video_ids)} videos")

    video_count = 0
    chunk_count = 0

    for video_id in video_ids:
        print(f"Processing video {video_id}...")
        transcript = get_transcript(video_id)
        if not transcript:
            continue

        chunks = chunk_text(transcript)
        embeddings = get_embeddings(chunks)
        ids = [f"{video_id}_chunk_{i}" for i in range(len(chunks))]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=[
                {
                    "video_id": video_id,
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                }
                for _ in chunks
            ]
        )

        video_count += 1
        chunk_count += len(chunks)

        print(f"Indexed video {video_count}/{len(video_ids)}: {video_id}")
    
    print(f"\nDone. Indexed {video_count} videos and {chunk_count} chunks.")

def query_channel(question: str) -> dict:
    q_embedding = get_embeddings([question])[0]

    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=5
    )

    docs = results.get("documents")
    context = "\n\n".join(docs[0]) if docs and docs[0] else ""

    metas = results.get("metadatas")
    sources = [str(m.get("url")) for m in metas[0] if m] if metas and metas[0] else []

    prompt = f"""Answer the question using ONLY the youtube transcript context below. Include which video(s) the answer came from.

Context:
{context}

Question: {question}
Answer:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": list(set(sources))
    }


# Testing
index_chanel("https://www.youtube.com/@TechWithTim/videos")
result = query_channel("What is the best way to learn Python?")

print("Answer:", result["answer"])
print("Sources:", result["sources"])