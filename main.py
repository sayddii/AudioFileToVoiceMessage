#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import telebot
from telebot import apihelper
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '8144294582:AAHKrqBxbvuFrCVnUbUTlXqmReg0qPx0_pQ'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start_command_handler(message):
    """Handle /start and /help commands"""
    text = "Just send an audio message and I'll convert it to a voice message for you."
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode='Markdown'
    )

@bot.message_handler(content_types=['audio'])
def audio_handler(message):
    """Convert audio messages to voice messages"""
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
            "Sorry, I couldn't process that audio. Please try again."
        )

def run_bot():
    """Run the bot with proper error handling and conflict resolution"""
    while True:
        try:
            logger.info("Starting bot polling...")
            bot.infinity_polling(
                skip_pending=True,  # Skip pending updates on restart
                interval=2,        # Longer interval between checks
                timeout=30          # Longer timeout
            )
        except apihelper.ApiTelegramException as api_error:
            if "Conflict" in str(api_error):
                logger.warning("Bot conflict detected. Waiting 10 seconds before restarting...")
                time.sleep(10)
            else:
                logger.error(f"Telegram API error: {api_error}")
                time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {e}. Restarting in 10 seconds...")
            time.sleep(10)
        else:
            break  # Exit loop if bot stopped intentionally

if __name__ == '__main__':
    logger.info("Starting voice converter bot...")
    run_bot()