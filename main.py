import os
import time
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
API_TOKEN = "cdsvj8qad3i9i37khudgcdsvj8qad3i9i37khue0"  # توكن Finnhub الخاص بك
ALLOWED_IDS = [7863509137]

bot = Bot(token=TOKEN)
app = Flask(__name__)

def scan_stocks(update, context):
    chat_id = update.effective_chat.id
    if chat_id not in ALLOWED_IDS:
        bot.send_message(chat_id=chat_id, text="🚫 غير مصرح لك باستخدام هذا البوت.")
        return
    
    bot.send_message(chat_id=chat_id, text="⏳ جاري فحص الأسهم... يرجى الانتظار.")
    try:
        response = requests.get(f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={API_TOKEN}")
        response.raise_for_status()
        symbols = [item["symbol"] for item in response.json() if "." not in item["symbol"]]

        selected = []
        count = 0

        for symbol in symbols:
            if count >= 200:  # فحص 200 سهم فقط لتقليل الضغط
                break

            quote = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_TOKEN}").json()
            if all(k in quote for k in ("c", "pc", "v")):
                price = quote["c"]
                prev = quote["pc"]
                volume = quote["v"]

                if price > 1 and volume > 100000 and price > prev:
                    selected.append(f"{symbol}: ${price:.2f} 🔼 {((price - prev)/prev)*100:.2f}%")
                    count += 1

        if selected:
            message = "📈 أسهم السوق التي تحقق الشروط:\n\n" + "\n".join(selected)
        else:
            message = "لا توجد أسهم تحقق الشروط حالياً."

        bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f"❌ حدث خطأ أثناء الفحص: {str(e)}")

def send_daily_report():
    chat_id = ALLOWED_IDS[0]
    try:
        response = requests.get(f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={API_TOKEN}")
        response.raise_for_status()
        symbols = [item["symbol"] for item in response.json() if "." not in item["symbol"]]

        selected = []
        count = 0

        for symbol in symbols:
            if count >= 200:
                break

            quote = requests.get(f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_TOKEN}").json()
            if all(k in quote for k in ("c", "pc", "v")):
                price = quote["c"]
                prev = quote["pc"]
                volume = quote["v"]

                if price > 1 and volume > 100000 and price > prev:
                    selected.append(f"{symbol}: ${price:.2f} 🔼 {((price - prev)/prev)*100:.2f}%")
                    count += 1

        if selected:
            message = "📢 تقرير يومي عن الأسهم التي تحقق الشروط:\n\n" + "\n".join(selected)
        else:
            message = "لا توجد أسهم تحقق الشروط حالياً."

        bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f"❌ حدث خطأ أثناء توليد التقرير: {str(e)}")

# جدولة التقرير اليومي الساعة 3 مساءً بتوقيت الرياض
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, "cron", hour=15, minute=0, timezone=pytz.timezone("Asia/Riyadh"))
scheduler.start()

dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("scan_stocks", scan_stocks))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    bot.set_webhook(url=f"https://your-render-app-url.onrender.com/{TOKEN}")  # استبدل هنا بالرابط الخاص بك
    app.run(host="0.0.0.0", port=1000)
