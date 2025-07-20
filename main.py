import requests
import yfinance as yf
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import telegram
import pytz
from datetime import datetime

# إعدادات البوت
BOT_TOKEN = "7863509137:AAHBuRbtzMAOM_yBbVZASfx-oORubvQYxY8"
ALLOWED_USERS = [658712542]  # أضف هنا معرفات المستخدمين المصرح لهم

# إعداد البوت والتطبيق
bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)
timezone = pytz.timezone("Asia/Riyadh")

# دالة لجلب رموز ناسداك من ملف رسمي
def get_nasdaq_tickers():
    url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
    resp = requests.get(url)
    lines = resp.text.splitlines()[1:]  # تخطي رأس الجدول
    tickers = [line.split("|")[0] for line in lines if "Test Issue" not in line]
    return tickers

# دالة الفحص وإرسال التنبيهات
def scan_and_notify():
    tickers = get_nasdaq_tickers()
    batch = tickers[:300]  # يمكن زيادة العدد حسب الحاجة

    try:
        data = yf.download(tickers=batch, period="2d", interval="1d", group_by='ticker', threads=True)
    except Exception as e:
        print(f"فشل في تحميل البيانات: {e}")
        return

    for ticker in batch:
        try:
            if ticker not in data or len(data[ticker]) < 2:
                continue

            today = data[ticker].iloc[-1]
            yesterday = data[ticker].iloc[-2]

            close = today['Close']
            prev_close = yesterday['Close']
            sma_50 = yf.Ticker(ticker).history(period="60d")['Close'].rolling(50).mean().iloc[-1]

            percent_change = ((close - prev_close) / prev_close) * 100
            crossed_sma50 = close > sma_50 and yesterday['Close'] <= sma_50

            msg = ""
            if close > 1:
                if percent_change >= 5:
                    msg += f"📈 {ticker} صعد أكثر من 5٪ اليوم\n"
                if crossed_sma50:
                    msg += f"📊 {ticker} اخترق المتوسط 50 SMA\n"

                if msg:
                    for uid in ALLOWED_USERS:
                        bot.send_message(chat_id=uid, text=msg)

        except Exception as e:
            print(f"خطأ في {ticker}: {e}")

# صفحة التحقق على الويب
@app.route('/')
def home():
    return '✅ Stock bot is running.'

# نقطة تلقي الرسائل من تليجرام
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    handle_message(update)
    return 'OK'

# التعامل مع الرسائل
def handle_message(update):
    message = update.message
    chat_id = message.chat.id

    if chat_id not in ALLOWED_USERS:
        bot.send_message(chat_id=chat_id, text="🚫 غير مصرح لك باستخدام هذا البوت.")
        return

    if message.text == '/scan':
        bot.send_message(chat_id=chat_id, text="🔍 يتم الآن فحص السوق...")
        scan_and_notify()

# جدولة الفحص التلقائي كل ساعة
scheduler = BackgroundScheduler(timezone=timezone)
scheduler.add_job(scan_and_notify, 'interval', hours=1)
scheduler.start()

# تشغيل السيرفر على Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
