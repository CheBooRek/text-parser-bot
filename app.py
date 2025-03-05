import os
import requests
import time
import telebot

from dotenv import load_dotenv

from src.text_parser import TextParser


load_dotenv(override=True)


BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
text_parser = TextParser()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Send a welcome message when the /start command is issued."""
    bot.reply_to(message, "Привет! Пришли мне URL сайта и название файла (т.е. 'https://example.com myfile.pdf'), и я сгенерю PDF с текстом с сайта.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle user messages."""
    try:
        # Split the message into URL and filename
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Пожалуйста отправь URL и наименование файла через пробел (т.е. 'https://example.com myfile.pdf').")
            return
        
        url, filename = parts
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        path = os.path.join('texts/', filename)
        
        text_parser(url=url, filename=filename)
        
        # Send the PDF file to the user
        with open(path, 'rb') as file:
            bot.send_document(message.chat.id, file)
        
        # Notify the user
        bot.reply_to(message, f"Держи PDF файл: {filename}")
    
    except requests.RequestException as e:
        bot.reply_to(message, f"Ошибка загрузки страницы: {e}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")


if __name__ == "__main__":
    # Start the bot
    print("Bot is running...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(15)
