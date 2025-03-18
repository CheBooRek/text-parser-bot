import os
import requests
import time
import logging
import telebot

from datetime import datetime
from dotenv import load_dotenv

from src.text_parser import TextParser
from src.utils import validate_url, build_filename


load_dotenv(override=True)


BOT_TOKEN = os.getenv('BOT_PROD')
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


def create_file(message, ext='pdf'):

    try:
        text_parser.set_file_format(ext)
        _, url_raw = message.text.split()
        url = validate_url(url_raw)
        if url is None:
            logger.warning(f"Invalid input from user {message.chat.id}: {message.text}")
            bot.reply_to(message, f"Пожалуйста отправь валиднyю команду (например '/{ext} https://example.com').")
            return

        text_parser.set_url(url.geturl())
        filename = build_filename(url, ext)
        path = os.path.join('texts/', filename)

        text_parser(filename=filename, unique=True)
        
        # Send the PDF file to the user
        with open(path, 'rb') as file:
            bot.send_document(message.chat.id, file)
        logger.info(f"{ext} file {filename} sent to user {message.chat.id}")

        bot.reply_to(message, f"Держи {ext} файл: {filename}")

    except requests.RequestException as e:
        error_message = f"Error downloading the page: {e}"
        logger.error(error_message)
        bot.reply_to(message, error_message)
    except Exception as e:
        error_message = f"An error occurred: {e}"
        logger.error(error_message)
        bot.reply_to(message, error_message)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Send a welcome message when the /start command is issued."""
    logger.info(f"User {message.chat.id} issued /start or /help command")
    msg = """Привет! Я бот, который умеет парсить текст с сайтов, мои команды:
        /start, /help - выводит данное сообщение
        /pdf <url> (например '/pdf https://example.com') - я собираю с предоставленного URL весь текст и возвращаю файл в формате PDF
        /txt <url> (например '/txt https://example.com') - я собираю с предоставленного URL весь текст и возвращаю файл в формате TXT
        /links <url> (например '/links https://example.com') - я собираю все внутренние ссылки 1 уровня с сайта и присылаю обратным сообщением
        /status - возвращает техническое сообщение о статусе бота (проверка работы)
    """
    bot.reply_to(message, msg)


@bot.message_handler(commands=['status'])
def send_status(message):
    logger.info(f"User {message.chat.id} issued /status command")
    now = datetime.now()
    uptime = (now - start).total_seconds() // 60
    txt = f'status: running\nstart timestamp: {start}\nuptime: {uptime} minutes'
    bot.reply_to(message, txt)


@bot.message_handler(commands=['pdf'])
def create_pdf(message):
    create_file(message, 'pdf')


@bot.message_handler(commands=['txt'])
def create_txt(message):
    create_file(message, 'txt')


@bot.message_handler(commands=['links'])
def parse_links(message):

    try:
        _, url_raw = message.text.split()
        url = validate_url(url_raw)
        if url is None:
            logger.warning(f"Invalid input from user {message.chat.id}: {message.text}")
            bot.reply_to(message, "Пожалуйста отправь валиднyю команду (например '/txt https://example.com').")
            return
        text_parser.set_url(url.geturl())
        html = text_parser.download_html(text_parser.url)
        links = text_parser.get_html_links(html, internal_only=True)
        links ='\n'.join(links)

        bot.reply_to(message, f"Держи внутренние ссылки: \n{links}")

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
