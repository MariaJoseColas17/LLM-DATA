from pathlib import Path
import pandas as pd
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

PDFS_CSV = "SDLR.csv"
VIDEOS_CSV = "SDLR_yt_urls.csv"
OUT_OK = "SDLR RELACION.csv"
OUT_DROP = "no_match.csv"

DRIVE_FOLDER_ID = "1FiJMziz0pAJd_xhtkntVEm5MedvPG_TI"
CLIENT_SECRETS = "client_secrets.json"


def _norm_name(x: str) -> str:
    return Path(str(x)).name.strip().lower()


def get_drive_links(folder_id: str) -> dict:
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(CLIENT_SECRETS)
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    links = {}

    q = f"'{folder_id}' in parents and trashed=false"
    file_list = drive.ListFile({'q': q}).GetList()

    for f in file_list:
        title = str(f.get("title", ""))
        if not title.lower().endswith(".pdf"):
            continue

        try:
            f.InsertPermission({'type': 'anyone', 'value': '', 'role': 'reader'})
        except Exception:
            pass

        link = f.get("alternateLink", "")
        if link:
            links[_norm_name(title)] = link

    return links


def main():
    pdfs = pd.read_csv(PDFS_CSV, dtype=str)
    pdfs.columns = [c.strip() for c in pdfs.columns]

    if "fecha_contenido" not in pdfs.columns:
        raise SystemExit("El CSV de PDFs debe incluir la columna 'fecha_contenido'.")
    pdfs["fecha_contenido"] = pd.to_datetime(
        pdfs["fecha_contenido"], errors="coerce"
    ).dt.date

    if "nombre_documento" in pdfs.columns:
        pdfs["nombre_documento"] = pdfs["nombre_documento"].astype(str).str.strip()
    elif "local_path" in pdfs.columns:
        pdfs["nombre_documento"] = pdfs["local_path"].apply(lambda p: Path(str(p)).name)
    else:
        raise SystemExit("El CSV de PDFs debe tener 'nombre_documento' o 'local_path'.")

    v = pd.read_csv(VIDEOS_CSV, header=None, dtype=str, encoding="utf-8-sig")
    if v.shape[1] < 3:
        raise SystemExit("El CSV de videos debe tener 3 columnas: titulo, fecha, url (SIN header).")
    v = v.iloc[:, :3]
    v.columns = ["titulo_video", "fecha_publicacion", "url_youtube"]

    v["fecha_publicacion"] = pd.to_datetime(
        v["fecha_publicacion"], format="%Y-%m-%d", errors="coerce"
    ).dt.date

    m = pdfs.merge(v, left_on="fecha_contenido", right_on="fecha_publicacion", how="left")

    print("🔎 Listando PDFs en Drive…")
    drive_links_raw = get_drive_links(DRIVE_FOLDER_ID)
    drive_links = {k: v for k, v in drive_links_raw.items()}  # ya vienen normalizados

    m["link_pdf"] = m["nombre_documento"].map(lambda x: drive_links.get(_norm_name(x), ""))

    tabla = (
        m[["nombre_documento", "link_pdf", "url_youtube", "fecha_contenido"]]
        .rename(columns={"url_youtube": "enlace_youtube"})
    )

    con_enlace = tabla[tabla["enlace_youtube"].notna() & (tabla["enlace_youtube"].str.strip() != "")]
    sin_enlace = tabla[~tabla.index.isin(con_enlace.index)]

    con_enlace[["nombre_documento", "link_pdf", "enlace_youtube"]].to_csv(
        OUT_OK, index=False, encoding="utf-8-sig"
    )
    sin_enlace[["nombre_documento", "fecha_contenido"]].to_csv(
        OUT_DROP, index=False, encoding="utf-8-sig"
    )

    print(f"✅ Guardado: {OUT_OK} (filas con video: {len(con_enlace)})")
    print(f"📝 Sin match (revisar): {OUT_DROP} (filas: {len(sin_enlace)})")


if __name__ == "__main__":
    main()
