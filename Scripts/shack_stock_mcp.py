"""
SHACK ENTERTAINMENT — shack_stock_mcp.py
Phase 1 MCP stock tool for the Design Agent (read-only retrieval).
Searches Unsplash, downloads to assets\stock, logs rights in Data\stock_log.csv.
Runs under AnythingLLM via stdio. Self-test: py shack_stock_mcp.py --test
"""
import os, sys
from datetime import date
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

KEY = os.getenv('UNSPLASH_KEY', '')
STOCK = os.path.join(project_root, 'assets', 'stock')
LOG = os.path.join(project_root, 'Data', 'stock_log.csv')
os.makedirs(STOCK, exist_ok=True)
HEADER = 'date,source,creator,license,filename,query'
LIC = 'Unsplash License - free commercial use, attribution optional'

mcp = FastMCP('ShackStock')

def _rows():
    if not os.path.exists(LOG):
        return []
    with open(LOG, encoding='utf-8') as f:
        return [l.rstrip() for l in f if l.strip()]

@mcp.tool()
def stock_search(query: str, max_results: int = 6) -> str:
    """Search Unsplash for reference/stock imagery; returns a short list."""
    if not KEY:
        return 'UNSPLASH_KEY missing in configs/.env'
    r = httpx.get('https://api.unsplash.com/search/photos',
                  params={'query': query, 'per_page': max_results},
                  headers={'Authorization': f'Client-ID {KEY}'}, timeout=20)
    r.raise_for_status()
    out = []
    for p in r.json().get('results', []):
        out.append({'id': p['id'],
                    'desc': (p.get('description') or p.get('alt_description')
                             or 'untitled')[:80],
                    'photographer': p['user']['name'],
                    'url': p['urls']['regular']})
    return str(out)

@mcp.tool()
def stock_download(url: str, filename: str,
                   photographer: str = '', query: str = '') -> str:
    """Download one chosen image into assets\\stock and log rights."""
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        filename += '.jpg'
    r = httpx.get(url, headers={'Authorization': f'Client-ID {KEY}'},
                  timeout=60, follow_redirects=True)
    r.raise_for_status()
    path = os.path.join(STOCK, filename)
    with open(path, 'wb') as f:
        f.write(r.content)
    rows = _rows() or [HEADER]
    rows.append(','.join([date.today().isoformat(), 'unsplash',
                          photographer.replace(',', ' '), LIC, filename,
                          query.replace(',', ' ')]))
    with open(LOG, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rows) + '\n')
    return f'Banked: {path} (rights logged)'

@mcp.tool()
def stock_list() -> str:
    """List logged stock assets."""
    return '\n'.join(_rows() or ['(no stock logged yet)'])

if __name__ == '__main__':
    if '--test' in sys.argv:
        print(stock_search('jazz stage spotlight'))
    else:
        mcp.run()