from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Spotify Downloader API")

# Allow all origins (WordPress or other frontend can call)
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
    """
    Input: Spotify track or playlist URL
    Output: JSON with download_url and title
    """
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    # Step 1: Visit Spotdown homepage
    session.get("https://spotdown.org")

    # Step 2: Check metadata
    check_api = "https://spotdown.org/api/check-direct-download"
    res = session.get(check_api, params={"url": url}, headers={"Referer": "https://spotdown.org/"})

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch metadata")

    data = res.json()
    type_field = data.get("type", "").lower()

    # ---------------- Single track ----------------
    if type_field in ["track", "song", "single"]:
        download_url = data.get("url")
        title = data.get("title", "song")
        if not download_url:
            raise HTTPException(status_code=400, detail="Download URL not found")
        return {"download_url": download_url, "title": title}

    # ---------------- Playlist ----------------
    elif type_field in ["playlist", "playlist_track"]:
        tracks = data.get("tracks", [])
        if not tracks:
            raise HTTPException(status_code=400, detail="No tracks found in playlist")

        # Return first track only (can be extended later)
        first_track = tracks[0]
        download_url = first_track.get("url")
        title = first_track.get("title", "song")
        if not download_url:
            raise HTTPException(status_code=400, detail="Download URL not found")
        return {"download_url": download_url, "title": title}

    # ---------------- Unknown type ----------------
    else:
        raise HTTPException(status_code=400, detail=f"Invalid type: {type_field}")
