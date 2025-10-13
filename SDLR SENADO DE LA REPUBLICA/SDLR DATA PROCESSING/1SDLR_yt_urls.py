import re
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime

API_KEY = "AIzaSyCkZfpwB3lc-PJ5Dog_YIWDBahhfvrGTOg"

PLAYLIST_IDS = [
    "PLLamNSgCzGXkngGQUUWUaoOQPjAxjtcie",
    "PLLamNSgCzGXkFqDzZNnADHLot0xPdDXXr",
    "PLLamNSgCzGXlCl_hxd1sMxXko4_EPEx0e",
    "PLLamNSgCzGXla-ECG14lRCMuGy46RaXL8",
    "PLLamNSgCzGXmSs51noHQ9lAKFG-bnJ9Wd",
]

OUT_CSV = "SDLR_yt_urls.csv"

pat = re.compile(
    r"(?i)"  
    r"(?:transmi(?:sión|sion)?\s+en\s+vivo.*?ses[ií]on\s*(?:no\.?\s*)?\d{1,4})"
    r"|"
    r"(?:ses[ií]on\s+(?:ordinaria|extraordinaria)\s*(?:no\.?\s*)?\d{1,4})"
)

fecha_pat = re.compile(
    r"(\d{1,2})\s+(?:de\s+)?(ene(?:ro)?|feb(?:rero)?|mar(?:zo)?|abr(?:il)?|may(?:o)?|jun(?:io)?|jul(?:io)?|ago(?:sto)?|sep(?:tiembre)?|oct(?:ubre)?|nov(?:iembre)?|dic(?:iembre)?)\s+(?:de\s+)?(\d{4})",
    re.IGNORECASE
)
meses_es = {
    'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 'may': 'May', 'jun': 'Jun',
    'jul': 'Jul', 'ago': 'Aug', 'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
}


def extract_session_date(title, published_at):

    match_fecha = fecha_pat.search(title)

    if match_fecha:
        day, month_es, year = match_fecha.groups()


        month_key = next((k for k in meses_es.keys() if month_es.lower().startswith(k)), None)

        if month_key:
            month_en = meses_es[month_key]
            date_str_en = f"{day} {month_en} {year}"

            try:

                date_obj = datetime.strptime(date_str_en, '%d %b %Y')
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass

    # Respaldo: Usar la fecha de publicación de YouTube (fecha de subida)
    return published_at[:10] if published_at else ""


# --- PROCESAMIENTO PRINCIPAL ---

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

            vid = sn["resourceId"]["videoId"]
            if vid in seen:
                continue
            seen.add(vid)

            published_at = sn.get("publishedAt", "")
            fecha_sesion = extract_session_date(title, published_at)

            rows.append({
                "titulo_youtube": title,
                "fecha_sesion": fecha_sesion,
                "url_youtube": f"https://www.youtube.com/watch?v={vid}"
            })

        token = resp.get("nextPageToken")
        if not token:
            break

pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
print(f"OK -> {OUT_CSV} ({len(rows)} videos, {len(PLAYLIST_IDS)} playlists)")