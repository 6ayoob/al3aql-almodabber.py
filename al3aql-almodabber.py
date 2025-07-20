from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import os

TOKEN = "توكن_البوت_هنا"
ALLOWED_USERS = [7863509137]

bot = Bot(token=TOKEN)
app = Flask(__name__)

# إعداد Dispatcher
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

# أوامر البوت
def start(update: Update, context: CallbackContext):
    if update.effective_user.id not in ALLOWED_USERS:
        return update.message.reply_text("غير مصرح لك.")
    update.message.reply_text("أهلاً بك في بوت السوق.")

def scan(update: Update, context: CallbackContext):
    if update.effective_user.id not in ALLOWED_USERS:
        return update.message.reply_text("غير مصرح لك.")
    update.message.reply_text("يتم الآن فحص السوق...")

# ربط الأوامر
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("scan", scan))

# جدولة إرسال التقرير اليومي
scheduler = BackgroundScheduler()

def send_daily_report():
    for user_id in ALLOWED_USERS:
        try:
            bot.send_message(chat_id=user_id, text="📈 تقرير السوق اليومي...")
        except Exception as e:
            print(f"خطأ عند الإرسال إلى {user_id}: {e}")

scheduler.add_job(send_daily_report, "cron", hour=12, minute=0)
scheduler.start()

# إعداد Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "✅ البوت يعمل"

# إعداد Webhook عند التشغيل
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'example.com')}/{TOKEN}"
    bot.set_webhook(url=webhook_url)
    app.run(host="0.0.0.0", port=port)
