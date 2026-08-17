import requests

API_KEY = "S6FXWJQ-3I7MVHY-PM7Y1F2-9PAB4FP"
URL = "http://localhost:3001/api/v1/workspace/shack-finance/chat"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "message": "Hello",
    "mode": "chat"
}

try:
    print("Testing AnythingLLM API...")
    response = requests.post(URL, headers=headers, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"ERROR: {e}")
    print("Is AnythingLLM running on port 3001?")