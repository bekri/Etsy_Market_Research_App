import cloudscraper

url = 'https://www.etsy.com/'
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

try:
    response = scraper.get(url, timeout=30)
    print(f"Status code: {response.status_code}")
    print(f"First 500 chars:\n{response.text[:500]}")
except Exception as e:
    print(f"Error: {e}") 