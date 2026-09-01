"""
SHACK ENTERTAINMENT — shack_patch_subscribers.py
Wires /subscribe and /subscribers into the bot.
"""
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_main_agent.py')
with open(p, encoding='utf-8') as f:
    t = f.read()

REPL = []
REPL.append((
"import shack_ops_guard as og",
"import shack_ops_guard as og\nimport shack_subscribers as ssb"))
REPL.append((
"if __name__ == '__main__':",
"""async def subscribe(update: Update, context):
    parts = _msg_text(update).split(' ', 1)
    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text("Usage: /subscribe <email>")
        return
    sid, msg = ssb.add(parts[1].strip())
    await update.message.reply_text(msg)
    if sid:
        await send_voice(update, msg)

async def subscribers(update: Update, context):
    await update.message.reply_text(f"📬 {ssb.count()} active subscriber(s).")

if __name__ == '__main__':"""))
REPL.append((
'    app.add_handler(CommandHandler("senddraft", senddraft))',
'    app.add_handler(CommandHandler("senddraft", senddraft))\n'
'    app.add_handler(CommandHandler("subscribe", subscribe))\n'
'    app.add_handler(CommandHandler("subscribers", subscribers))'))

for old, new in REPL:
    assert t.count(old) >= 1, 'anchor not found: ' + old[:60]
    t = t.replace(old, new)
with open(p, 'w', encoding='utf-8') as f:
    f.write(t)
print('subscribers wired: /subscribe + /subscribers live')