import requests
import json

print("🔍 Testing AnythingLLM API Authentication Methods...\n")

API_KEY = "SYWBD4J-CXZ4AEE-H9VWR1-P3WDYVG"

# Test different authentication header formats
auth_methods = [
    {"Authorization": f"Bearer {API_KEY}"},
    {"X-API-Key": API_KEY},
    {"Authorization": API_KEY},
]

payload = {"message": "test", "mode": "chat"}

for i, headers_dict in enumerate(auth_methods, 1):
    headers_dict["Content-Type"] = "application/json"
    
    print(f"Test {i}: Headers = {list(headers_dict.keys())}")
    
    try:
        response = requests.post(
            "http://localhost:3001/api/v1/workspace/shack-finance/chat",
            headers=headers_dict,
            json=payload,
            timeout=5
        )
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:150]}")
        if response.status_code == 200:
            print("  ✅ SUCCESS! This is the correct format!\n")
            break
    except Exception as e:
        print(f"  Error: {str(e)[:100]}\n")

print("\nAlso checking: Is the workspace slug correct?")
print("Try accessing in your browser: http://localhost:3001/workspace/shack-finance")
print("Does the workspace exist with that exact name?")