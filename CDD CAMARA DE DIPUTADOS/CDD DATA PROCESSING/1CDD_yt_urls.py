import re, pandas as pd
from googleapiclient.discovery import build

API_KEY = "AIzaSyDTMP0f1Jdd7yHuGy_6gT82OJThnldvydU"

PLAYLIST_IDS = [
    "PLhmHTNWPNuNf9Yg0Ecf7aFNtvgFcIHPZd"

]

OUT_CSV = "CDD_yt_urls.csv"


pat = re.compile(
    r"\b(?:primera|1ra|i)\b.*\blegislatura\b.*\b(?:ordinaria|extraordinaria)\b"
    r"|"
    r"\b(?:segunda|2da|ii)\b.*\blegislatura\b.*\b(?:ordinaria|extraordinaria)\b",
    re.IGNORECASE
)

yt = build("youtube", "v3", developerKey=API_KEY)

rows = []
seen = set()

for plist in PLAYLIST_IDS:
    token = None
    while True:
        resp = yt.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=plist,
            maxResults=50,
            pageToken=token
        ).execute()

        for it in resp.get("items", []):
            sn = it["snippet"]
            title = sn.get("title") or ""
            if not pat.search(title):
                continue

            vid = sn["resourceId"]["videoId"]
            if vid in seen:
                continue
            seen.add(vid)

            published = sn.get("publishedAt", "")[:10]  # AAAA-MM-DD
            rows.append({
                "titulo_youtube": title,
                "fecha_sesion": published,
                "url_youtube": f"https://www.youtube.com/watch?v={vid}"
            })

        token = resp.get("nextPageToken")
        if not token:
            break

pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
print(f"OK -> {OUT_CSV} ({len(rows)} videos, {len(PLAYLIST_IDS)} playlists)")
