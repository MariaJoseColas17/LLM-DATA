# LLM-DATA — Relación de Actas (PDF) con Videos de Sesiones en YouTube

Este proyecto automatiza el cruce entre actas (PDF) de sesiones del Senado (SDLR) y la Cámara de Diputados (CDD) de la República Dominicana y sus videos correspondientes en YouTube.
-

A partir de los PDFs descargados y las publicaciones oficiales de cada canal, el pipeline:
-
Lee y entiende fechas directamente del contenido de los PDFs o del nombre del archivo.


Consulta YouTube (YouTube Data API v3) para obtener título, fecha y URL de cada sesión.


Relaciona PDF ↔ video por fecha, generando un reporte final con enlaces clicables.


(Opcional) Publica los PDFs en Google Drive y agrega el link compartido a cada acta.


Produce un archivo “sin match” con los casos que requieren revisión manual.


El objetivo es entregar una vista única y confiable por institución y por año: qué acta corresponde a qué video, todo en CSV/Excel listo para análisis, verificación y archivo.
---

## 📚 Fuentes oficiales

* **Cámara de Diputados (CDD) – Actas:** [https://www.camaradediputados.gob.do/actas](https://www.camaradediputados.gob.do/actas)
* **Senado de la República (SDLR):** [https://www.senado.gob.do/](https://www.senado.gob.do/)
* **YouTube – Cámara de Diputados:** [https://www.youtube.com/@CamaraDeDiputadosRD](https://www.youtube.com/@CamaraDeDiputadosRD)
* **YouTube – Senado:** [https://www.youtube.com/@SenadoRD](https://www.youtube.com/@SenadoRD)

---

## ✅ Resultado

El pipeline genera, para **cada institución** (CDD / SDLR):

* **`*_RELACION.csv`** → columnas: **`nombre_documento`**, **`link_pdf`** (enlace público a Drive), y **`enlace_youtube`**.
* **`no_match.csv`** → PDFs cuya fecha **no encontró** video (para supervisión manual).
* **`*_Archivo Relacional.xlsx`** → versión en Excel con hipervínculos clicables

---

## 🗂️ Estructura de carpetas (idéntica para CDD y SDLR)

### `CDD DATA PROCESSING`

```
CDD Archivo Relacional.xlsx
1CDD_yt_urls.py          # YouTube API: extrae títulos/fechas/URLs de videos
2CDD_pdfs.py             # PDF → fecha (lee 1ª página y detecta AAAA-MM-DD)
3CDD_relacion.py         # Une por fecha, añade links de Drive, exporta CSV y no_match
4CDD_cvsaexcel.py        # Da formato y exporta Excel desde el CSV final
CDD PDFS.csv             # Salida de (2): nombre_documento, fecha_contenido
CDD RELACION.csv         # Salida de (3): nombre_documento, link_pdf, enlace_youtube
CDD_yt_urls.csv          # Salida de (1): titulo, fecha_publicacion, url_youtube
no_match.csv             # Salida de (3): PDFs sin video coincidente


## 🔁 Flujo de trabajo (4 scripts)

1. **YouTube → CSV**
   Ejecuta `1CDD_yt_urls.py` / `1SDLR_yt_urls.py`.

   * Usa **YouTube Data API v3** para obtener **título, fecha de publicación y URL** de videos.
   * Filtra por patrones (sesiones/legislaturas) y guarda en `*_yt_urls.csv`.

2. **PDFs → fechas**
   Ejecuta `2CDD_pdfs.py` / `2SDLR_pdfs.py`.

   * Abre cada PDF con **pdfplumber**, toma la **1ª página** y extrae la fecha (regex robusta en español; también entiende 01/10/2024).
   * Guarda `*_PDFS.csv` con **`nombre_documento`** y **`fecha_contenido`** (AAAA-MM-DD).

3. **Relación por fecha + Drive**
   Ejecuta `3CDD_relacion.py` / `3SDLR_relacion.py`.

   * Une `*_PDFS.csv` con `*_yt_urls.csv` por **fecha**.
   * (Opcional) Usa **PyDrive2** + **`client_secrets.json`** para mapear **enlaces de Drive** de cada PDF por nombre.
   * Exporta **`*_RELACION.csv`** y **`no_match.csv`**.

4. **CSV → Excel con formato**
   Ejecuta `4CDD_cvsaexcel.py` / `4SDLR_cvsaexcel.py`.

   * Crea **`*_Archivo Relacional.xlsx`** con headers en negrita, filtros, zebra y **hipervínculos clicables**.

---

## ▶️ Cómo ejecutar (ejemplo CDD)

```bash
# 1) Videos de YouTube → CDD_yt_urls.csv
python 1CDD_yt_urls.py

# 2) PDFs locales → fechas → CDD PDFS.csv
python 2CDD_pdfs.py

# 3) Relación (join por fecha) + enlaces Drive → CSV final + no_match
python 3CDD_relacion.py

# 4) Excel con estilo desde el CSV final
python 4CDD_cvsaexcel.py
```

> Repite exactamente lo mismo con los scripts **SDLR** para el Senado.

---

## 🔐 Credenciales y requisitos

* **Python 3.10+**
* Instalar dependencias:

  ```
  pip install google-api-python-client pydrive2 pdfplumber pandas openpyxl
  ```
* **YouTube Data API v3:** crea una **API key** en Google Cloud y colócala en `1*_yt_urls.py`.
* **Google Drive (opcional):**

  * Crea credencial **OAuth de escritorio** y descarga **`client_secrets.json`**.
  * Guarda el JSON **junto** al script `3*_relacion.py`.
  * La primera ejecución abrirá el navegador para autorizar; se guardará un token local.

---

## 🧩 Consideraciones

* La coincidencia se hace por **fecha exacta** (AAAA-MM-DD). Si el acta o el video difieren por zona horaria o publicación tardía, el elemento irá a **`no_match.csv`** para revisión manual.
* La detección de fecha se hace en la **1ª página** del PDF; formatos muy atípicos pueden requerir ajustar la regex.
* Para los enlaces de Drive, los **nombres de archivos** en la nube deben **coincidir exactamente** con los nombres detectados localmente.

---

## 🛠️ Tecnologías

* **Python**, **pandas**, **pdfplumber**, **openpyxl**
* **YouTube Data API v3** (`google-api-python-client`)
* **Google Drive** con **PyDrive2** (OAuth)
* **Expresiones regulares** para fechas en español

---

## 📦 Entregables

* **`*_RELACION.csv`** – reporte final (PDF ↔ YouTube).
* **`*_Archivo Relacional.xlsx`** – el mismo reporte en Excel, con formato y links activos.
* **`no_match.csv`** – pendientes a validar manualmente.


Agradecimientos
--
Este proyecto ha sido financiado parcialmente por el Ministerio de Educación Superior, Ciencia y Tecnología (MESCyT) de la República Dominicana a través de la subvención FONDOCYT. Los autores agradecen este apoyo. 
Las opiniones, hallazgos, conclusiones o recomendaciones expresadas en este material son responsabilidad de los autores y no necesariamente reflejan la opinión del MESCyT.

