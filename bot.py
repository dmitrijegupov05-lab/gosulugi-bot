from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import sqlite3, random, string

TOKEN = "8642894333:AAEVcW8lJ6sCm1kN0yn2rrVECdDbQgUYgck"
WALLET = "0x44698049ad0be92e567cdfe9c5aa86d70047f73e"
NETWORK = "Ethereum (ERC20)"

conn = sqlite3.connect('clients.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (tg_id TEXT)''')
conn.commit()

def gen_fake():
    return {
        'login': ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)),
        'pass': ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    }

def start(update, context):
    kb = [[InlineKeyboardButton("🏦 Госуслуги", callback_data='gos')],
          [InlineKeyboardButton("💎 Криптобиржи", callback_data='crypto')]]
    update.message.reply_text("🔥 Выбери пакет:", reply_markup=InlineKeyboardMarkup(kb))

def buy(update, context):
    query = update.callback_query
    query.answer()
    fake = gen_fake()
    kb = [[InlineKeyboardButton("💰 Оплатить", callback_data='pay')]]
    query.edit_message_text(
        f"Логин: {fake['login']}\nПароль: {fake['pass']}\n\n"
        f"Оплати на кошелёк: {WALLET}\nСеть: {NETWORK}",
        reply_markup=InlineKeyboardMarkup(kb)
    )

def pay(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("⏳ Идёт проверка... Данные уже активированы!")

updater = Updater(TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(buy, pattern='^(gos|crypto)$'))
updater.dispatcher.add_handler(CallbackQueryHandler(pay, pattern='^pay$'))

print("✅ Бот запущен!")
updater.start_polling()
updater.idle()
