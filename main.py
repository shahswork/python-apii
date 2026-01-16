from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Spotify Downloader API")

# Allow all origins (WordPress/front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Spotify downloader API running"}

@app.get("/download")
def download_spotify(url: str):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    # Step 1: Visit homepage
    session.get("https://spotdown.org")

    # Step 2: Metadata check
    check_api = "https://spotdown.org/api/check-direct-download"
    res = session.get(check_api, params={"url": url}, headers={"Referer": "https://spotdown.org/"})

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch metadata")

    data = res.json()

    # Try multiple ways to get download URL
    download_url = None
    title = "song"

    # Case 1: Direct URL
    if "url" in data:
        download_url = data["url"]
        title = data.get("title", "song")

    # Case 2: Playlist / tracks array
    elif "tracks" in data and isinstance(data["tracks"], list) and len(data["tracks"]) > 0:
        first_track = data["tracks"][0]
        download_url = first_track.get("url")
        title = first_track.get("title", "song")

    # Case 3: Fallback - check keys
    elif "download_url" in data:
        download_url = data["download_url"]
        title = data.get("title", "song")

    if not download_url:
        raise HTTPException(status_code=400, detail="Download URL not found")

    return {"download_url": download_url, "title": title}
