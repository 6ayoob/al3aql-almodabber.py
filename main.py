import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import yfinance as yf
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_IDS = [7863509137]
bot = Bot(token=TOKEN)

app = Flask(__name__)

def is_golden_cross(df):
    # تقاطع صاعد عندما MA20 يقطع MA50 من الأسفل للأعلى
    return df['MA20'][-2] < df['MA50'][-2] and df['MA20'][-1] > df['MA50'][-1]

def check_stock(symbol):
    try:
        df = yf.download(symbol, period="60d")  # بيانات 60 يوم لاحتساب المتوسطات
        if df.empty or len(df) < 50:
            return False

        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['Volume_MA50'] = df['Volume'].rolling(window=50).mean()

        price = df['Close'][-1]
        volume = df['Volume'][-1]
        vol_ma50 = df['Volume_MA50'][-1]
        ma20 = df['MA20'][-1]
        ma50 = df['MA50'][-1]

        # الشروط
        if price > 1 and price > ma50 and volume > vol_ma50 and is_golden_cross(df):
            return True
        return False
    except Exception as e:
        print(f"خطأ في السهم {symbol}: {e}")
        return False

# قائمة أسهم ناسداك (هذه عينة، استبدلها بقائمة كاملة عندك)
nasdaq_symbols = [
    "AAPL", "MSFT", "AMZN", "TSLA", "NVDA", "GOOGL", "META", "ADBE", "INTC", "CMCSA",
    # أضف المزيد حتى تصل 200 سهم أو اقرأ من ملف symbols.txt
]

selected_stocks = []

for symbol in nasdaq_symbols[:200]:
    if check_stock(symbol):
        selected_stocks.append(symbol)

print("الأسهم التي تحقق الشروط:")
for stock in selected_stocks:
    print(stock)

# ✅ تقرير يومي تلقائي
def send_daily_report():
    chat_id = ALLOWED_IDS[0]
    try:
        response = requests.get("https://finnhub.io/api/v1/stock/symbol?exchange=US&token=cdsvj8qad3i9i37khudgcdsvj8qad3i9i37khue0")
        symbols = [item["symbol"] for item in response.json() if "." not in item["symbol"]]
        selected = []
        for symbol in symbols[:100]:
            quote = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token=cdsvj8qad3i9i37khudgcdsvj8qad3i9i37khue0").json()
            if all(k in quote for k in ("c", "pc", "v")):
                price = quote["c"]
                prev = quote["pc"]
                volume = quote["v"]
                if price and price < 7 and volume > 100000 and price > prev:
                    change = ((price - prev) / prev) * 100
                    selected.append(f"{symbol}: ${price:.2f} 🔼 {change:.2f}%")
        message = "\n".join(selected) if selected else "لا توجد أسهم تستوفي الشروط حاليًا."
        bot.send_message(chat_id=chat_id, text="📢 تقرير يومي عن الأسهم تحت 7 دولار:\n" + message)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text="حدث خطأ أثناء توليد التقرير.")

# ✅ جدولة التقرير اليومي
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, "cron", hour=15, minute=0, timezone=timezone("Asia/Riyadh"))
scheduler.start()

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def index():
    return "Bot is running!"

# ✅ تهيئة الأوامر
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("scan_stocks", scan_stocks))

# ✅ إعداد Webhook
if __name__ == "__main__":
    bot.set_webhook(url=f"https://al3aql-almodabber-py-2xic.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=1000)
