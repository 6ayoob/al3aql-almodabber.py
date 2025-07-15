
import requests
from flask import Flask, request
import telegram
import threading

# إعدادات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [658712542]
FINNHUB_API_KEY = "d1qisl1r01qo4qd7h510d1qisl1r01qo4qd7h51g"
COINGECKO_API = "https://api.coingecko.com/api/v3"

# إنشاء البوت وFlask
bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return '🤖 Bot is running!'

@app.route('/webhook', methods=['POST'])  # ✅ رابط Webhook المعدّل
def telegram_webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    handle_message(update)
    return 'OK'

def handle_message(update):
    message = update.message
    user_id = message.chat.id
    text = message.text

    if user_id not in ALLOWED_USERS:
        bot.send_message(chat_id=user_id, text="❌ غير مصرح لك باستخدام هذا البوت.")
        return

    if text == '/scan_stocks':
        bot.send_message(chat_id=user_id, text="🔍 جاري البحث عن الأسهم تحت 7 دولار...")
        scan_stocks(user_id)

    elif text == '/scan_crypto':
        bot.send_message(chat_id=user_id, text="💰 جاري فحص العملات الرقمية...")
        scan_crypto(user_id)

def scan_stocks(chat_id):
    symbols_url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}"
    symbols = requests.get(symbols_url).json()

    results = []
    for stock in symbols:
        symbol = stock["symbol"]
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        data = requests.get(quote_url).json()
        current = data.get("c")

        if current and current > 0 and current < 7:
            results.append(f"{symbol} - ${current:.2f}")
        if len(results) >= 10:
            break

    if results:
 msg = "📈 أفضل الأسهم تحت 7 دولار:\n" + "\n".join(results)
" + "\n".join(results)
    else:
        msg = "❌ لا توجد أسهم تحقق الشروط حالياً."

    bot.send_message(chat_id=chat_id, text=msg)

def scan_crypto(chat_id):
    url = f"{COINGECKO_API}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
    response = requests.get(url).json()

    lines = [f"{coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']}" for coin in response]
    msg = "🪙 أفضل العملات الرقمية:\n" + "\n".join(lines)
    bot.send_message(chat_id=chat_id, text=msg)

def breakout_alert():
    try:
        # ---- الأسهم ----
        symbols_url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={FINNHUB_API_KEY}"
        symbols = requests.get(symbols_url).json()

        for stock in symbols[:100]:
            symbol = stock['symbol']
            candles_url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=D&count=15&token={FINNHUB_API_KEY}"
            res = requests.get(candles_url).json()

            if res.get('s') != 'ok':
                continue

            highs = res.get('h', [])
            lows = res.get('l', [])
            closes = res.get('c', [])
            volumes = res.get('v', [])

            if not highs or not closes or not lows:
                continue

            current = closes[-1]
            resistance = max(highs[:-1])
            support = min(lows[:-1])

            # Breakout
            if current > resistance:
                diff = ((current - resistance) / resistance) * 100
                if diff >= 1.5:
                    strength = "💎 Breakout قوي"
                elif diff >= 0.8:
                    strength = "🔹 Breakout متوسط"
                else:
                    continue
                msg = f"{strength}:
📈 {symbol} اخترق المقاومة ${resistance:.2f} ➝ ${current:.2f} (+{diff:.2f}%)\n🔗 https://www.tradingview.com/symbols/{symbol}/"
                bot.send_message(chat_id=ALLOWED_USERS[0], text=msg)

            # Breakdown
            elif current < support:
                diff = ((support - current) / support) * 100
                if diff >= 1.5:
                    strength = "⚠️ Breakdown قوي"
                elif diff >= 0.8:
                    strength = "🔸 Breakdown متوسط"
                else:
                    continue
                msg = f"{strength}:
📉 {symbol} كسر الدعم ${support:.2f} ➝ ${current:.2f} (-{diff:.2f}%)\n🔗 https://www.tradingview.com/symbols/{symbol}/"
                bot.send_message(chat_id=ALLOWED_USERS[0], text=msg)

            # Volume Spike
            if len(volumes) >= 2:
                current_volume = volumes[-1]
                avg_volume = sum(volumes[:-1]) / (len(volumes) - 1)
                ratio = current_volume / avg_volume if avg_volume else 0
                if ratio >= 1.5:
                    msg = f"📊 Volume Spike:
💎 {symbol} حجم تداول اليوم = {ratio:.1f}x من المتوسط!\n📈 السعر: ${current:.2f}\n🔗 https://www.tradingview.com/symbols/{symbol}/"
                    bot.send_message(chat_id=ALLOWED_USERS[0], text=msg)

        # ---- العملات ----
        crypto_url = f"{COINGECKO_API}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
        coins = requests.get(crypto_url).json()

        for coin in coins:
            coin_id = coin['id']
            symbol = coin['symbol'].upper()
            name = coin['name']
            price_now = coin.get('current_price', 0)
            current_volume = coin.get('total_volume', 0)

            history_url = f"{COINGECKO_API}/coins/{coin_id}/market_chart?vs_currency=usd&days=14"
            history = requests.get(history_url).json()
            prices = [p[1] for p in history.get("prices", [])[:-1]]
            volumes = [v[1] for v in history.get("total_volumes", [])[:-1]]

            if not prices or not volumes:
                continue

            resistance = max(prices)
            support = min(prices)

            # Breakout
            if price_now > resistance:
                diff = ((price_now - resistance) / resistance) * 100
                if diff >= 1.5:
                    strength = "💎 Breakout قوي"
                elif diff >= 0.8:
                    strength = "🔹 Breakout متوسط"
                else:
                    continue
                msg = f"{strength}:
🪙 {name} ({symbol}) اخترق ${resistance:.2f} ➝ ${price_now:.2f} (+{diff:.2f}%)\n🔗 https://www.coingecko.com/en/coins/{coin_id}"
                bot.send_message(chat_id=ALLOWED_USERS[0], text=msg)

            # Breakdown
            elif price_now < support:
                diff = ((support - price_now) / support) * 100
                if diff >= 1.5:
                    strength = "⚠️ Breakdown قوي"
                elif diff >= 0.8:
                    strength = "🔸 Breakdown متوسط"
                else:
                    continue
                msg = f"{strength}:
🪙 {name} ({symbol}) كسر الدعم ${support:.2f} ➝ ${price_now:.2f} (-{diff:.2f}%)\n🔗 https://www.coingecko.com/en/coins/{coin_id}"
                bot.send_message(chat_id=ALLOWED_USERS[0], text=msg)

            # Volume Spike
            avg_volume = sum(volumes) / len(volumes)
            ratio = current_volume / avg_volume if avg_volume else 0
            if ratio >= 1.5:
                msg = f"📊 Volume Spike:
🪙 {name} ({symbol}) حجم تداول مرتفع {ratio:.1f}x من المتوسط\nالسعر: ${price_now:.2f}\n🔗 https://www.coingecko.com/en/coins/{coin_id}"
                bot.send_message(chat_id=ALLOWED_USERS[0], text=msg)

    except Exception as e:
        print(f"[Breakout/Breakdown Error] {e}")

    threading.Timer(3600, breakout_alert).start()

# بدء التنبيهات التلقائية
breakout_alert()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
