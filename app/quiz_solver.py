import re
import json
import time
import requests
from bs4 import BeautifulSoup
from .browser import get_page_html
from .data_utils import download_file, load_tabular, pdf_text_by_page
from .analysis_utils import sum_column, mean_column
from .config import STUDENT_EMAIL, STUDENT_SECRET

def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for s in soup(["script", "style"]):
        s.decompose()
    return soup.get_text(separator="\n").strip()

def extract_submit_url_and_links(html: str, base_url: str | None = None) -> dict:
    soup = BeautifulSoup(html, "lxml")
    submit_url = None
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        links.append(href)
        text = (a.get_text() or "").lower()
        if submit_url is None and ("submit" in href.lower() or "submit" in text or "answer" in href.lower() or "answer" in text):
            submit_url = href
    if submit_url is None:
        form = soup.find("form")
        if form and form.get("action"):
            submit_url = form.get("action")
    return {"submit_url": submit_url, "links": links}

def simple_intent_parse(text: str) -> dict:
    lowered = text.lower()
    intent = None
    if re.search(r"\b(sum|total of|what is the sum|what is the total)\b", lowered):
        intent = "sum"
    elif re.search(r"\b(mean|average|avg)\b", lowered):
        intent = "mean"
    elif re.search(r"\b(true|false|yes|no|boolean)\b", lowered):
        intent = "boolean"
    elif re.search(r"\b(count|how many)\b", lowered):
        intent = "count"
    elif re.search(r"\b(max|maximum|highest)\b", lowered):
        intent = "max"
    elif re.search(r"\b(min|minimum|lowest)\b", lowered):
        intent = "min"
    else:
        intent = "unknown"

    col_match = re.search(r"[\"'“”](?P<col>[A-Za-z0-9 _-]{1,60})[\"'“”]\s+column", text, re.I)
    if not col_match:
        col_match = re.search(r"column\s+['\"]?(?P<col>[A-Za-z0-9_ -]+)['\"]?", text, re.I)
    column = col_match.group("col").strip() if col_match else None

    page_match = re.search(r"page\s+([0-9]{1,3})", text, re.I)
    page = int(page_match.group(1)) if page_match else None

    return {"intent": intent, "column": column, "page": page}

def choose_numeric_column(df):
    # Return a candidate numeric column name or None
    numeric_cols = [c for c in df.columns if df[c].dtype.kind in "biufc"]
    if not numeric_cols:
        return None
    # prefer likely names
    for pref in ("value", "amount", "total", "sum", "count"):
        for c in numeric_cols:
            if pref in c.lower():
                return c
    return numeric_cols[0]

def solve_quiz_url(email: str, secret: str, url: str, deadline: float):
    current_url = url
    while True:
        if time.time() > deadline:
            return {"status": "timeout"}

        html = get_page_html(current_url)
        text = html_to_text(html)
        extracted = extract_submit_url_and_links(html)
        submit_url = extracted.get("submit_url")
        links = extracted.get("links", [])

        parsed = simple_intent_parse(text)
        intent = parsed["intent"]
        column = parsed["column"]
        page = parsed["page"]

        data_link = None
        for l in links:
            l_lower = l.lower()
            if any(l_lower.endswith(ext) for ext in (".csv", ".xlsx", ".xls", ".pdf")):
                data_link = l
                break

        # Normalize relative URLs if needed: if data_link is relative and page link exists, attempt naive join
        if data_link and data_link.startswith("/") and current_url.startswith("http"):
            from urllib.parse import urljoin
            data_link = urljoin(current_url, data_link)

        answer = None
        if data_link:
            local_path = download_file(data_link)
            if local_path.lower().endswith(".pdf"):
                if page:
                    txt = pdf_text_by_page(local_path, page_number=page)
                    # We cannot robustly parse tabular PDFs in minimal mode.
                    answer = {"note": "PDF downloaded; manual table parsing not implemented in MVP", "path": local_path}
                else:
                    answer = {"note": "PDF downloaded; no page specified", "path": local_path}
            else:
                import pandas as pd
                df = load_tabular(local_path)
                if column is None:
                    column = choose_numeric_column(df)
                try:
                    if intent == "mean":
                        numeric_mean = float(mean_column(df, column)) if column else float(df.select_dtypes(include=["number"]).mean().iloc[0])
                        answer = numeric_mean
                    else:
                        # default to sum for sum/unknown/count requests
                        if intent == "count":
                            answer = int(len(df))
                        elif intent in ("max", "minimum", "min"):
                            if column:
                                answer = float(df[column].max())
                            else:
                                answer = float(df.select_dtypes(include=["number"]).max().iloc[0])
                        else:
                            numeric_sum = float(sum_column(df, column)) if column else float(df.select_dtypes(include=["number"]).sum().iloc[0])
                            answer = numeric_sum
                except Exception as e:
                    answer = {"error": str(e), "available_columns": list(df.columns)}

        else:
            # No data link found — try to answer trivially from text or return diagnostic
            if "true" in text.lower() and "false" in text.lower():
                answer = {"note": "ambiguous boolean in text; manual step required"}
            else:
                answer = {"note": "No data link found. Manual/advanced parsing required.", "inspected_text": text[:600]}

        payload = {
            "email": email,
            "secret": secret,
            "url": current_url,
            "answer": answer
        }

        if not submit_url:
            # Return diagnostic so you can debug
            return {"status": "no_submit_url", "inspected_links": links, "parsed": parsed, "payload": payload}

        # If submit_url is relative, join with current_url
        if submit_url.startswith("/") and current_url.startswith("http"):
            from urllib.parse import urljoin
            submit_url = urljoin(current_url, submit_url)

        try:
            resp = requests.post(submit_url, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            return {"status": "submit_error", "error": str(e), "payload": payload}

        if result.get("correct"):
            next_url = result.get("url")
            if next_url:
                current_url = next_url
                continue
            else:
                return {"status": "done", "result": result}
        else:
            next_url = result.get("url")
            if next_url:
                current_url = next_url
                continue
            else:
                return {"status": "wrong", "result": result}
