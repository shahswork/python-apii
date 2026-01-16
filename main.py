from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import requests
import io

app = FastAPI()

@app.get("/download")
def download_spotify(url: str):
    session = requests.Session()

    session.get("https://spotdown.org", headers={"User-Agent": "Mozilla/5.0"})

    check_api = "https://spotdown.org/api/check-direct-download"
    meta = session.get(
        check_api,
        params={"url": url},
        headers={"Referer": "https://spotdown.org/"}
    ).json()

    song_url = meta.get("url")
    title = meta.get("title", "song")

    download_api = "https://spotdown.org/api/download"
    r = session.post(
        download_api,
        json={"url": song_url},
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://spotdown.org/",
            "Content-Type": "application/json"
        },
        stream=True
    )

    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Download failed")

    return StreamingResponse(
        r.iter_content(8192),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f'attachment; filename="{title}.mp3"'
        }
    )
