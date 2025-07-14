import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
from flask import Flask
import asyncio

# إعدادات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [658712542]

# مفاتيح API
FINNHUB_API_KEY = "d1qisl1r01qo4qd7h510d1qisl1r01qo4qd7h51g"
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Flask وهمي لـ Render
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# أوامر البوت
async def scan_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    await update.message.reply_text("🔍 جاري البحث عن الأسهم تحت ٧ دولار...")

    symbols_url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}"
    symbols = requests.get(symbols_url).json()

    results = []
    for stock in symbols:
        symbol = stock.get("symbol")
        if not symbol:
            continue
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        data = requests.get(quote_url).json()
        current = data.get("c")

        if current and 0 < current < 7:
            results.append(f"{symbol} - ${current}")
        if len(results) >= 10:
            break

    if results:
        msg = "🟢 أفضل الأسهم تحت ٧ دولار:\n" + "\n".join(results)
    else:
        msg = "❌ لا توجد أسهم تحقق الشروط حالياً."

    await update.message.reply_text(msg)

async def scan_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    await update.message.reply_text("💰 جاري فحص العملات الرقمية...")

    url = f"{COINGECKO_API}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    response = requests.get(url).json()

    lines = [f"{coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}" for coin in response]
    await update.message.reply_text("🪙 أفضل العملات الرقمية:\n" + "\n".join(lines))

# تشغيل بوت تيليجرام بشكل غير متزامن داخل Flask
async def run_bot():
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(CommandHandler("scan_stocks", scan_stocks))
    app_telegram.add_handler(CommandHandler("scan_crypto", scan_crypto))
    await app_telegram.initialize()
    await app_telegram.start()
    print("Telegram Bot started.")
    await app_telegram.updater.start_polling()
    await app_telegram.updater.idle()

def start_async_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())

start_async_bot()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
