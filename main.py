#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import threading
import telebot
import logging
from flask import Flask

# Initialize Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running", 200

@app.route('/health')
def health_check():
    return "OK", 200

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')
if not TOKEN:
    logger.error("Missing TOKEN environment variable")
    exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start_command_handler(message):
    bot.reply_to(message, "🎧 Send me an audio file to convert to voice message!")

@bot.message_handler(content_types=['audio'])
def audio_handler(message):
    try:
        file_info = bot.get_file(message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        bot.send_voice(
            message.chat.id,
            downloaded_file,
            reply_to_message_id=message.message_id
        )
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        bot.reply_to(message, "⚠️ Error processing audio. Please try again.")

def run_bot():
    while True:
        try:
            logger.info("Starting bot with webhook...")
            # Critical change: Use webhook instead of polling
            bot.remove_webhook()
            time.sleep(1)
            bot.set_webhook(url="https://your-render-url.onrender.com/" + TOKEN)
            break
        except Exception as e:
            logger.error(f"Webhook setup failed: {e}. Retrying in 10s...")
            time.sleep(10)

if __name__ == '__main__':
    # Start Flask in a thread
    flask_thread = threading.Thread(
        target=app.run,
        kwargs={
            'host': '0.0.0.0',
            'port': int(os.getenv('PORT', 5000)),
            'debug': False,
            'use_reloader': False
        },
        daemon=True
    )
    flask_thread.start()
    
    # Setup webhook
    run_bot()
    
    # Keep the application running
    while True:
        time.sleep(1000)
