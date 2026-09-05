import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_main_agent.py')
with open(p, encoding='utf-8') as f:
    lines = f.read().split('\n')

# 1. Owner is never intake: voice_intake walks away from the MD.
i = next(i for i, l in enumerate(lines) if l.startswith('async def voice_intake'))
lines.insert(i + 1, '    if str(update.effective_chat.id) == og.OWNER:\n        return')

# 2. The natural layer: plain text from the MD, no slash required.
NAT = '''async def owner_natural(update, context):
    if str(update.effective_chat.id) != og.OWNER:
        return
    text = (update.message.text or '').strip().lower()
    if not text:
        return
    if 'approve' in text: action = 'approve'
    elif 'run stage' in text or 'runstage' in text: action = 'runstage'
    elif text.startswith('read'): action = 'read'
    elif text.startswith('status'): action = 'status'
    else: return
    deal_code = next((v for k, v in VOICE_DEALS.items() if k in text), None)
    if action != 'status' and not deal_code:
        await update.message.reply_text(f"Heard '{action}' but no deal name (showcase / spirit).")
        return
    await update.message.reply_text(f'🗣️ Heard → /{action} ' + (deal_code or ''))
    context.args = [deal_code] if deal_code else []
    if action == 'approve':
        card_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Data', 'deals', deal_code + '.json')
        if os.path.exists(card_p):
            import json as _json
            with open(card_p, encoding='utf-8') as f: card = _json.load(f)
            nxt = card['status']['current_stage'] + 1
            tok = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Data', 'approvals', f'approved_{deal_code}-S{nxt}.token')
            with open(tok, 'w') as f: f.write('natural')
            await update.message.reply_text(f'🗣️ Token released: {deal_code}-S{nxt} approved.')
    elif action == 'read': await read_cmd(update, context)
    elif action == 'runstage': await runstage_cmd(update, context)
    elif action == 'status': await status(update, context)

'''
i = next(i for i, l in enumerate(lines) if l.startswith('async def runstage_cmd'))
lines[i:i] = NAT.split('\n')

# 3. Register it.
i = next(i for i, l in enumerate(lines) if 'filters.VOICE, handle_voice' in l)
lines.insert(i + 1, '    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, owner_natural))')

with open(p, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('natural layer applied')