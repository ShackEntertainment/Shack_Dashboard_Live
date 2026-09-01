"""
SHACK ENTERTAINMENT — shack_patch_guard.py
Owner lock + graceful-fall onto shack_main_agent.py.
"""
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_main_agent.py')
with open(p, encoding='utf-8') as f:
    t = f.read()

REPL = []
REPL.append((
"from telegram.ext import Application, CommandHandler, MessageHandler, filters",
"from telegram.ext import (Application, CommandHandler, MessageHandler,\n"
"                          filters, ApplicationHandlerStop)"))
REPL.append((
"import shack_outline_dig as dig",
"import shack_outline_dig as dig\nimport shack_ops_guard as og"))
REPL.append((
"async def remember(update: Update, context):",
"async def owner_gate(update: Update, context):\n"
"    cid = str(update.effective_chat.id) if update.effective_chat else ''\n"
"    if cid != og.OWNER:\n"
"        try:\n"
"            if update.message is not None:\n"
"                await update.message.reply_text(\n"
"                    \"🔒 This bot is private to the Shack office.\")\n"
"        except Exception:\n"
"            pass\n"
"        raise ApplicationHandlerStop\n"
"\n"
"async def remember(update: Update, context):"))
REPL.append((
"    app.add_handler(MessageHandler(filters.ALL, remember), group=-1)",
"    app.add_handler(MessageHandler(filters.ALL, owner_gate), group=-2)\n"
"    app.add_handler(MessageHandler(filters.ALL, remember), group=-1)"))
REPL.append((
"""    except Exception as e:
        traceback.print_exc()
        try:
            await update.message.reply_text(
                f"❌ {label} error: {type(e).__name__}: {e}")
        except Exception:
            pass""",
"""    except Exception as e:
        traceback.print_exc()
        await og.fail(update, label, e, context.bot)"""))
REPL.append((
"""        try:
            await update.message.reply_text(f"❌ Finance error: {e}")
        except Exception:
            pass""",
"        await og.fail(update, 'Finance', e, context.bot)"))
REPL.append((
"""        try:
            await update.message.reply_text(f"❌ Finance Agent error: {e}")
        except Exception:
            pass""",
"        await og.fail(update, 'Finance Agent', e, context.bot)"))
REPL.append((
"""        traceback.print_exc()
        await update.message.reply_text(f"❌ Ledger error: {e}")
        return""",
"""        traceback.print_exc()
        await og.fail(update, 'Ledger', e, context.bot)
        return"""))
REPL.append((
'        await update.message.reply_text(f"❌ Calendar error: {e}")',
"        await og.fail(update, 'Calendar', e, context.bot)"))
REPL.append((
"""        try:
            await context.bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=thinking.message_id,
                text=f"❌ Intake error: {e}")
        except Exception:
            pass""",
"        await og.fail(update, 'Intake', e, context.bot)"))
REPL.append((
"""        try:
            await update.message.reply_text(f"❌ Intake error: {e}")
        except Exception:
            pass""",
"        await og.fail(update, 'Intake', e, context.bot)"))
REPL.append((
'        await update.message.reply_text("ERROR: " + str(e))',
"        await og.fail(update, 'Sales', e, context.bot)"))
REPL.append((
"    chat = _last_chat()",
"    chat = og.OWNER"))
REPL.append((
"""    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text("Usage: /senddraft <draft_id>")
        return
    result = await asyncio.to_thread(mb.send_draft, parts[1].strip())""",
"""    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text("Usage: /senddraft <draft_id>")
        return
    if str(update.effective_chat.id) != og.OWNER:
        await update.message.reply_text("🔒 Approval commands are MD-only.")
        return
    result = await asyncio.to_thread(mb.send_draft, parts[1].strip())"""))

for old, new in REPL:
    n = t.count(old)
    assert n >= 1, 'anchor not found: ' + old[:60]
    t = t.replace(old, new)
with open(p, 'w', encoding='utf-8') as f:
    f.write(t)
print('guard patched: owner lock + graceful-fall live')