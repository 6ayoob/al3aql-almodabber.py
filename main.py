import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher
import logging
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

# إعداد البوت
TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [7863509137]
bot = Bot(token=TOKEN)

# إعداد السجل
logging.basicConfig(level=logging.INFO)

# دالة فحص العملات الرقمية (كمثال)
def scan_crypto():
    return "📊 نتائج العملات الرقمية:\n- BTC: ارتفاع\n- ETH: تجميع"

# دالة فحص الأسهم تحت 7 دولار (كمثال)
def scan_stocks():
    return "📈 نتائج الأسهم:\n- ABC: حجم تداول مرتفع\n- XYZ: تجميع"

# دالة التقرير اليومي
def send_daily_report():
    report = scan_stocks()
    for user_id in ALLOWED_USERS:
        bot.send_message(chat_id=user_id, text=f"📅 التقرير اليومي:\n{report}")

# أوامر Telegram
def start(update: Update, context):
    if update.effective_user.id in ALLOWED_USERS:
        update.message.reply_text("أهلاً بك في بوت مراقبة السوق 📈")

def handle_scan_stocks(update: Update, context):
    if update.effective_user.id in ALLOWED_USERS:
        result = scan_stocks()
        update.message.reply_text(result)

def handle_scan_crypto(update: Update, context):
    if update.effective_user.id in ALLOWED_USERS:
        result = scan_crypto()
        update.message.reply_text(result)

# إعداد Flask
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running!"

# جدولة التقرير اليومي
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, "cron", hour=15, minute=0, timezone=pytz.timezone('Asia/Riyadh'))
scheduler.start()

# إعداد أوامر البوت
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("scan_stocks", handle_scan_stocks))
dispatcher.add_handler(CommandHandler("scan_crypto", handle_scan_crypto))

# إعداد Webhook
if __name__ == "__main__":
    bot.set_webhook(url=f"https://al3aql-almodabber-py-2xic.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=1000)
