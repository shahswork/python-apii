from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

@app.get("/download")
def download_spotify(url: str):
    session = requests.Session()
    session.get("https://spotdown.org", headers={"User-Agent": "Mozilla/5.0"})

    check_api = "https://spotdown.org/api/check-direct-download"
    res = session.get(check_api, params={"url": url}, headers={"Referer": "https://spotdown.org/"})

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch metadata")

    data = res.json()

    # Single track
    if data.get("type") == "track":
        download_url = data.get("url")  # check exact field
        title = data.get("title", "song")
    # Playlist
    elif data.get("type") == "playlist":
        tracks = data.get("tracks", [])
        if not tracks:
            raise HTTPException(status_code=400, detail="No tracks found")
        download_url = tracks[0].get("url")
        title = tracks[0].get("title", "song")
    else:
        raise HTTPException(status_code=400, detail="Invalid type")

    if not download_url:
        raise HTTPException(status_code=400, detail="Download URL not found")

    return {"download_url": download_url, "title": title}
