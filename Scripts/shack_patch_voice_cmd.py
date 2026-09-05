import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_main_agent.py')
with open(p, encoding='utf-8') as f:
    lines = f.read().split('\n')

BLOCK = '''
import tempfile, json, re
from faster_whisper import WhisperModel
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

try:
    WHISPER_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
except Exception:
    WHISPER_MODEL = None

VOICE_DEALS = {"showcase": "DEAL-SHOWCASE01", "spirit": "DEAL-SPIRITCO", "paul": "DEAL-PND"}
NUM_MAP = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5"}

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != og.OWNER:
        return
    if WHISPER_MODEL is None:
        await update.message.reply_text("🔴 Whisper model failed to load.")
        return

    voice_file = await update.message.voice.get_file()
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tf:
        await voice_file.download_to_drive(tf.name)
        audio_path = tf.name

    try:
        segments, _ = WHISPER_MODEL.transcribe(audio_path, beam_size=5)
        text = " ".join([seg.text for seg in segments]).strip().lower()
    except Exception as e:
        text = ""
        await update.message.reply_text(f"🔴 Audio decode error (needs ffmpeg?): {e}")
    finally:
        os.unlink(audio_path)

    await update.message.reply_text(f"👂 Heard: '{text}'")

    action = "approve" if "approve" in text else "runstage" if "run stage" in text or "runstage" in text else "read" if "read" in text else None
    if not action:
        await update.message.reply_text("No command recognized. Say approve, run stage, or read.")
        return

    deal_code = next((v for k, v in VOICE_DEALS.items() if k in text), None)
    if not deal_code:
        await update.message.reply_text(f"Command '{action}' recognized, but no deal name heard.")
        return

    if action == "approve":
        card_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Data', 'deals', deal_code + '.json')
        if os.path.exists(card_p):
            with open(card_p, 'r') as f: card = json.load(f)
            nxt = card['status']['current_stage'] + 1
            tok = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Data', 'approvals', f'approved_{deal_code}-S{nxt}.token')
            open(tok, 'w').write('voice')
            await update.message.reply_text(f"🗣️ Token released: {deal_code}-S{nxt} approved.")
        else:
            await update.message.reply_text(f"Deal card {deal_code} not found.")
    else:
        context.args = [deal_code]
        if action == "read": await read_cmd(update, context)
        elif action == "runstage": await runstage_cmd(update, context)
'''

i = next((i for i, l in enumerate(lines) if l.startswith('async def runstage_cmd')), len(lines))
lines[i:i] = BLOCK.split('\n')

i = next((i for i, l in enumerate(lines) if 'CommandHandler("runstage"' in l), -1)
if i != -1:
    lines.insert(i + 1, '    app.add_handler(MessageHandler(filters.VOICE, handle_voice))')

with open(p, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('voice command patch applied')