import requests

print("Checking workspace access...\n")

# Try to access the workspace directly
urls_to_try = [
    "http://localhost:3001/api/v1/workspace",
    "http://localhost:3001/api/v1/workspaces",
    "http://localhost:3001/workspace/shack-finance",
    "http://localhost:3001/workspace/Shack-Finance",
]

for url in urls_to_try:
    try:
        response = requests.get(url, timeout=3)
        print(f"GET {url}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ Found it! Response: {response.text[:100]}")
        print()
    except Exception as e:
        print(f"GET {url}")
        print(f"  Error: {str(e)[:80]}\n")