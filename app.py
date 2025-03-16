import os
import requests
import time
import logging
import telebot

from datetime import datetime
from dotenv import load_dotenv

from src.text_parser import TextParser, validate_url


load_dotenv(override=True)


BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
text_parser = TextParser(url=None, file_format=None)
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
    bot.reply_to(message, "Привет! Пришли мне URL сайта (т.е. 'https://example.com'), и я подскажу опции парсинга")


@bot.message_handler(commands=['status'])
def send_status(message):
    logger.info(f"User {message.chat.id} issued /status command")
    now = datetime.now()
    uptime = (now - start).total_seconds() // 60
    txt = f'status: running\nstart timestamp: {start}\nuptime: {uptime} minutes'
    bot.reply_to(message, txt)


@bot.callback_query_handler(lambda query: query.data == 'create_pdf')
def create_pdf(query):
    
    text_parser.set_file_format('pdf')

    url = validate_url(text_parser.url)
    filename = url.netloc.replace('.','_') + '.pdf'
    path = os.path.join('texts/', filename)

    text_parser(filename=filename, unique=True)
    
    # Send the PDF file to the user
    with open(path, 'rb') as file:
        bot.send_document(query.chat.id, file)
    logger.info(f"PDF file {filename} sent to user {query.chat.id}")

    bot.reply_to(query, f"Держи PDF файл: {filename}")


@bot.callback_query_handler(lambda query: query.data == 'create_txt')
def create_txt(query):
    
    text_parser.set_file_format('txt')

    url = validate_url(text_parser.url)
    filename = url.netloc.replace('.','_') + '.txt'
    path = os.path.join('texts/', filename)

    text_parser(filename=filename, unique=True)
    
    # Send the PDF file to the user
    with open(path, 'rb') as file:
        bot.send_document(query.chat.id, file)
    logger.info(f"TXT file {filename} sent to user {query.chat.id}")

    bot.reply_to(query, f"Держи TXT файл: {filename}")


@bot.callback_query_handler(lambda query: query.data == 'parse_links')
def parse_links(query):
    
    html = text_parser.download_html(text_parser.url)
    links = text_parser.get_html_links(html, internal_only=False)
    links ='\n'.join(links)



@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle user messages."""
    try:
        # Split the message into URL and filename
        logger.info(f"Received message from user {message.chat.id}: {message.text}")
        txt = message.text
        url = validate_url(txt)
        
        if url is None:
            logger.warning(f"Invalid input from user {message.chat.id}: {message.text}")
            bot.reply_to(message, "Пожалуйста отправь валидный URL (например 'https://example.com').")
            return
        
        text_parser.set_url(txt)
        
        bot.reply_to(message, "У меня есть следующий функционал: ")
    
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
