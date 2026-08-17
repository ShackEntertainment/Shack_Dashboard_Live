"""Clean restart Streamlit - clear all caches first"""
import subprocess, time, os, shutil, sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

print('1. Killing python...')
subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
time.sleep(2)

print('2. Clearing __pycache__ directories...')
for root, dirs, files in os.walk('C:/Users/Bola/Documents/Shack_Project'):
    dirs[:] = [d for d in dirs if d not in ['.streamlit']]
    if root.endswith('__pycache__'):
        print(f'   Removing: {root}')
        shutil.rmtree(root, ignore_errors=True)

# Also clear .streamlit cache
st_cache = 'C:/Users/Bola/Documents/Shack_Project/.streamlit'
if os.path.exists(st_cache):
    for item in os.listdir(st_cache):
        path = os.path.join(st_cache, item)
        if os.path.isdir(path) and ('cache' in item.lower() or 'pyc' in item.lower()):
            print(f'   Removing: {path}')
            shutil.rmtree(path, ignore_errors=True)

print('3. Starting Streamlit fresh...')
subprocess.Popen([
    'C:/Users/Bola/AppData/Local/Programs/Python/Python314/python.exe',
    '-m', 'streamlit', 'run',
    'C:/Users/Bola/Documents/Shack_Project/dashboards/Home.py',
    '--server.headless', 'true',
    '--server.port', '8501'
], creationflags=subprocess.CREATE_NO_WINDOW)

time.sleep(8)

try:
    r = urllib.request.urlopen('http://localhost:8501', timeout=5)
    print(f'Streamlit is UP - status {r.status}')
except Exception as e:
    print(f'Streamlit check failed: {e}')
