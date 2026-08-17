import requests
import json

# Test 1: Can we reach AnythingLLM at all?
print("Test 1: Checking if AnythingLLM is accessible...")
try:
    response = requests.get("http://localhost:3001", timeout=5)
    print(f"✅ AnythingLLM is running! Status: {response.status_code}")
except:
    print(" Cannot reach AnythingLLM at localhost:3001")
    print("   Is AnythingLLM desktop app running? Does it have a web server?")
    exit()

# Test 2: Try the API with different key formats
print("\nTest 2: Testing API keys...")

keys_to_try = [
    "SYWBD4J-CXZ4AEE-H9VWR1-P3WDYVG",
    "S6FXWJQ-3I7MVHY-PM7Y1F2-9PAB4FP"
]

for api_key in keys_to_try:
    print(f"\nTrying key: {api_key[:10]}...")
    
    # Try with Bearer token
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": "test",
        "mode": "chat"
    }
    
    # Try different endpoint formats
    endpoints = [
        "http://localhost:3001/api/v1/workspace/shack-finance/chat",
        "http://localhost:3001/api/v1/workspace/Shack-Finance/chat",
        "http://localhost:3001/api/v1/chat/completions"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=5)
            print(f"  Endpoint: {endpoint}")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:100]}")
            if response.status_code == 200:
                print("  ✅ SUCCESS! Use this endpoint and key!")
                break
        except Exception as e:
            print(f"  Endpoint {endpoint}: {str(e)[:50]}")