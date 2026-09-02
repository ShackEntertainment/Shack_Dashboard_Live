import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_main_agent.py')
with open(p, encoding='utf-8') as f:
    t = f.read()

REPL = []
REPL.append((
"if __name__ == '__main__':",
"""async def approve_cmd(update: Update, context):
    parts = _msg_text(update).split()
    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text("Usage: /approve <code>")
        return
    if str(update.effective_chat.id) != og.OWNER:
        await update.message.reply_text("🔒 Approval commands are MD-only.")
        return
    code = parts[1].strip().upper()
    adir = os.path.join(project_root, 'Data', 'approvals')
    os.makedirs(adir, exist_ok=True)
    with open(os.path.join(adir, f"approved_{code}.token"), 'w') as f:
        f.write('approved')
    await update.message.reply_text(
        f"✅ Approved {code} — the asset moves on DA's next tool call.")

if __name__ == '__main__':"""))
REPL.append((
'    app.add_handler(CommandHandler("subscribers", subscribers))',
'    app.add_handler(CommandHandler("subscribers", subscribers))\n'
'    app.add_handler(CommandHandler("approve", approve_cmd))'))

for old, new in REPL:
    assert t.count(old) >= 1, 'anchor not found: ' + old[:60]
    t = t.replace(old, new)
with open(p, 'w', encoding='utf-8') as f:
    f.write(t)
print('/approve wired')