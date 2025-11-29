import requests
from pathlib import Path
from PyPDF2 import PdfReader
import pandas as pd

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def download_file(url: str, filename: str | None = None, timeout: int = 60) -> str:
    if filename is None:
        filename = url.split("/")[-1] or "downloaded"
    path = DATA_DIR / filename
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    path.write_bytes(resp.content)
    return str(path)

def load_tabular(path: str) -> pd.DataFrame:
    path = str(path)
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    if path.lower().endswith((".xls", ".xlsx")):
        return pd.read_excel(path)
    raise ValueError("Unsupported tabular file type: " + path)

def pdf_text_by_page(path: str, page_number: int | None = None) -> str:
    reader = PdfReader(path)
    pages = reader.pages
    if page_number is None:
        texts = [p.extract_text() or "" for p in pages]
        return "\n".join(texts)
    if page_number < 1 or page_number > len(pages):
        raise IndexError("page_number out of range")
    return pages[page_number - 1].extract_text() or ""
