import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# إعداد التوكن والمعرّف
TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_IDS = [7863509137]

# إنشاء الكائنات الأساسية
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# أمر /start
def start(update: Update, context: CallbackContext):
    if update.effective_user.id in ALLOWED_IDS:
        update.message.reply_text("مرحبًا بك في البوت!")

# أمر /time - فقط كمثال
def show_time(update: Update, context: CallbackContext):
    if update.effective_user.id in ALLOWED_IDS:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update.message.reply_text(f"الوقت الحالي: {now}")

# مهمة يومية وهمية (يمكنك استبدالها بتحليلك اليومي)
def send_daily_report():
    for user_id in ALLOWED_IDS:
        try:
            bot.send_message(chat_id=user_id, text="📊 هذا هو تقريرك اليومي (مثال تجريبي).")
        except Exception as e:
            print(f"❌ فشل الإرسال إلى {user_id}: {e}")

# إضافة الأوامر
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("time", show_time))

# Flask route لمعالجة Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# جدولة التقرير اليومي
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, "cron", hour=15, minute=0)  # الساعة 3 مساءً بتوقيت السعودية
scheduler.start()

# تشغيل التطبيق
if __name__ == "__main__":
    bot.delete_webhook()  # حذف أي Webhook سابق

    external_url = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if external_url:
        webhook_url = f"https://{external_url}/{TOKEN}"
        bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook set to {webhook_url}")

    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
