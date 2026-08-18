"""
SHACK ENTERTAINMENT — shack_social.py
[SOCWIRE] 2026-08-17 — Buffer publishing pipe (GraphQL API).
Tier-3: drafts stay local until /social send; posts go to the Buffer
QUEUE (addToQueue), never immediate; Buffer UI stays the 2nd checkpoint.
"""
import os
import json
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler
import httpx
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
social_dir = os.path.join(project_root, 'Social_Drafts')
os.makedirs(social_dir, exist_ok=True)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

BUF = 'https://api.buffer.com'

def _key():
    return os.getenv('BUFFER_API_KEY', '')

def _msg_text(update):
    return update.message.text or update.message.caption or ''

async def _gql(query):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(BUF,
                         headers={'Authorization': 'Bearer ' + _key(),
                                  'Content-Type': 'application/json'},
                         json={'query': query})
        r.raise_for_status()
        return r.json()

async def _channels():
    orgs = await _gql('{ account { organizations { id name } } }')
    olist = (((orgs.get('data') or {}).get('account') or {})
             .get('organizations') or [])
    if not olist:
        return []
    oid = olist[0]['id']
    ch = await _gql(
        '{ channels(input: { organizationId: "' + oid + '" }) '
        '{ id name service } }')
    return (ch.get('data') or {}).get('channels') or []

async def profiles(update, context):
    try:
        chans = await _channels()
        if not chans:
            await update.message.reply_text(
                "No Buffer channels found (check BUFFER_API_KEY in .env).")
            return
        await update.message.reply_text("Buffer channels:\n" + '\n'.join(
            f"{c['service']}  —  {c['name']}" for c in chans))
    except Exception as e:
        await update.message.reply_text(f"❌ Buffer: {type(e).__name__}: {e}")

async def draft(update, context):
    parts = _msg_text(update).split(' ', 2)
    if len(parts) < 3 or not parts[2].strip():
        await update.message.reply_text("Usage: /social draft <post text>")
        return
    ts = datetime.now().strftime('%y%m%d_%H%M%S')
    with open(os.path.join(social_dir, 'PENDING_' + ts + '.md'),
              'w', encoding='utf-8') as f:
        f.write(parts[2].strip() + '\n')
    await update.message.reply_text(
        f"📝 Social draft saved: {ts}\n"
        f"Review: /social pending — queue: /social send {ts} <services csv>")

async def pending(update, context):
    try:
        files = sorted(f for f in os.listdir(social_dir)
                       if f.startswith('PENDING_'))
        if not files:
            await update.message.reply_text("No pending social drafts.")
            return
        out = []
        for f in files:
            with open(os.path.join(social_dir, f), encoding='utf-8') as fh:
                out.append(f.replace('PENDING_', '').replace('.md', '') +
                           ' — ' + fh.read().strip()[:80])
        await update.message.reply_text("Pending social drafts:\n" + '\n'.join(out))
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def send(update, context):
    parts = _msg_text(update).split(' ', 3)
    if len(parts) < 4:
        await update.message.reply_text(
            "Usage: /social send <draft_id> <services csv>")
        return
    did = parts[2].strip()
    services = [s.strip().lower() for s in parts[3].split(',')]
    match = [f for f in os.listdir(social_dir)
             if f.startswith('PENDING_') and did in f]
    if not match:
        await update.message.reply_text("No such draft.")
        return
    with open(os.path.join(social_dir, match[0]), encoding='utf-8') as f:
        text = f.read().strip()
    try:
        chans = [c for c in await _channels() if c['service'] in services]
        if not chans:
            await update.message.reply_text(
                "No connected Buffer channel for: " + ', '.join(services))
            return
        done = []
        for c in chans:
            q = ('mutation { createPost(input: { text: ' + json.dumps(text) +
                 ', channelId: ' + json.dumps(c['id']) +
                 ', schedulingType: automatic, mode: addToQueue }) '
                 '{ ... on PostActionSuccess { post { id dueAt } } '
                 '... on MutationError { message } } }')
            try:
                r = await _gql(q)
                cp = ((r.get('data') or {}).get('createPost')) or {}
                if cp.get('post'):
                    done.append(c['name'] + ' queued')
                else:
                    done.append(c['name'] + ' FAILED: ' +
                                str(cp.get('message') or r.get('errors')))
            except Exception as e:
                body = ''
                if hasattr(e, 'response') and e.response is not None:
                    body = e.response.text[:150]
                done.append(c['name'] + ' FAILED: ' + type(e).__name__ + ' ' + body)
            await asyncio.sleep(2)
        os.rename(os.path.join(social_dir, match[0]),
                  os.path.join(social_dir, match[0].replace('PENDING_', 'QUEUED_')))
        await update.message.reply_text("✅ " + ' | '.join(done) +
                                        "\nCheck the Buffer queue as final look.")
    except Exception as e:
        await update.message.reply_text(f"❌ Buffer: {type(e).__name__}: {e}")

async def _router(update, context):
    parts = _msg_text(update).split()
    sub = parts[1].lower() if len(parts) > 1 else ''
    if sub == 'profiles':
        await profiles(update, context)
    elif sub == 'draft':
        await draft(update, context)
    elif sub == 'pending':
        await pending(update, context)
    elif sub == 'send':
        await send(update, context)
    else:
        await update.message.reply_text(
            'Usage: /social profiles | draft <text> | pending | '
            'send <id> <services csv>')

def add_handlers(app):
    app.add_handler(CommandHandler('social', _router))