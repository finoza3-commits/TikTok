import os
import requests
import schedule
import time
import threading
from datetime import datetime
from flask import Flask
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# =================ตั้งค่าตัวแปร=================
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'ใส่_TOKEN_ของบอทคุณที่นี่')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'ใส่_CHAT_ID_ของกลุ่มหรือของคุณที่นี่')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'ใส่_OPENAI_API_KEY_ของคุณที่นี่')
# ============================================

app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@app.route('/')
def home():
    return "TikTok Bot is running!"

def get_tiktok_best_sellers():
    """
    ฟังก์ชันสำหรับดึงข้อมูลสินค้าขายดีจาก TikTok โดยใช้ GPT-mini (OpenAI API)
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "คุณคือนักวิเคราะห์เทรนด์ TikTok Shop ไทย สรุปข้อมูลให้สั้น กระชับที่สุด ตรงประเด็น"},
            {"role": "user", "content": "สรุปเทรนด์ TikTok ไทยวันนี้ 2 ส่วน (ส่วนละ 3 อันดับ):\n1. 🔥 สินค้ากำลังดัน\n2. 💰 สินค้าขายดี\n\nแต่ละอันดับให้บอกแค่: ชื่อสินค้า | เหตุผลที่ฮิต | ความเชื่อมโยงกับสภาพอากาศ/ฤดูกาลช่วงนี้\n(พิมพ์ให้สั้นที่สุด ห้ามเกริ่นยาว เพื่อประหยัด Token)"}
        ],
        "max_tokens": 350,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"[{datetime.now()}] ข้อผิดพลาด OpenAI API: {e}")
        return "⚠️ ไม่สามารถดึงข้อมูลสินค้าขายดีจาก GPT ได้ในขณะนี้"

def send_telegram_message(message):
    """
    ฟังก์ชันสำหรับส่งข้อความไปยัง Telegram อัตโนมัติ
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        print(f"[{datetime.now()}] ส่งรายงานอัตโนมัติสำเร็จ!")
    except Exception as e:
        print(f"[{datetime.now()}] เกิดข้อผิดพลาดในการส่งอัตโนมัติ: {e}")

def daily_job():
    """
    งานที่จะให้ทำทุกวันเวลา 04:30
    """
    print("กำลังดึงข้อมูลและส่งรายงานอัตโนมัติ...")
    data = get_tiktok_best_sellers()
    today_date = datetime.now().strftime('%d/%m/%Y')
    message = f"🇹🇭📈 **รายงานเจาะลึกเทรนด์ TikTok ไทย ประจำวันที่ {today_date}**\n\n{data}\n\n💡 _อัปเดตข้อมูลเพื่อให้คุณไม่พลาดทุกกระแส!_"
    send_telegram_message(message)

# =================การตั้งเวลา=================
schedule.every().day.at("04:30").do(daily_job)

def run_scheduler():
    print("ระบบตั้งเวลาเริ่มทำงานแล้ว... รอเวลาส่งรายงาน (04:30 น.)")
    while True:
        schedule.run_pending()
        time.sleep(60)

# =================สร้างเมนูบอท=================
@bot.message_handler(commands=['start', 'menu'])
def send_menu(message):
    # สร้างคีย์บอร์ดปุ่มกด
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("📈 เช็คสินค้ากำลังดัน (TikTok ไทย)")
    markup.add(btn1)
    
    bot.send_message(message.chat.id, "ยินดีต้อนรับ! เลือกเมนูที่ต้องการได้เลยครับ 👇", reply_markup=markup)

@bot.message_handler(commands=['check', 'trend'])
@bot.message_handler(func=lambda message: message.text == "📈 เช็คสินค้ากำลังดัน (TikTok ไทย)")
def manual_report(message):
    # ฟังก์ชันตอบสนองเมื่อผู้ใช้กดปุ่ม
    bot.send_message(message.chat.id, "กำลังวิเคราะห์ข้อมูล... กรุณารอสักครู่ ⏳")
    data = get_tiktok_best_sellers()
    today_date = datetime.now().strftime('%d/%m/%Y')
    report_message = f"🇹🇭📈 **รายงานเจาะลึกเทรนด์ TikTok ไทย ประจำวันที่ {today_date}**\n\n{data}\n\n💡 _อัปเดตข้อมูลเพื่อให้คุณไม่พลาดทุกกระแส!_"
    bot.send_message(message.chat.id, report_message)

def run_bot_polling():
    print("บอทพร้อมรับคำสั่งจากผู้ใช้แล้ว...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"[{datetime.now()}] Polling error: {e}")
            time.sleep(15)

if __name__ == '__main__':
    # 1. เริ่มการทำงานของ schedule ใน background thread
    t1 = threading.Thread(target=run_scheduler)
    t1.start()
    
    # 2. เริ่มการทำงานของ Bot Polling (รอรับคำสั่งปุ่มกด)
    t2 = threading.Thread(target=run_bot_polling)
    t2.start()
    
    # 3. รัน Web Server สำหรับให้ Render ผูก Port
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
