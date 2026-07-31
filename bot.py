import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random, string

TOKEN = "8642894333:AAEVcW8lJ6sCm1kN0yn2rrVECdDbQgUYgck"
WALLET = "0x44698049ad0be92e567cdfe9c5aa86d70047f73e"

def gen_fake():
    return {
        'login': ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)),
        'pass': ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏦 Банки", callback_data='banks')],
        [InlineKeyboardButton("🏛 Госуслуги", callback_data='gosuslugi')],
        [InlineKeyboardButton("💳 Карты", callback_data='cards')],
        [InlineKeyboardButton("📊 Криптобиржи", callback_data='exchanges')],
        [InlineKeyboardButton("🛒 Маркетплейсы", callback_data='marketplaces')],
        [InlineKeyboardButton("📱 Соцсети", callback_data='social')],
        [InlineKeyboardButton("🎮 Игровые аккаунты", callback_data='games')],
        [InlineKeyboardButton("📧 Почтовые сервисы", callback_data='email')],
        [InlineKeyboardButton("💼 VPN/Прокси", callback_data='vpn')],
        [InlineKeyboardButton("📦 Комбо-пакет", callback_data='combo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔥 *AkkauntGuru* — доступы ко всему!\nВыбери категорию:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    package = query.data
    prices = {
        'banks': 1500, 'gosuslugi': 1200, 'cards': 2000,
        'exchanges': 2500, 'marketplaces': 1800, 'social': 800,
        'games': 1000, 'email': 500, 'vpn': 700, 'combo': 6000
    }
    names = {
        'banks': '🏦 Банки (Сбер, Тинькофф, ВТБ, Альфа)',
        'gosuslugi': '🏛 Госуслуги (полный доступ)',
        'cards': '💳 Карты (Visa/Mastercard с балансом)',
        'exchanges': '📊 Криптобиржи (Binance, Bybit, OKX)',
        'marketplaces': '🛒 Маркетплейсы (Ozon, Wildberries, Ali)',
        'social': '📱 Соцсети (Instagram, VK, Telegram)',
        'games': '🎮 Игровые аккаунты (Steam, Epic, Roblox)',
        'email': '📧 Почта (Gmail, Mail.ru, Яндекс)',
        'vpn': '💼 VPN/Прокси (готовые настройки)',
        'combo': '📦 КОМБО (все 9 категорий)'
    }
    
    price = prices.get(package, 0)
    name = names.get(package, 'Пакет')
    
    fake1 = gen_fake()
    fake2 = gen_fake() if package == 'combo' else None
    
    if fake2:
        context.user_data['fake_data'] = fake1
        context.user_data['fake_data2'] = fake2
    else:
        context.user_data['fake_data'] = fake1
    
    keyboard = [[InlineKeyboardButton("💰 Оплатить криптой", callback_data='pay')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if package == 'combo':
        text = (
            f"📌 *{name}*\n\n"
            f"🔹 Логин 1: `{fake1['login']}` | Пароль: `{fake1['pass']}`\n"
            f"🔹 Логин 2: `{fake2['login']}` | Пароль: `{fake2['pass']}`\n\n"
            f"💰 Цена: {price}₽ (~{round(price/90, 2)} USDT)\n"
            f"Переведи на кошелёк:\n`{WALLET}`\nСеть: Ethereum (ERC20)"
        )
    else:
        text = (
            f"📌 *{name}*\n\n"
            f"Логин: `{fake1['login']}`\n"
            f"Пароль: `{fake1['pass']}`\n\n"
            f"💰 Цена: {price}₽ (~{round(price/90, 2)} USDT)\n"
            f"Переведи на кошелёк:\n`{WALLET}`\nСеть: Ethereum (ERC20)"
        )
    
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    fake1 = context.user_data.get('fake_data', gen_fake())
    fake2 = context.user_data.get('fake_data2')
    
    if fake2:
        text = (
            "✅ *Оплата подтверждена!*\n\n"
            "Твои данные активированы:\n"
            f"🔹 Логин 1: `{fake1['login']}` | Пароль: `{fake1['pass']}`\n"
            f"🔹 Логин 2: `{fake2['login']}` | Пароль: `{fake2['pass']}`"
        )
    else:
        text = (
            "✅ *Оплата подтверждена!*\n\n"
            "Твои данные активированы:\n"
            f"Логин: `{fake1['login']}`\n"
            f"Пароль: `{fake1['pass']}`"
        )
    
    await query.edit_message_text(
        text=text,
        parse_mode='Markdown'
    )

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(buy, pattern='^(banks|gosuslugi|cards|exchanges|marketplaces|social|games|email|vpn|combo)$'))
    app.add_handler(CallbackQueryHandler(pay, pattern='^pay$'))
    
    print("✅ Бот с 10 услугами запущен!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
