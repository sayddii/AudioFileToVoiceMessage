#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import telebot
from telebot import apihelper
import logging
from flask import Flask  # Required for Render health checks

# Initialize Flask app for Render health checks
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health_check():
    return "OK", 200

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')  # Get token from environment variable
if not TOKEN:
    logger.error("No TOKEN found in environment variables!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start_command_handler(message):
    text = (
        "🎧 Audio to Voice Converter Bot\n\n"
        "Just send me an audio file and I'll convert it to a Telegram voice message!\n\n"
        "Features:\n"
        "- 24/7 online via Render.com\n"
        "- Supports MP3, OGG, WAV\n"
        "- Preserves captions"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['audio'])
def audio_handler(message):
    try:
        file_info = bot.get_file(message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        bot.send_voice(
            chat_id=message.chat.id,
            voice=downloaded_file,
            caption=message.caption,
            caption_entities=message.caption_entities,
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        bot.reply_to(
            message,
            "⚠️ Error processing audio. Please try again or send a different file."
        )

def run_bot():
    """Run bot with Render-compatible configuration"""
    while True:
        try:
            logger.info("Starting bot polling...")
            bot.infinity_polling(
                skip_pending=True,
                interval=2,
                timeout=30,
                restart_on_change=True  # Critical for 24/7 operation
            )
        except apihelper.ApiTelegramException as api_error:
            if "Conflict" in str(api_error):
                logger.warning("Conflict detected. Restarting in 10s...")
                time.sleep(10)
            else:
                logger.error(f"API Error: {api_error}")
                time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(10)

if __name__ == '__main__':
    # Start Flask server for Render health checks
    import threading
    threading.Thread(
        target=app.run,
        kwargs={'host': '0.0.0.0', 'port': int(os.getenv('PORT', 5000))}
    ).start()
    
    # Start the bot
    run_bot()
