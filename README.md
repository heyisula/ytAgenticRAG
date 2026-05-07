<div align="center">

# 🎬 ytAgenticRAG

**Ask anything about a YouTube channel — powered by RAG + GPT-4o**

[![Status](https://img.shields.io/badge/status-ongoing-orange?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/heyisula/ytAgenticRAG)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o%20%7C%20Whisper-412991?style=for-the-badge&logo=openai&logoColor=white)](https://platform.openai.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6B35?style=for-the-badge&logo=databricks&logoColor=white)](https://www.trychroma.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

> ⚠️ **This project is actively under development.** Features, APIs, and behaviour may change without notice.

</div>

---

## 📖 Overview

**ytAgenticRAG** is an agentic Retrieval-Augmented Generation (RAG) system that lets you **query the entire transcript corpus of any YouTube channel** using natural language. Point it at a channel URL, and the pipeline automatically:

1. **Scrapes** the latest video IDs from the channel using `yt-dlp`
2. **Fetches** English transcripts via `youtube-transcript-api` (with authenticated cookie support)
3. **Falls back** to OpenAI Whisper audio transcription when captions are unavailable
4. **Chunks & embeds** transcripts with `text-embedding-ada-002` into a ChromaDB vector store
5. **Answers questions** using GPT-4o-mini with source attribution back to the original videos

---

## 🏗️ Architecture

```
YouTube Channel URL
        │
        ▼
┌───────────────────┐
│   yt-dlp          │  ← Extracts video IDs (flat playlist)
└────────┬──────────┘
         │
         ▼
┌───────────────────────────────────────────────┐
│              Transcript Pipeline               │
│                                               │
│  1. YouTubeTranscriptApi (with cookies)       │
│     └── Retry w/ exponential backoff          │
│  2. Fallback: yt-dlp audio + Whisper-1        │
└────────┬──────────────────────────────────────┘
         │
         ▼
┌───────────────────┐      ┌──────────────────────────┐
│  Text Chunker     │─────▶│  OpenAI Embeddings        │
│  (400w / 50 ovlp) │      │  text-embedding-ada-002   │
└───────────────────┘      └────────────┬─────────────┘
                                        │
                                        ▼
                           ┌──────────────────────────┐
                           │  ChromaDB Vector Store    │
                           │  (in-memory collection)   │
                           └────────────┬─────────────┘
                                        │
                           ┌────────────▼─────────────┐
                           │  GPT-4o-mini (RAG query)  │
                           │  Top-5 chunk retrieval    │
                           │  + source video URLs      │
                           └──────────────────────────┘
```

---

## 📁 Project Structure

```
ytAgenticRAG/
├── app.py                  # Core pipeline: indexing + RAG query engine
├── get_cookies.py          # Automated cookie extraction via Selenium (Edge)
├── get_cookies_manual.py   # Manual cookie extraction via DevTools copy-paste
├── cookies.txt             # Netscape-format YouTube session cookies (gitignored)
├── .env                    # Environment variables (API keys)
├── .gitignore
└── LICENSE
```

### File Breakdown

| File | Purpose |
|---|---|
| [`app.py`](app.py) | Main entry point. Indexes a YouTube channel and runs Q&A against it. |
| [`get_cookies.py`](get_cookies.py) | Launches Microsoft Edge via Selenium in stealth mode, prompts manual login, then exports authenticated session cookies to `cookies.txt` in Netscape format. |
| [`get_cookies_manual.py`](get_cookies_manual.py) | No-extension alternative. Guides the user to copy raw cookie headers from DevTools and converts them to `cookies.txt`. Useful when automated login is blocked. |
| `cookies.txt` | Netscape HTTP cookie file passed to `yt-dlp` and `youtube-transcript-api` to bypass age-restricted or rate-limited content. |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- Microsoft Edge (for `get_cookies.py`) **or** any browser with DevTools (for `get_cookies_manual.py`)

### 1. Clone the repo

```bash
git clone https://github.com/heyisula/ytAgenticRAG.git
cd ytAgenticRAG
```

### 2. Install dependencies

```bash
pip install openai chromadb yt-dlp youtube-transcript-api python-dotenv requests selenium
```

### 3. Configure environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-key-here
```

### 4. Extract YouTube cookies (recommended)

Cookies are required for reliable transcript access, especially for age-restricted or heavily rate-limited channels.

**Option A — Automated (Selenium + Edge):**
```bash
python get_cookies.py
```
A browser window will open. Sign into your Google account, then press `ENTER` in the terminal.

**Option B — Manual (DevTools copy-paste):**
```bash
python get_cookies_manual.py
```
Follow the on-screen instructions to copy your cookie header from the browser's Network tab.

### 5. Run the pipeline

Edit the channel URL and query at the bottom of `app.py`, then run:

```bash
python app.py
```

**Example output:**
```
Fetching video IDs from https://www.youtube.com/@TechWithTim/videos...
Found 5 videos
Processing video abc123...
Indexed video 1/5: abc123
...
Answer: The best way to learn Python according to Tim is to build real projects...
Sources: ['https://www.youtube.com/watch?v=abc123', ...]
```

---

## ⚙️ Configuration

| Parameter | Location | Default | Description |
|---|---|---|---|
| `playlistend` | `app.py:27` | `5` | Number of latest videos to index |
| `chunk_size` | `app.py:91` | `400` | Words per transcript chunk |
| `overlap` | `app.py:91` | `50` | Word overlap between chunks |
| `n_results` | `app.py:150` | `5` | Top-k chunks retrieved per query |
| `languages` | `app.py:58` | `['en']` | Preferred transcript language |
| `model` (chat) | `app.py:168` | `gpt-4o-mini` | OpenAI chat model |
| `model` (embed) | `app.py:102` | `text-embedding-ada-002` | OpenAI embedding model |

---

## 🛣️ Roadmap

> This project is **actively being developed**. Planned features include:

- [ ] **Persistent vector store** — swap in-memory ChromaDB for disk-backed persistence
- [ ] **Multi-language support** — auto-detect and index non-English transcripts
- [ ] **CLI interface** — interactive command-line Q&A session
- [ ] **Web UI** — Streamlit/Gradio front-end for non-technical users
- [ ] **Agentic loop** — tool-calling agent that can search, re-rank, and reason over multiple channels
- [ ] **Caching layer** — avoid re-indexing already-processed videos
- [ ] **Docker support** — containerized deployment

---

## 🔑 Cookie Authentication

YouTube aggressively rate-limits transcript access. This project includes two cookie extraction strategies to maintain reliable access:

| Method | Script | When to use |
|---|---|---|
| **Selenium (auto)** | `get_cookies.py` | Preferred method. Launches a real browser in stealth mode to bypass anti-bot detection. |
| **DevTools (manual)** | `get_cookies_manual.py` | Fallback when Google blocks automated browser login. No extensions needed. |

The exported `cookies.txt` uses the standard **Netscape cookie format** compatible with both `yt-dlp` and `youtube-transcript-api`.

---

## ⚠️ Disclaimer

This tool is intended for **personal, educational, and research use only**. Usage must comply with [YouTube's Terms of Service](https://www.youtube.com/t/terms). The authors are not responsible for any misuse.

---

## 📄 License

Copyright © 2026 **Isula Dissanayake** — Released under the [MIT License](LICENSE).

---

<div align="center">

Made with ❤️ by [heyisula](https://github.com/heyisula)

</div>
