from flask import Flask, request, Response
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# إعدادات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [658712542]

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# أمر اختبار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("✅ البوت يعمل!")

application.add_handler(CommandHandler("start", start))

@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return Response("OK", status=200)

@app.route("/", methods=["GET"])
def home():
    return "🤖 Bot is running!"

# تعيين Webhook تلقائيًا عند أول تشغيل
@app.before_first_request
def setup_webhook():
   https://crypto-mastermind.onrender.com # ← استبدل هذا بالرابط الفعلي لخدمتك على Render
    bot = Bot(BOT_TOKEN)
    bot.set_webhook(url)

if __name__ == "__main__":
    app.run(port=10000, host="0.0.0.0")
