from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"status": "Spotify downloader API running"}


@app.get("/download")
def download_spotify(url: str):
    session = requests.Session()

    # STEP 1: Visit homepage
    session.get(
        "https://spotdown.org",
        headers={"User-Agent": "Mozilla/5.0"}
    )

    # STEP 2: Metadata API
    check_api = "https://spotdown.org/api/check-direct-download"

    check_res = session.get(
        check_api,
        params={"url": url},
        headers={
            "Referer": "https://spotdown.org/",
            "Accept": "application/json"
        }
    )

    if check_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch metadata")

    data = check_res.json()

    # Playlist or single
    if data.get("type") == "playlist":
        songs = data.get("tracks", [])
    else:
        songs = [data]

    downloaded_files = []

    # STEP 3: Download
    for song in songs:
        title = song.get("title", "unknown")
        artist = song.get("artist", "")
        safe_name = f"{title} - {artist}".replace("/", "-").replace("\\", "-").strip() + ".mp3"
        file_path = os.path.join(DOWNLOAD_DIR, safe_name)

        download_api = "https://spotdown.org/api/download"
        payload = {"url": song.get("url", url)}

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://spotdown.org/",
            "Origin": "https://spotdown.org",
            "Content-Type": "application/json"
        }

        response = session.post(download_api, json=payload, headers=headers, stream=True)

        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)

            downloaded_files.append(safe_name)

    return {
        "status": "success",
        "total_files": len(downloaded_files),
        "files": downloaded_files
    }
