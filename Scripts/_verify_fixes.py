import sys
sys.stdout.reconfigure(encoding='utf-8')

# Verify the fix is actually in place
with open('data_sync.py', 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    ('Scope reads from token.json', 'token_scopes = token_data.get' in content),
    ('OAuth warning silenced', 'st.warning' not in content or 'pass  # Silently fail - OAuth' in content),
    ('Service account warning silenced', 'st.warning(f"Service account' not in content),
    ('Secrets error silenced', 'st.error(f"Error loading credentials' not in content),
]

print('=== data_sync.py Fix Verification ===')
for name, result in checks:
    status = 'PASS' if result else 'FAIL'
    print(status + ': ' + name)

# Also check: does get_google_credentials still have any st.warning/st.error?
import re
warnings = re.findall(r'st\.(warning|error)\(', content)
print('\nRemaining st.warning/st.error calls in data_sync.py: ' + str(len(warnings)))
for w in warnings:
    print('  - st.' + w)
