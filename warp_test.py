import requests

url = 'https://api.ipify.org?format=json'
try:
    response = requests.get(url, timeout=30)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}") 