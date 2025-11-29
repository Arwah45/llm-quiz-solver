from playwright.sync_api import sync_playwright

def get_page_html(url: str, timeout: int = 30000) -> str:
    """Return page HTML after JS execution using Playwright (synchronous)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=timeout)
        html = page.content()
        browser.close()
    return html
