LLM-DATA

Automatiza la extracción de videos de sesiones desde YouTube (YouTube Data API), la lectura de fechas en actas PDF y la vinculación automática PDF ↔ video por fecha.
Genera un reporte final con enlaces de YouTube y, opcionalmente, links compartidos a los PDFs en Google Drive (PyDrive2). Incluye un archivo de “sin match” para revisión manual.

Proyecto financiado por FONDOCyT.

🎯 Objetivo

Centralizar, limpiar y relacionar la información pública de actas oficiales (PDF) y sus transmisiones en video (YouTube), entregando un dataset usable (CSV/Excel) para consulta, análisis y publicación.

🧭 Alcance

Instituciones cubiertas: Cámara de Diputados (CDD) y Senado de la República Dominicana (SDLR).

Fuentes:

Portales oficiales de Actas (descarga de PDFs).

Canal/Playlists oficiales en YouTube (videos de sesiones).

Google Drive (opcional) para alojar PDFs y obtener enlaces compartibles.

Unidad de enlace: Fecha exacta (YYYY-MM-DD) entre el acta (texto de 1.ª página) y el video (publishedAt).

🗂️ Estructura de carpetas (sugerida)
LLM-DATA/
├─ CDD ACTAS PDFS/                # PDFs de Cámara de Diputados
├─ SDLR ACTAS PDFS/                # PDFs de Senado
├─ client_secrets.json            # Credenciales OAuth (Drive) - no subir público
├─ 1CDD_yt_urls.py                # YouTube → CSV (Cámara)
├─ 1SDLR_yt_urls.py                # YouTube → CSV (Senado)
├─ 2CDD_pdfs.py                   # PDFs → CSV (Cámara)
├─ 2SDR_pdfs.py                   # PDFs → CSV (Senado)
├─ 3CDD_relacion.py               # Relación + Drive (Cámara)
├─ 3SDR_relacion.py               # Relación + Drive (Senado)
├─ 4_excel_pretty.py              # Embellece Excel con hipervínculos
├─ CDD_yt_urls.csv                # salida YouTube (Cámara)
├─ SDR_yt_urls.csv                # salida YouTube (Senado)
├─ CDD PDFS.csv                   # salida PDFs (Cámara)
├─ SDR PDFS.csv                   # salida PDFs (Senado)
├─ CDD RELACION.csv               # salida final (Cámara)
├─ SDR RELACION.csv               # salida final (Senado)
└─ no_match.csv                   # actas sin video (para revisión)


Puedes mantener un único flujo por institución o fusionar ambos en un pipeline general. Lo importante es conservar nombres claros y consistentes.

⚙️ Tecnologías y librerías

Python 3.10+

pandas: tabular, merges, exportes CSV/Excel.

pdfplumber: extracción de texto desde PDFs (1.ª página).

regex (re): fechas “largas” y numéricas, robusto a tildes/variantes.

google-api-python-client: YouTube Data API v3.

PyDrive2: autenticación y acceso a Google Drive (links compartidos).

openpyxl (opcional): Excel con estilo e hipervínculos.

Instalación rápida:

pip install pandas pdfplumber google-api-python-client pydrive2 openpyxl

🔑 Credenciales & claves

YouTube API Key (YouTube Data API v3).

Google Drive OAuth: client_secrets.json (descargado desde Google Cloud → Credentials).

⚠️ No subas estas credenciales a repositorios públicos.

🚀 Cómo correr el pipeline (resumen)
1) Extraer videos de YouTube → *_yt_urls.csv

Obtiene título, fecha (YYYY-MM-DD) y URL desde playlist(s) o canal.

python 1CDD_yt_urls.py
python 1SDR_yt_urls.py


Parámetros dentro del script:

API_KEY

PLAYLIST_ID o CHANNEL_ID (según enfoque)

Salida:
CDD_yt_urls.csv / SDR_yt_urls.csv con columnas:

titulo_youtube, fecha_publicacion, url_youtube

2) Procesar PDFs locales → * PDFS.csv

Lee la primera página de cada PDF, detecta la fecha oficial y guarda:

nombre_documento, fecha_contenido

python 2CDD_pdfs.py
python 2SDR_pdfs.py


Parámetros clave:

ROOT_DIR: carpeta con los PDFs (CDD ACTAS PDFS/, SDR ACTAS PDFS/).

Si un PDF no tiene fecha legible, se deja vacío (aparecerá luego en no_match.csv).

3) Relacionar PDFs ↔ YouTube + (opcional) enlaces de Drive

Hace merge por fecha exacta y agrega links de Drive por nombre de archivo.

python 3CDD_relacion.py
python 3SDR_relacion.py


Salidas:

CDD RELACION.csv / SDR RELACION.csv:

nombre_documento, link_pdf, enlace_youtube


no_match.csv: PDFs sin video para revisión manual.

Notas:

Si usas Drive, define DRIVE_FOLDER_ID y coloca client_secrets.json junto al script.

El script intenta publicar lectura (“anyone with the link, reader”) para generar un link compartible.

El mapeo a Drive es por nombre (con normalización para evitar fallos por tildes/“(1)”/espacios).

4) Excel “bonito” con hipervínculos (opcional)

Convierte el CSV final en un Excel con formato (encabezados, filtros y enlaces clicables).

python 4_excel_pretty.py

🧪 Criterios y supuestos

Match por fecha exacta: fecha_contenido (PDF) = fecha_publicacion (YouTube).

La fecha del PDF proviene del contenido (no del nombre del archivo).

Si en un día hay varios videos, el merge puede generar múltiples filas para un mismo PDF (caso real a revisar).

Los PDFs en Drive deben coincidir en nombre con los locales (se normaliza para tolerar may/minus, tildes, “(1)”, etc.).

🛠️ Troubleshooting

No aparecen links de Drive:

Verifica DRIVE_FOLDER_ID y que los archivos estén en esa carpeta (no en subcarpetas).

Revisa que autorizaste con la misma cuenta donde está la carpeta.

Chequea consola: el script imprime cuántos PDFs vio en Drive.

KeyError: ‘local_path’ / encabezados raros:

Asegúrate de que * PDFS.csv tenga nombre_documento o local_path y fecha_contenido.

Normaliza encabezados: sin espacios, minúsculas.

Fechas vacías en PDFs:

Documento puede ser imagen escaneada sin OCR.

Intenta otra versión del PDF o un OCR previo (no incluido).

YouTube devuelve 0 videos:

Verifica API_KEY y PLAYLIST_ID/CHANNEL_ID.

La API tiene límites por consulta; si el canal es muy grande, pagina o usa la playlist de uploads.

🔒 Privacidad y buenas prácticas

Las fuentes son públicas.

Mantén claves y JSON fuera de repos públicos.

En Drive, usa enlaces solo lectura.

Guarda un respaldo de los PDFs originales.

🙌 Créditos

Implementación y documentación: María José Colás.

Proyecto financiado por FONDOCyT.

🧵 Roadmap (ideas futuras)

Emparejamiento “tolerante” (±1 día) y/o por número de sesión si el portal lo publica.

Pipeline unificado multi-año/multi-institución con configuración en YAML.

Panel simple (Streamlit) para explorar RELACION/no_match.
