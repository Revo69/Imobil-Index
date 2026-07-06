"""
wake_streamlit.py
Wakes a sleeping Streamlit Community Cloud app by actually loading it in a
headless browser and clicking "Yes, get this app back up!" if present.
A plain HTTP GET is NOT enough — it only returns the static sleep-page shell
without starting the Python process.
"""
import sys
from playwright.sync_api import sync_playwright

APP_URL = "https://imobil-index.streamlit.app"


def wake(url: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(5_000)

        wake_button = page.get_by_role("button", name="Yes, get this app back up!")
        if wake_button.count() > 0:
            print(f"App is asleep, waking: {url}")
            wake_button.click()
            # Give the app time to actually boot before the runner exits
            page.wait_for_timeout(60_000)
        else:
            print(f"App already awake: {url}")

        browser.close()


if __name__ == "__main__":
    try:
        wake(APP_URL)
    except Exception as exc:
        print(f"Failed to wake app: {exc}")
        sys.exit(1)
