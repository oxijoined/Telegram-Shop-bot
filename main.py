import telebot
import psycopg2
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="mylog.log",
    encoding='utf-8',
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
)

load_dotenv()

telegramToken = os.getenv("TelegramToken")

bot = telebot.TeleBot(telegramToken, parse_mode='HTML', threaded=True)


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, 'hi')


bot.polling()
