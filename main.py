
TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
API_TOKEN = "cdsvj8qad3i9i37khudgcdsvj8qad3i9i37khue0"  # توكن Finnhub الخاص بك
ALLOWED_IDS = [7863509137]
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
import asyncio

# إعدادات البوت
BOT_TOKEN = '7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8'
ALLOWED_IDS = [7863509137]

# إعداد السجل
logging.basicConfig(level=logging.INFO)

# Flask App لتشغيل السيرفر الوهمي على Render
app = Flask(__name__)

# إنشاء تطبيق البوت
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_IDS:
        return
    await update.message.reply_text("مرحبًا! أنا جاهز ✅")

# تسجيل الأوامر
bot_app.add_handler(CommandHandler("start", start))

# نقطة استقبال Webhook (مطلوبة لـ Render)
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    asyncio.create_task(bot_app.process_update(update))
    return "ok", 200

# تشغيل البوت داخليًا في Render
@app.before_first_request
def activate_bot():
    asyncio.create_task(bot_app.initialize())
    asyncio.create_task(bot_app.start())
    asyncio.create_task(bot_app.updater.start_polling())  # ضروري فقط لتشغيل الـ JobQueue إن وُجد
    logging.info("✅ Bot is running and webhook is set.")

# تشغيل سيرفر Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
