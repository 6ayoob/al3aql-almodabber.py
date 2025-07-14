from flask import Flask
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import asyncio

# إعدادات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [658712542]
FINNHUB_API_KEY = "d1qisl1r01qo4qd7h510d1qisl1r01qo4qd7h51g"
COINGECKO_API = "https://api.coingecko.com/api/v3"

app = Flask(__name__)
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

@app.route('/')
def home():
    return 'Bot is alive!'

# أوامر البوت
async def scan_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("🔍 جاري البحث عن الأسهم تحت 7 دولار...")

    try:
        symbols_url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}"
        symbols = requests.get(symbols_url).json()

        results = []
        for stock in symbols:
            symbol = stock["symbol"]
            quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
            data = requests.get(quote_url).json()
            current = data.get("c")
            if current and current < 7:
                results.append(f"{symbol} - ${current}")
            if len(results) >= 10:
                break

        msg = "📈 أفضل الأسهم تحت ٧ دولار:\n" + "\n".join(results) if results else "❌ لا توجد نتائج."
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

async def scan_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("💰 جاري فحص العملات الرقمية...")

    try:
        url = f"{COINGECKO_API}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
        response = requests.get(url).json()
        lines = [f"{coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}" for coin in response]
        await update.message.reply_text("🪙 أفضل العملات الرقمية:\n" + "\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# ربط الأوامر
bot_app.add_handler(CommandHandler("scan_stocks", scan_stocks))
bot_app.add_handler(CommandHandler("scan_crypto", scan_crypto))

# تشغيل البوت بشكل غير متزامن داخل Flask
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot_app.initialize())
    loop.run_until_complete(bot_app.start())
    loop.run_until_complete(bot_app.updater.start_polling())
    loop.run_forever()

import threading
threading.Thread(target=run_bot).start()
