"""
Re-authorize Google Sheets OAuth with FULL scopes (spreadsheets + drive).
Manual flow: prints URL -> you open browser -> paste auth code back.
"""

import json
import os
import urllib.parse
import urllib.request

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(PROJECT_ROOT, 'configs', 'credentials.json')
TOKEN_PATH = os.path.join(PROJECT_ROOT, 'configs', 'token.json')

# Load credentials
with open(CREDS_PATH) as f:
    creds_data = json.load(f)['installed']

CLIENT_ID = creds_data['client_id']
CLIENT_SECRET = creds_data['client_secret']

# Full scopes needed for gspread
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Build authorization URL
params = urllib.parse.urlencode({
    'client_id': CLIENT_ID,
    'redirect_uri': 'http://localhost',
    'response_type': 'code',
    'access_type': 'offline',
    'prompt': 'consent',
    'scope': ' '.join(SCOPES),
})

auth_url = "https://accounts.google.com/o/oauth2/auth?" + params

print("=" * 60)
print("SHACK PROJECT - Google Sheets Re-Authorization")
print("=" * 60)
print()
print("STEP 1: Open this URL in your browser:")
print()
print(auth_url)
print()
print("STEP 2: Sign in with shackentertainment@gmail.com")
print("STEP 3: Grant permission (spreadsheets + drive)")
print("STEP 4: The browser will redirect to localhost and show")
print("         an error page - that's normal!")
print("STEP 5: Copy the FULL URL from your browser address bar")
print("         (it will look like http://localhost/?code=XXXXX...)")
print()

auth_code_input = input("Paste the full URL or just the code here: ").strip()

# Extract code from URL if they pasted the whole URL
if 'code=' in auth_code_input:
    parsed = urllib.parse.urlparse(auth_code_input)
    params_dict = urllib.parse.parse_qs(parsed.query)
    auth_code = params_dict['code'][0]
else:
    auth_code = auth_code_input

print()
print("Exchanging authorization code for tokens...")

token_data = urllib.parse.urlencode({
    'code': auth_code,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'redirect_uri': 'http://localhost',
    'grant_type': 'authorization_code',
}).encode('utf-8')

req = urllib.request.Request(
    'https://oauth2.googleapis.com/token',
    data=token_data,
    method='POST'
)
req.add_header('Content-Type', 'application/x-www-form-urlencoded')

try:
    response = urllib.request.urlopen(req)
    token_json = json.loads(response.read().decode('utf-8'))

    token_to_save = {
        'token': token_json.get('access_token'),
        'refresh_token': token_json.get('refresh_token'),
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scopes': SCOPES,
        'expiry': token_json.get('expires_in', 3600),
    }

    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_to_save, f, indent=2)

    print()
    print("=" * 60)
    print("SUCCESS! New token saved to:")
    print(TOKEN_PATH)
    print()
    print("Scopes granted:")
    for s in SCOPES:
        print(f"  - {s}")
    print()
    print("Refresh token:", "YES" if token_to_save.get('refresh_token') else "NO (re-use existing)")
    print("=" * 60)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
