import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# إعدادات البوت
TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_IDS = [7863509137]

# تهيئة البوت و Flask
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, use_context=True)

# تسجيل الأحداث
logging.basicConfig(level=logging.INFO)

# دالة تحقق من صلاحية المستخدم
def is_authorized(user_id):
    return user_id in ALLOWED_IDS

# أوامر البوت
def start(update: Update, context):
    if is_authorized(update.effective_user.id):
        update.message.reply_text("✅ أهلاً بك! البوت يعمل.")
    else:
        update.message.reply_text("❌ غير مصرح لك باستخدام هذا البوت.")

def scan(update: Update, context):
    if not is_authorized(update.effective_user.id):
        return update.message.reply_text("❌ غير مصرح.")
    update.message.reply_text("📊 جاري الفحص...")

# إضافة الأوامر
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("scan", scan))

# تقرير يومي
def send_daily_report():
    for chat_id in ALLOWED_IDS:
        bot.send_message(chat_id, "📈 هذا تقرير يومي تجريبي.")

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, "cron", hour=15, minute=0, timezone="Asia/Riyadh")
scheduler.start()

# نقطة الدخول لـ Telegram Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# نقطة وهمية لإرضاء Render
@app.route("/", methods=["GET"])
def home():
    return "✅ البوت يعمل"

# عند تشغيل السيرفر
if __name__ == "__main__":
    # تعيين Webhook تلقائيًا عند التشغيل
    external_url = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if external_url:
        webhook_url = f"https://{external_url}/{TOKEN}"
        bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook set to {webhook_url}")

    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
