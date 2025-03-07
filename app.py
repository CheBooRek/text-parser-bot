import os
import requests
import time
import logging
import telebot

from datetime import datetime
from dotenv import load_dotenv

from src.text_parser import TextParser


load_dotenv(override=True)


BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
start = datetime.now()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"logs/log_{start}.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)
logger = logging.getLogger(__name__)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Send a welcome message when the /start command is issued."""
    logger.info(f"User {message.chat.id} issued /start command")
    bot.reply_to(message, "Привет! Пришли мне URL сайта и название файла (т.е. 'https://example.com myfile.pdf'), и я сгенерю PDF с текстом с сайта.")


@bot.message_handler(commands=['status'])
def send_status(message):
    logger.info(f"User {message.chat.id} issued /status command")
    now = datetime.now()
    uptime = (now - start).total_seconds() // 60
    txt = f'status: running\nstart timestamp: {start}\nuptime: {uptime} minutes'
    bot.reply_to(message, txt)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle user messages."""
    try:
        # Split the message into URL and filename
        parts = message.text.split()
        logger.info(f"Received message from user {message.chat.id}: {message.text}")
        if len(parts) != 2:
            logger.warning(f"Invalid input from user {message.chat.id}: {message.text}")
            bot.reply_to(message, "Пожалуйста отправь URL и наименование файла через пробел (т.е. 'https://example.com myfile.pdf').")
            return
        
        url, filename = parts
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        path = os.path.join('texts/', filename)
        
        text_parser = TextParser(url=url, file_format='pdf')
        text_parser(filename=filename, unique=True)
        
        # Send the PDF file to the user
        with open(path, 'rb') as file:
            bot.send_document(message.chat.id, file)
        logger.info(f"PDF file {filename} sent to user {message.chat.id}")
        # Notify the user
        bot.reply_to(message, f"Держи PDF файл: {filename}")
    
    except requests.RequestException as e:
        error_message = f"Error downloading the page: {e}"
        logger.error(error_message)
        bot.reply_to(message, error_message)
    except Exception as e:
        error_message = f"An error occurred: {e}"
        logger.error(error_message)
        bot.reply_to(message, error_message)


if __name__ == "__main__":
    # Start the bot
    print("Bot is running...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(5)
