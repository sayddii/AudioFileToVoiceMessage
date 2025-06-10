import os
from flask import Flask, request
import telebot
import logging

# Initialize
app = Flask(__name__)
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return "Bot is running", 200

@app.route('/health')
def health_check():
    return "OK", 200

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Bad request', 400

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, "Send me an audio file to convert to voice message!")

@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    try:
        file_info = bot.get_file(message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        bot.send_voice(message.chat.id, downloaded_file)
    except Exception as e:
        logger.error(f"Error: {e}")
        bot.reply_to(message, "Error processing audio")

if __name__ == '__main__':
    # Remove and set new webhook
    bot.remove_webhook()
    bot.set_webhook(url=f"https://your-render-service.onrender.com/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
