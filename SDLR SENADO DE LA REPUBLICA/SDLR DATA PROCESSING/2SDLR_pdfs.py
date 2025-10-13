from pathlib import Path
import re, unicodedata
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent / "SDLR ACTAS PDFS"
OUT_CSV  = "SDLR PDFS.csv"

MESES = {
    "enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
    "julio":7,"agosto":8,"septiembre":9,"setiembre":9,"octubre":10,
    "noviembre":11,"diciembre":12,
    "ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,"jul":7,"ago":8,"sept":9,"oct":10,"nov":11,"dic":12,
    "sepiembre":9  # typo frecuente
}
DIAS = r"lunes|martes|miercoles|miércoles|jueves|viernes|sabado|sábado|domingo"

def ymd(y,m,d): return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"

def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii").lower()
    s = re.sub(r"\b(1ro|1o|1\.?º)\b", "1", s)
    s = re.sub(r"\bde\s*fecha\b", " ", s)       # ← quita "de fecha"
    s = re.sub(r"[-_\.]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

PAT_LARGO = re.compile(
    rf"(?:\b(?:{DIAS})\b\s+de\s+|del\s+(?:{DIAS})\s+)?"
    rf"(\d{{1,2}})\s+(?:de\s+)?"
    rf"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre|"
    rf"ene|feb|mar|abr|may|jun|jul|ago|sept|oct|nov|dic|sepiembre)"
    rf"\s+(?:de\s+|del\s+)?(\d{{4}})"
)
PAT_DMY = re.compile(r"\b(\d{1,2})[ \-_/\.](\d{1,2})[ \-_/\.](\d{4})\b")
PAT_YMD = re.compile(r"\b(20\d{2})[ \-_/\.](\d{1,2})[ \-_/\.](\d{1,2})\b")

def _valid(d,m): return 1<=d<=31 and 1<=m<=12

def fecha_desde_nombre(nombre: str) -> str:
    n = _normalize(nombre.rsplit(".",1)[0])

    m = PAT_LARGO.search(n)
    if m:
        d, mes_txt, y = int(m.group(1)), m.group(2), int(m.group(3))
        if not re.fullmatch(DIAS, mes_txt or ""):
            mn = MESES.get(mes_txt, 0)
            if mn and _valid(d, mn): return ymd(y, mn, d)

    m = PAT_YMD.search(n)
    if m:
        y, mn, d = map(int, m.groups())
        if _valid(d, mn): return ymd(y, mn, d)

    m = PAT_DMY.search(n)
    if m:
        d, mn, y = map(int, m.groups())
        if _valid(d, mn): return ymd(y, mn, d)

    return ""

def main():
    rows, sin = [], []
    for p in sorted(ROOT_DIR.rglob("*.pdf")):
        f = fecha_desde_nombre(p.name) or ""
        if not f: sin.append(p.name)
        rows.append({"nombre_documento": p.name, "fecha_contenido": f})

    df = pd.DataFrame(rows, dtype=object)
    df["fecha_contenido"] = df["fecha_contenido"].where(df["fecha_contenido"]!="", "SIN_FECHA")
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig", na_rep="SIN_FECHA")

    print(f"OK -> {OUT_CSV} ({len(df)} filas)")
    if sin:
        print("Sin fecha (muestra):")
        for s in sin[:10]: print("  -", s)

if __name__ == "__main__":
    main()