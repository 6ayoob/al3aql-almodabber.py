import os
from flask import Flask
from telegram import Bot, Update
from telegram.ext import CommandHandler, CallbackContext, Updater, Dispatcher
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# إعدادات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [7863509137]

# تهيئة البوت
bot = Bot(token=BOT_TOKEN)

# Flask لتشغيل الخدمة على Render
app = Flask(__name__)

# إعدادات اللوغ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# دالة فحص العملات (مثال)
def scan_crypto():
    return "📈 أفضل العملات الآن:\n1. BTC\n2. ETH\n3. SOL"

# دالة فحص الأسهم (مثال)
def scan_stocks():
    return "📊 أفضل الأسهم الآن:\n1. AAPL\n2. NVDA\n3. TSLA"

# أوامر التليجرام
def start(update: Update, context: CallbackContext):
    if update.effective_user.id in ALLOWED_USERS:
        update.message.reply_text("مرحبًا! أرسل /scan_crypto أو /scan_stocks للحصول على التحليلات.")

def scan_crypto_command(update: Update, context: CallbackContext):
    if update.effective_user.id in ALLOWED_USERS:
        result = scan_crypto()
        update.message.reply_text(result)

def scan_stocks_command(update: Update, context: CallbackContext):
    if update.effective_user.id in ALLOWED_USERS:
        result = scan_stocks()
        update.message.reply_text(result)

# جدولة إرسال تلقائي يومي
def send_daily_report():
    try:
        bot.send_message(chat_id=7863509137, text="📅 تقرير السوق:\n\n" + scan_crypto() + "\n\n" + scan_stocks())
    except Exception as e:
        print("خطأ أثناء إرسال التقرير:", e)

# تشغيل Flask وهمي لـ Render
@app.route('/')
def home():
    return "Running!"

# التهيئة النهائية
if __name__ == '__main__':
    updater = Updater(BOT_TOKEN, use_context=True)
    dp: Dispatcher = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("scan_crypto", scan_crypto_command))
    dp.add_handler(CommandHandler("scan_stocks", scan_stocks_command))

    # تشغيل البوت
    updater.start_polling()

    # جدولة التقرير اليومي الساعة 3 مساءً
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_report, 'cron', hour=15, minute=0, timezone='Asia/Riyadh')
    scheduler.start()

import os
port = int(os.environ.get("PORT", 10000))  # يستخدم متغير البيئة PORT أو 10000 افتراضياً
app.run(host='0.0.0.0', port=port)
