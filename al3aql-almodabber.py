import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
import asyncio

# إعدادات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [658712542]

# API
FINNHUB_API_KEY = "d1qisl1r01qo4qd7h510d1qisl1r01qo4qd7h51g"
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# ====== Telegram Commands ======

async def scan_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("🔍 جاري البحث عن الأسهم تحت 7 دولار...")

    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}"
    symbols = requests.get(url).json()

    results = []
    for stock in symbols:
        symbol = stock["symbol"]
        q = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        data = requests.get(q).json()
        price = data.get("c")
        if price and price < 7:
            results.append(f"{symbol} - ${price}")
        if len(results) >= 10:
            break

    msg = "أفضل الأسهم تحت ٧ دولار:\n" + "\n".join(results) if results else "❌ لا توجد نتائج حالياً."
    await update.message.reply_text(msg)

async def scan_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("💰 جاري فحص العملات الرقمية...")

    url = f"{COINGECKO_API}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    coins = requests.get(url).json()
    msg = "🪙 أفضل العملات:\n" + "\n".join(
        f"{coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}" for coin in coins
    )
    await update.message.reply_text(msg)

# ====== Main Runner ======
def run_bot():
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(CommandHandler("scan_stocks", scan_stocks))
    app_telegram.add_handler(CommandHandler("scan_crypto", scan_crypto))

    loop = asyncio.get_event_loop()
    loop.create_task(app_telegram.initialize())
    loop.create_task(app_telegram.start())
    loop.create_task(app_telegram.updater.start_polling())
    return loop

if __name__ == '__main__':
    loop = run_bot()
    app.run(host='0.0.0.0', port=10000)
    loop.run_forever()
