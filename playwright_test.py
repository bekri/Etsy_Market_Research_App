from playwright.sync_api import sync_playwright
import time

url = 'https://www.etsy.com/search?q=handmade+soap+bath&explicit=1&ref=search_bar&is_best_seller=true'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle')
    time.sleep(2)  # Wait for dynamic content to load

    # Updated CSS selectors for product titles
    titles = page.query_selector_all('h3.v2-listing-card__title')
    for title in titles:
        print(title.inner_text())

    browser.close() 