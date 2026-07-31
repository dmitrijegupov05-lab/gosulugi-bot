from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import random, string

TOKEN = "8642894333:AAEVcW8lJ6sCm1kN0yn2rrVECdDbQgUYgck"
WALLET = "0x44698049ad0be92e567cdfe9c5aa86d70047f73e"

def gen_fake():
    return {
        'login': ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)),
        'pass': ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    }

def start(bot, update):
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
    update.message.reply_text(
        "🔥 *AkkauntGuru* — доступы ко всему!\nВыбери категорию:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def buy(bot, update):
    query = update.callback_query
    query.answer()
    
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
    
    context = update.callback_query.message.chat_id
    if fake2:
        text = (
            f"📌 *{name}*\n\n"
            f"🔹 Логин 1: `{fake1['login']}` | Пароль: `{fake1['pass']}`\n"
            f"🔹 Логин 2: `{fake2['login']}` | Пароль: `{fake2['pass']}`\n\n"
            f"💰 Цена: {price}₽ (~{round(price/90, 2)} USDT)\n"
            f"Переведи на кошелёк:\n`{WALLET}`\nСеть: Ethereum (ERC20)\n\n"
            f"После оплаты нажми кнопку ниже."
        )
    else:
        text = (
            f"📌 *{name}*\n\n"
            f"Логин: `{fake1['login']}`\n"
            f"Пароль: `{fake1['pass']}`\n\n"
            f"💰 Цена: {price}₽ (~{round(price/90, 2)} USDT)\n"
            f"Переведи на кошелёк:\n`{WALLET}`\nСеть: Ethereum (ERC20)\n\n"
            f"После оплаты нажми кнопку ниже."
        )
    
    keyboard = [[InlineKeyboardButton("💰 Оплатить криптой", callback_data='pay')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def pay(bot, update):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="✅ *Оплата подтверждена!*\n\n"
             "Твои данные активированы.\n"
             "⚠️ Если не заходит — подожди 5-10 минут.",
        parse_mode='Markdown'
    )

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(buy, pattern='^(banks|gosuslugi|cards|exchanges|marketplaces|social|games|email|vpn|combo)$'))
    dp.add_handler(CallbackQueryHandler(pay, pattern='^pay$'))
    
    print("✅ Бот с 10 услугами запущен!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
