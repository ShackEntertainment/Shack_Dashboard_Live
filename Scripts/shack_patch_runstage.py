import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_main_agent.py')
with open(p, encoding='utf-8') as f:
    t = f.read()

REPL = []
REPL.append((
"import shack_subscribers as ssb",
"import shack_subscribers as ssb\nimport shack_runstage as rsg\nimport asyncio"))
REPL.append((
"if __name__ == '__main__':",
"""async def runstage_cmd(update: Update, context):
    if str(update.effective_chat.id) != og.OWNER:
        await update.message.reply_text("🔒 Runstage is MD-only.")
        return
    parts = _msg_text(update).split()
    code = parts[1] if len(parts) > 1 else 'DEAL-SPIRITCO'
    await update.message.reply_text(f"🎼 Firing current stage of {code} — replies will follow.")
    summary = await asyncio.to_thread(rsg.run, code)
    await update.message.reply_text(summary)

if __name__ == '__main__':"""))
REPL.append((
'    app.add_handler(CommandHandler("approve", approve_cmd))',
'    app.add_handler(CommandHandler("approve", approve_cmd))\n'
'    app.add_handler(CommandHandler("runstage", runstage_cmd))'))

for old, new in REPL:
    assert t.count(old) >= 1, 'anchor not found: ' + old[:60]
    t = t.replace(old, new)
with open(p, 'w', encoding='utf-8') as f:
    f.write(t)
print('/runstage wired')