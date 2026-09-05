import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_main_agent.py')
with open(p, encoding='utf-8') as f:
    lines = f.read().split('\n')

BLOCK = '''import edge_tts
VOICE_ID = 'en-GB-SoniaNeural'

async def _tts_send(text, update):
    import tempfile
    fn = os.path.join(tempfile.gettempdir(), 'shack_voice.mp3')
    await edge_tts.Communicate(text[:6000], VOICE_ID).save(fn)
    with open(fn, 'rb') as f:
        await update.message.reply_audio(audio=f, title='Shack voice note')

async def read_cmd(update, context):
    if str(update.effective_chat.id) != og.OWNER:
        await update.message.reply_text("🔒 Read is MD-only.")
        return
    parts = update.message.text.split()
    out_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Data', 'deals', 'outputs')
    d = os.path.join(out_base, parts[1]) if len(parts) > 1 and os.path.isdir(os.path.join(out_base, parts[1])) else None
    if d is None:
        subs = [os.path.join(out_base, x) for x in os.listdir(out_base) if os.path.isdir(os.path.join(out_base, x))]
        d = max(subs, key=os.path.getmtime) if subs else out_base
    cands = [os.path.join(d, x) for x in os.listdir(d) if x.endswith('_reply.md')]
    if not cands:
        await update.message.reply_text('No replies to read.')
        return
    fn = max(cands, key=os.path.getmtime)
    await update.message.reply_text('🔊 Reading: ' + os.path.basename(fn))
    await _tts_send(open(fn, encoding='utf-8').read(), update)

'''

i = next(i for i, l in enumerate(lines) if l.startswith('async def runstage_cmd'))
lines[i:i] = BLOCK.split('\n')

i = next(i for i, l in enumerate(lines) if 'CommandHandler("runstage"' in l)
lines.insert(i + 1, '    app.add_handler(CommandHandler("read", read_cmd))')

i = next(i for i, l in enumerate(lines) if l.strip() == 'await update.message.reply_text(summary)')
lines.insert(i + 1, '    await _tts_send(summary, update)')

with open(p, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('voice patch applied')