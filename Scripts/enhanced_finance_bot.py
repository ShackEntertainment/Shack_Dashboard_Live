import telebot
import sqlite3
import os
import time
import whisper
import pyttsx3
import subprocess
from dotenv import load_dotenv

load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = telebot.TeleBot(TOKEN)

print("Loading local Whisper model (this may take a minute on first run)...")
# Using 'tiny' for speed. You can change to 'base' or 'small' for better accuracy later.
whisper_model = whisper.load_model("tiny")
print("✅ Whisper loaded!")

# Initialize local text-to-speech engine
tts_engine = pyttsx3.init()
# Optional: Set a slightly faster rate
tts_engine.setProperty('rate', 150) 

def get_db():
    db_path = 'executive_cache.db'
    if not os.path.exists(db_path): return None
    return sqlite3.connect(db_path)

def parse_currency(value):
    if value is None: return 0.0
    try: return float(str(value).replace('£', '').replace(',', ''))
    except: return 0.0

def generate_audio_response(text):
    """Generate audio using local pyttsx3"""
    try:
        audio_file = "response_audio.mp3"
        tts_engine.save_to_file(text, audio_file)
        tts_engine.runAndWait()
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
            
            total = le_rev + au_rev
            return f"Total revenue is £{total:,.2f}. Live Exchange: £{le_rev:,.2f}. Artists Unlimited: £{au_rev:,.2f}."

        elif 'product' in q or 'stock' in q:
            cursor.execute("SELECT product_name, retail_price, current_stock FROM au_products WHERE current_stock > 0 LIMIT 5")
            rows = cursor.fetchall()
            if rows:
                resp = f"We have {len(rows)} products in stock. "
                for r in rows: 
                    resp += f"{r[0]}, priced at £{r[1]:,.2f}, with {r[2]} units available. "
                return resp
            return "No products currently in stock."

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
            return "I can help you with revenue, products, events, and more. What would you like to know?"
            
    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        conn.close()

# Handle voice messages
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        bot.reply_to(message, " Processing voice...")
        
        # 1. Download voice file
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open('voice_message.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # 2. Convert OGG to WAV using local ffmpeg
        # We use .\ffmpeg.exe since it's in your Shack_Project folder
        subprocess.run(['.\ffmpeg.exe', '-i', 'voice_message.ogg', '-y', 'voice_message.wav'], 
                      check=True, capture_output=True)
        
        # 3. Transcribe with LOCAL Whisper
        print("Transcribing...")
        result = whisper_model.transcribe("voice_message.wav")
        question = result["text"]
        print(f"Transcribed: {question}")
        
        bot.reply_to(message, f" You said: {question}")
        
        # 4. Process the question
        answer = query_db(question)
        
        # 5. Generate audio response (local TTS)
        audio_file = generate_audio_response(answer)
        
        if audio_file and os.path.exists(audio_file):
            with open(audio_file, 'rb') as audio:
                bot.send_voice(message.chat.id, audio)
            os.remove(audio_file)
        
        # Also send text
        bot.reply_to(message, answer)
        
        # Cleanup
        if os.path.exists('voice_message.ogg'):
            os.remove('voice_message.ogg')
        if os.path.exists('voice_message.wav'):
            os.remove('voice_message.wav')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Voice processing error: {str(e)}")
        print(f"Voice error: {e}")

# Handle text commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, " **Shack Finance Bot with Local Voice**\n\nSend text or voice messages!\n/revenue\n/products\n/events\n/status")

@bot.message_handler(commands=['revenue', 'products', 'events'])
def handle_commands(message):
    cmd = message.text.split()[0].replace('/', '')
    queries = {
        'revenue': "What's our total revenue?",
        'products': "What products are in stock?",
        'events': "What events do we have?"
    }
    
    answer = query_db(queries.get(cmd, ""))
    bot.reply_to(message, answer)

print("="*50)
print(" Shack Finance Bot with LOCAL VOICE starting...")
print("No API costs - running locally!")
print("="*50)

while True:
    try:
        bot.polling()
    except Exception as e:
        print(f"Connection error: {e}")
        time.sleep(10)