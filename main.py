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
import requests
import time

API_TOKEN = "d1qisl1r01qo4qd7h510d1qisl1r01qo4qd7h51g"

def get_candles(symbol):
    to_time = int(time.time())
    from_time = to_time - 60*60*24*90  # 90 يوم تقريباً (ثلاثة أشهر)
    url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=D&from={from_time}&to={to_time}&token={API_TOKEN}"
    resp = requests.get(url).json()
    if resp.get('s') != 'ok':
        return None
    return resp

def moving_average(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period

def is_golden_cross(close_prices):
    if len(close_prices) < 50:
        return False
    ma20_yesterday = moving_average(close_prices[:-1], 20)
    ma50_yesterday = moving_average(close_prices[:-1], 50)
    ma20_today = moving_average(close_prices, 20)
    ma50_today = moving_average(close_prices, 50)
    if ma20_yesterday is None or ma50_yesterday is None:
        return False
    return ma20_yesterday < ma50_yesterday and ma20_today > ma50_today

def check_stock(symbol):
    quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_TOKEN}"
    quote = requests.get(quote_url).json()
    if not all(k in quote for k in ("c", "v")):
        return False

    price = quote["c"]
    volume = quote["v"]
    if price <= 1:
        return False

    candles = get_candles(symbol)
    if not candles:
        return False

    close_prices = candles['c']
    volume_ma50 = sum(candles['v'][-50:]) / 50 if len(candles['v']) >= 50 else None

    if volume_ma50 is None or volume <= volume_ma50:
        return False

    if price <= moving_average(close_prices, 50):
        return False

    if not is_golden_cross(close_prices):
        return False

    return True

# استخدامك للقائمة:
symbols = ["AAPL", "MSFT", "TSLA", "AMZN", ...]  # حمل الرموز من ملف مثلا
selected = []

for sym in symbols[:200]:
    if check_stock(sym):
        selected.append(sym)

print("Selected stocks:", selected)

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
