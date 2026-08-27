"""
SHACK ENTERTAINMENT — shack_receipt_watcher.py
[WATCH] Watches OneDrive drop zones (phone scans + manual drops),
moves settled files into Data\finance_receipts, runs the expenses
clerk, and Telegrams the result. Scan, walk away, ledger grows.
"""
import os
import shutil
import asyncio
import httpx
from dotenv import load_dotenv
import shack_expenses_ingest as ex

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
LAST_CHAT = os.path.join(project_root, 'configs', 'last_chat.txt')

WATCH = [os.path.join(os.path.expanduser('~'), 'OneDrive', 'ShackReceipts'),
         os.path.join(os.path.expanduser('~'), 'OneDrive', 'Microsoft Lens')]
for w in WATCH:
    os.makedirs(w, exist_ok=True)

async def notify(msg):
    try:
        chat = open(LAST_CHAT).read().strip()
        async with httpx.AsyncClient(timeout=15) as c:
            await c.post(
                'https://api.telegram.org/bot' + TOKEN + '/sendMessage',
                json={'chat_id': int(chat), 'text': msg})
    except Exception as e:
        print('notify failed:', e)

async def loop():
    seen = {}
    while True:
        for w in WATCH:
            try:
                names = os.listdir(w)
            except OSError:
                continue
            for fn in names:
                p = os.path.join(w, fn)
                if not os.path.isfile(p):
                    continue
                low = fn.lower()
                if low.endswith(('.crdownload', '.partial')) or fn.startswith('~'):
                    continue
                if not low.endswith(('.pdf', '.jpg', '.jpeg', '.png')):
                    continue
                s = os.path.getsize(p)
                if seen.get(fn) == s:
                    dest = os.path.join(ex.REC, fn)
                    if os.path.exists(dest):
                        base, ext = os.path.splitext(fn)
                        dest = os.path.join(ex.REC, base + '_2' + ext)
                    shutil.move(p, dest)
                    seen.pop(fn, None)
                    print('new receipt:', fn)
                    added = await ex.main()
                    if added:
                        await notify('🧾 ' + ' | '.join(added) +
                                     ' — logged in expenses.csv')
                    else:
                        await notify('⚠️ ' + fn +
                                     ' unreadable — enter by hand')
                else:
                    seen[fn] = s
        await asyncio.sleep(5)

if __name__ == '__main__':
    print('watching', WATCH)
    asyncio.run(loop())