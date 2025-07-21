import requests
import json

# Test der API
url = "http://127.0.0.1:5000/api/customers"
data = {
    "name": "Heinz Schlagintweit",
    "company": "Schlagintweit & Co Elektrotechnik u. Planungs KG",
    "contact": "office@instanet.at"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Headers: {response.headers}")
except Exception as e:
    print(f"Error: {e}") 