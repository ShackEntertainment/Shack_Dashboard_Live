"""
SHACK ENTERTAINMENT — shack_ops_guard.py
Owner lock + graceful-fall for the Telegram bot.
Public faces never see raw errors; the MD is alerted privately.
"""
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
LAST_CHAT = os.path.join(project_root, 'configs', 'last_chat.txt')

def _seed():
    try:
        with open(LAST_CHAT) as f:
            return f.read().strip()
    except Exception:
        return ''

OWNER = os.getenv('TELEGRAM_OWNER_CHAT_ID') or _seed()

async def fail(update, label, e, bot=None):
    """Warm copy outward; the real error inward to the MD only."""
    try:
        await update.message.reply_text(
            "⚠️ A moment's grace — that hit a snag. It's logged and "
            "the MD is aware; try again shortly.")
    except Exception:
        pass
    detail = f"{type(e).__name__}: {e}"
    print(f"OPS ALERT — {label}: {detail}")
    try:
        if bot is not None and OWNER:
            await bot.send_message(
                int(OWNER), f"🚨 OPS ALERT — {label}: {detail}")
    except Exception:
        pass