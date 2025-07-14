import requests
from flask import Flask, request
import telegram

# إعدادات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [658712542]
FINNHUB_API_KEY = "d1qisl1r01qo4qd7h51g"
COINGECKO_API = "https://api.coingecko.com/api/v3"

bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is live!'

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    handle_message(update)
    return 'OK'

def handle_message(update):
    message = update.message
    if not message:
        return
    user_id = message.chat.id
    text = message.text

    if user_id not in ALLOWED_USERS:
        bot.send_message(chat_id=user_id, text="❌ غير مصرح لك.")
        return

    if text == '/scan_stocks':
        bot.send_message(chat_id=user_id, text="🔍 جاري البحث عن الأسهم تحت 7 دولار...")
        scan_stocks(user_id)
    elif text == '/scan_crypto':
        bot.send_message(chat_id=user_id, text="💰 جاري فحص العملات الرقمية...")
        scan_crypto(user_id)

def scan_stocks(chat_id):
    symbols = requests.get(f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}").json()
    results = []
    for stock in symbols:
        sym = stock["symbol"]
        data = requests.get(f"https://finnhub.io/api/v1/quote?symbol={sym}&token={FINNHUB_API_KEY}").json()
        c = data.get("c")
        if c and 0 < c < 7:
            results.append(f"{sym} - ${c:.2f}")
        if len(results) >= 10:
            break
    msg = ("📈 أفضل الأسهم تحت 7 دولار:\n" + "\n".join(results)) if results else "❌ لا توجد أسهم حالياً."
    bot.send_message(chat_id=chat_id, text=msg)

def scan_crypto(chat_id):
    resp = requests.get(f"{COINGECKO_API}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10").json()
    lines = [f"{c['name']} ({c['symbol'].upper()}): ${c['current_price']}" for c in resp]
    msg = "🪙 أفضل العملات الرقمية:\n" + "\n".join(lines)
    bot.send_message(chat_id=chat_id, text=msg)

if __name__ == "__main__":
    bot.set_webhook(url=f"https://al3aql-almodabber-py-1.onrender.com/{BOT_TOKEN}")
    app.run(host='0.0.0.0', port=10000)
