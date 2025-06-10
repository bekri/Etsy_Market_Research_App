import requests
import json

url = 'https://www.etsy.com/search?q=handmade+soap+bath&explicit=1&ref=search_bar&is_best_seller=true'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'DNT': '1',
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status code: {response.status_code}")
    print(f"First 1000 chars of HTML:\n{response.text[:1000]}")
except Exception as e:
    print(f"Error: {e}") 