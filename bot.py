from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import sqlite3, random, string

# === ТВОЙ ТОКЕН (из BotFather) ===
TOKEN = "8642894333:AAEVcW8lJ6sCm1kN0yn2rrVECdDbQgUYgck"
WALLET = "0x44698049ad0be92e567cdfe9c5aa86d70047f73e"
NETWORK = "Ethereum (ERC20)"

# === БАЗА ДАННЫХ ===
conn = sqlite3.connect('clients.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (tg_id TEXT, pay_status TEXT, balance INTEGER, bought_time TEXT)''')
conn.commit()

app = Application.builder().token(TOKEN).build()

def gen_fake():
    return {
        'login': ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)),
        'pass': ''.join(random.choices(string.ascii_letters + string.digits, k=12)),
        'status': '❌ НЕДЕЙСТВИТЕЛЕН'
    }

async def start(update, context):
    kb = [
        [InlineKeyboardButton("🏦 Госуслуги + банки", callback_data='gos')],
        [InlineKeyboardButton("💎 Криптобиржи", callback_data='crypto')],
        [InlineKeyboardButton("📦 Комбо-пакет (3 в 1)", callback_data='combo')]
    ]
    await update.message.reply_text(
        "🔥 *AkkauntGuru* — доступы к госуслугам, банкам и биржам.\n"
        "Выбери пакет:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode='Markdown'
    )

async def buy(update, context):
    query = update.callback_query
    await query.answer()
    
    package = query.data
    prices = {'gos': 1500, 'crypto': 2500, 'combo': 3500}
    price = prices.get(package, 0)
    
    fake = gen_fake()
    context.user_data['fake_data'] = fake
    
    kb = [[InlineKeyboardButton("💰 Оплатить криптой", callback_data=f'pay_{package}')]]
    await query.edit_message_text(
        f"📌 *Данные для пакета {package}*:\n"
        f"Логин: `{fake['login']}`\n"
        f"Пароль: `{fake['pass']}`\n"
        f"Статус: {fake['status']}\n\n"
        f"💰 Цена: {price}₽ (~{round(price/90, 2)} USDT)\n"
        f"Переведи точную сумму на кошелёк:\n"
        f"`{WALLET}`\n"
        f"Сеть: {NETWORK}\n\n"
        f"После оплаты нажми кнопку ниже.",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode='Markdown'
    )

async def payment(update, context):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⏳ *Проверяем платеж...*\n\n"
        f"Логин: `{context.user_data['fake_data']['login']}`\n"
        f"Пароль: `{context.user_data['fake_data']['pass']}`\n\n"
        "⚠️ Если не заходит — попробуй через 5 минут.",
        parse_mode='Markdown'
    )

app.add_handler(CommandHandler('start', start))
app.add_handler(CallbackQueryHandler(buy, pattern='^(gos|crypto|combo)$'))
app.add_handler(CallbackQueryHandler(payment, pattern='^pay_'))

print("✅ Бот запущен!")
app.run_polling()
