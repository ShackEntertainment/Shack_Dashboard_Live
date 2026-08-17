import telebot
import sqlite3
import os
import time
import whisper
import asyncio
import edge_tts
from dotenv import load_dotenv

load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = telebot.TeleBot(TOKEN)

# Absolute path to ffmpeg
FFMPEG_PATH = r'C:\Users\Bola\Documents\Shack_Project\ffmpeg.exe'

print("Loading local Whisper model...")
whisper_model = whisper.load_model("tiny")
print("✅ Whisper loaded!")

# British male voice - David (very natural)
VOICE = "en-GB-RyanNeural"  # British male
# Other options: "en-GB-SoniaNeural" (British female), "en-US-GuyNeural" (US male)

def get_db():
    db_path = 'executive_cache.db'
    if not os.path.exists(db_path): return None
    return sqlite3.connect(db_path)

async def generate_audio_response(text):
    """Generate natural audio using Microsoft Edge TTS"""
    try:
        audio_file = "response_audio.mp3"
        
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(audio_file)
        
        return audio_file
    except Exception as e:
        print(f"TTS error: {e}")
        return None

def query_db(question):
    conn = get_db()
    if not conn: return "Database not found."
    cursor = conn.cursor()
    q = question.lower()
    
    try:
        if 'revenue' in q:
            le_rev = au_rev = 0.0
            try:
                cursor.execute("SELECT SUM(total_price) FROM le_bookings")
                res = cursor.fetchone()
                if res and res[0]: le_rev = float(res[0])
            except: pass
            try:
                cursor.execute("SELECT SUM(retail_price * units_sold) FROM au_products")
                res = cursor.fetchone()
                if res and res[0]: au_rev = float(res[0])
            except: pass
            return f"Total revenue is £{le_rev + au_rev:,.2f}. Live Exchange: £{le_rev:,.2f}. Artists Unlimited: £{au_rev:,.2f}."
        elif 'product' in q or 'stock' in q:
            cursor.execute("SELECT product_name, retail_price, current_stock FROM au_products WHERE current_stock > 0 LIMIT 5")
            rows = cursor.fetchall()
            if rows:
                resp = f"We have {len(rows)} products. "
                for r in rows: 
                    resp += f"{r[0]} £{r[1]:,.2f} stock:{r[2]}. "
                return resp
            return "No products in stock."
        elif 'event' in q:
            cursor.execute("SELECT event_name, event_date, venue_name, tickets_sold, capacity_total FROM le_events LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                resp = f"We have {len(rows)} upcoming events. "
                for r in rows:
                    resp += f"{r[0]} on {r[1]} at {r[2]}. "
                return resp
            return "No events scheduled."
        else:
            return "I can help with revenue, products, events. What would you like to know?"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        conn.close()

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    print(f"🎤 Voice message received")
    try:
        bot.reply_to(message, " Processing voice...")
        
        # Download voice file
        print("  Downloading...")
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open('voice_message.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Convert OGG to WAV
        print("  Converting...")
        import subprocess
        subprocess.run(
            [FFMPEG_PATH, '-i', 'voice_message.ogg', '-y', 'voice_message.wav'], 
            check=True, capture_output=True
        )
        
        # Transcribe
        print("  Transcribing...")
        result = whisper_model.transcribe("voice_message.wav")
        question = result["text"]
        print(f"  You said: '{question}'")
        
        bot.reply_to(message, f"🎤 You said: {question}")
        
        # Query database
        print("  Querying...")
        answer = query_db(question)
        print(f"  Answer: {answer}")
        
        # Generate audio with Edge TTS
        print("  Generating natural voice audio...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_file = loop.run_until_complete(generate_audio_response(answer))
        loop.close()
        
        if audio_file and os.path.exists(audio_file):
            with open(audio_file, 'rb') as audio:
                bot.send_voice(message.chat.id, audio)
            os.remove(audio_file)
            print("  Audio sent!")
        
        bot.reply_to(message, answer)
        
        # Cleanup
        for f in ['voice_message.ogg', 'voice_message.wav']:
            if os.path.exists(f): os.remove(f)
        
    except Exception as e:
        error_msg = f"❌ Voice error: {str(e)}"
        print(error_msg)
        bot.reply_to(message, error_msg)

@bot.message_handler(commands=['start', 'help', 'products', 'revenue', 'events'])
def handle_commands(message):
    cmd = message.text.split()[0].replace('/', '')
    if cmd == 'products':
        bot.reply_to(message, query_db("show products"))
    elif cmd == 'revenue':
        bot.reply_to(message, query_db("total revenue"))
    elif cmd == 'events':
        bot.reply_to(message, query_db("upcoming events"))
    else:
        bot.reply_to(message, " Shack Finance Bot\nSend voice or text!\n/products\n/revenue\n/events")

print("="*50)
print(" Shack Voice Bot with NATURAL VOICE READY!")
print(f"Voice: {VOICE} (British Male)")
print("="*50)

while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"Connection error: {e}")
        time.sleep(10)