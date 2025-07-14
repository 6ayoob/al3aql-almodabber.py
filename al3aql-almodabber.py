from flask import Flask
import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# إعدادات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [658712542]
FINNHUB_API_KEY = "d1qisl1r01qo4qd7h510d1qisl1r01qo4qd7h51g"
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Flask وهمي لـ Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

# أوامر Telegram
async def scan_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    await update.message.reply_text("🔍 جاري البحث عن الأسهم تحت ٧ دولار...")

    url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}"
    try:
        symbols = requests.get(url).json()
    except:
        await update.message.reply_text("❌ فشل في تحميل رموز الأسهم.")
        return

    results = []
    for stock in symbols:
        symbol = stock.get("symbol")
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        try:
            quote = requests.get(quote_url).json()
            price = quote.get("c")
            if price and price < 7:
                results.append(f"{symbol} - ${price}")
                if len(results) >= 10:
                    break
        except:
            continue

    if results:
        msg = "📉 أفضل الأسهم تحت ٧ دولار:\n" + "\n".join(results)
    else:
        msg = "❌ لا توجد أسهم تحقق الشروط حالياً."
    
    await update.message.reply_text(msg)

async def scan_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    await update.message.reply_text("💰 جاري فحص العملات الرقمية...")

    url = f"{COINGECKO_API}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    try:
        data = requests.get(url).json()
        msg = "🪙 أفضل 10 عملات رقمية:\n"
        msg += "\n".join([f"{coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}" for coin in data])
    except:
        msg = "❌ فشل في تحميل بيانات العملات."

    await update.message.reply_text(msg)

# بدء البوت
async def main():
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(CommandHandler("scan_stocks", scan_stocks))
    app_telegram.add_handler(CommandHandler("scan_crypto", scan_crypto))
    await app_telegram.initialize()
    await app_telegram.start()
    await app_telegram.updater.start_polling()
    await app_telegram.updater.idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    app.run(host="0.0.0.0", port=10000)
