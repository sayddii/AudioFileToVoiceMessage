#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import threading
import telebot
from telebot import apihelper
import logging

# Initialize Flask app
from flask import Flask
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

TOKEN = os.getenv('TOKEN')
if not TOKEN:
    logger.error("Missing TOKEN environment variable")
    exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start_command_handler(message):
    bot.reply_to(message, "🎧 Send me an audio file to convert it to a voice message!")

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
        logger.error(f"Audio processing failed: {e}")
        bot.reply_to(message, "⚠️ Conversion failed. Please try another file.")

def run_bot():
    while True:
        try:
            logger.info("Starting bot polling...")
            # Remove restart_on_change for stability
            bot.infinity_polling(
                skip_pending=True,
                interval=2,
                timeout=30
            )
        except Exception as e:
            logger.error(f"Bot crashed: {e}. Restarting in 10s...")
            time.sleep(10)

if __name__ == '__main__':
    # Start Flask server
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
    
    # Start bot
    run_bot()
