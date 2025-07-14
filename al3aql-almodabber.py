import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# إعدادات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [658712542]

# مفاتيح API
FINNHUB_API_KEY = "d1qisl1r01qo4qd7h510d1qisl1r01qo4qd7h51g"
COINGECKO_API = "https://api.coingecko.com/api/v3"

# إعداد Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

# أوامر البوت
async def scan_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("🔍 جاري البحث عن الأسهم تحت 7 دولار...")

    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}"
    symbols = requests.get(url).json()

    results = []
    for stock in symbols:
        symbol = stock["symbol"]
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        data = requests.get(quote_url).json()
        price = data.get("c")
        if price and 0 < price < 7:
            results.append(f"{symbol} - ${price}")
        if len(results) >= 10:
            break

    msg = "أفضل الأسهم تحت ٧ دولار:\n" + "\n".join(results) if results else "❌ لا توجد أسهم حالياً."
    await update.message.reply_text(msg)

async def scan_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("💰 جاري فحص العملات الرقمية...")

    url = f"{COINGECKO_API}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    coins = requests.get(url).json()
    lines = [f"{c['name']} ({c['symbol'].upper()}): ${c['current_price']}" for c in coins]
    await update.message.reply_text("🪙 أفضل العملات الرقمية:\n" + "\n".join(lines))

# تشغيل البوت
async def main():
    app_telegram = Application.builder().token(BOT_TOKEN).build()
    app_telegram.add_handler(CommandHandler("scan_stocks", scan_stocks))
    app_telegram.add_handler(CommandHandler("scan_crypto", scan_crypto))
    await app_telegram.initialize()
    await app_telegram.start()
    await app_telegram.updater.start_polling()
    print("Telegram Bot is running...")

# تشغيل Flask وTelegram معًا
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    app.run(host="0.0.0.0", port=10000)
