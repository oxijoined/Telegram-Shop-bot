import json
import logging
import os

import psycopg2
import telebot
from dotenv import load_dotenv
from keyboa import Keyboa

logging.basicConfig(
    level=logging.DEBUG,
    filename="Log.log",
    encoding='utf-8',
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
)

with open("config.jsonc", "r", encoding="utf-8") as f:
    config = json.loads(f.read())

try:
    conn = psycopg2.connect(
        database=config["Database"]["Name"],
        user=config["Database"]["User"],
        password=config["Database"]["Password"],
        host=config["Database"]["Host"],
    )
    conn.autocommit = True
except Exception as ex:
    logging.info("[X] Error in connection to database.")
    logging.error(ex)

load_dotenv()


telegramToken = os.getenv("TelegramToken")

bot = telebot.TeleBot(telegramToken, parse_mode='HTML', threaded=True)


class Customer:
    def __init__(self, TelegramID) -> None:
        self.TelegramID = TelegramID

    def isExist(self):
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM Users WHERE tgid = {self.TelegramID}")
            data = cur.fetchone()
        return data is not None

    def createNewUser(self):
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO Users(tgid,balance) VALUES ({self.TelegramID},0)")

    @property
    def balance(self):
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT balance FROM Users WHERE tgid = {self.TelegramID}")
            data = cur.fetchone()[0]
        return 0 if data is None else data

    @balance.setter
    def balance(self, value):
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE Users SET balance = {value} WHERE tgid = {self.TelegramID}")

    def sendKeyboard(self):
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row(config['Buttons']['Buy'])
        keyboard.row(config['Buttons']['Profile'], config['Buttons']['Stock'])
        bot.send_message(self.TelegramID, "ᅠ", reply_markup=keyboard)

    @property
    def id(self):
        return self.TelegramID

    @property
    def firstName(self):
        return self.TelegramID


def BuyHandler(id, message):
    user = Customer(id)
    bot.send_message(user.id, 'hi')


def ProfileHandler(id, message):
    user = Customer(id)
    msg = f"""
<code>{message.from_user.first_name}</code>, привет!
Баланс:  <code>{user.balance}₽</code>
    """
    bot.reply_to(message, msg)


def StockHandler(id, message):
    user = Customer(id)
    bot.send_message(user.id, 'hi3')


@bot.message_handler(commands=['start'])
def startHandler(message):
    user = Customer(message.chat.id)
    if not user.isExist():
        user.createNewUser()
    user.sendKeyboard()


@bot.message_handler(content_types=['text'])
def menuHandler(message):
    user = Customer(message.chat.id)
    if message.text == config['Buttons']['Buy']:
        BuyHandler(user.id, message)
    elif message.text == config['Buttons']['Profile']:
        ProfileHandler(user.id, message)
    elif message.text == config['Buttons']['Stock']:
        StockHandler(user.id, message)


bot.polling()
