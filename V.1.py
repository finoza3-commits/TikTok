import os
import requests
import schedule
import time
import threading
from datetime import datetime
from flask import Flask
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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

def get_tiktok_best_sellers(time_range="รายวัน", category="ทั้งหมด"):
    """
    ฟังก์ชันสำหรับดึงข้อมูลสินค้าขายดีจาก TikTok โดยใช้ GPT-mini (OpenAI API)
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    current_month = thai_months[datetime.now().month - 1]
    
    category_text = f"เฉพาะหมวดหมู่: {category}" if category != "ทั้งหมด" else "จากทุกหมวดหมู่สินค้า"
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": f"คุณคือนักวิเคราะห์เทรนด์ TikTok Shop ไทย สรุปข้อมูลให้สั้น กระชับที่สุด ขณะนี้คือเดือน {current_month} (อิงสภาพอากาศปัจจุบันของไทย)"},
            {"role": "user", "content": f"สรุปเทรนด์ TikTok ไทยแบบ '{time_range}' {category_text} อัปเดตล่าสุด แบ่งเป็น 2 ส่วน (ส่วนละ 10 สินค้า รวมทั้งหมด 20 สินค้า):\n1. 🔥 สินค้ากำลังดัน (สินค้าที่อัลกอริทึม TikTok กำลังช่วยดันคลิปวิดีโอ/คลิปกำลังเป็นไวรัลในวันนี้) จำนวน 10 อันดับ\n2. 💰 สินค้าขายดี (ยอดสั่งซื้อพุ่งสูงสุดของเมื่อวาน/ช่วงที่ผ่านมา เพื่อนำมาทำคลิปดักกระแสในวันนี้) จำนวน 10 อันดับ\n\nบังคับรูปแบบการตอบแต่ละอันดับให้มี 'หมวดหมู่' ด้วย ดังนี้:\n[หมวดหมู่สินค้า] ชื่อสินค้า | เหตุผลที่ฮิต | ความเชื่อมโยงกับสภาพอากาศ/ฤดูกาลในเดือน {current_month}\n(พิมพ์ให้สั้นที่สุด ห้ามเกริ่นยาว เพื่อประหยัด Token)"}
        ],
        "max_tokens": 1200,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"[{datetime.now()}] ข้อผิดพลาด OpenAI API: {e}")
        return "⚠️ ไม่สามารถดึงข้อมูลสินค้าจาก GPT ได้ในขณะนี้"

def get_tiktok_idea(product_name):
    """
    ฟังก์ชันสำหรับดึงไอเดียทำคลิป TikTok จาก GPT-mini
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "คุณคือนักสืบและผู้เชี่ยวชาญหาสินค้าทำเงินใน TikTok Shop ไทย หน้าที่ของคุณคือแนะนำ 'ไอเดียสินค้าเจาะจง' ที่กำลังมาแรง เพื่อให้ผู้ใช้นำไปต่อยอดทำนายหน้า"},
            {"role": "user", "content": f"ช่วยแนะนำไอเดียสินค้าที่น่าเอามาทำนายหน้าในหมวดหมู่/คีย์เวิร์ดนี้: '{product_name}'\nขอ 3-5 สินค้าแบบเจาะจง (ห้ามกว้างเกินไป)\nพร้อมบอก 'จุดขายสั้นๆ' และ 'เหตุผลที่คนจะซื้อช่วงนี้'\n(พิมพ์สั้นๆ กระชับ ห้ามเกริ่นยาว เพื่อประหยัด Token)"}
        ],
        "max_tokens": 800,
        "temperature": 0.8
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"[{datetime.now()}] ข้อผิดพลาด OpenAI API (Idea): {e}")
        return "⚠️ ไม่สามารถสร้างไอเดียได้ในขณะนี้"

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
    data = get_tiktok_best_sellers("รายวัน", "ทั้งหมด")
    today_date = datetime.now().strftime('%d/%m/%Y')
    message = f"🇹🇭📈 **รายงานเจาะลึกเทรนด์ TikTok ไทย (รายวัน | รวมทุกหมวดหมู่) ประจำวันที่ {today_date}**\n\n{data}\n\n💡 _อัปเดตข้อมูลเพื่อให้คุณไม่พลาดทุกกระแส!_"
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
    btn2 = KeyboardButton("💡 ผู้ช่วยหาไอเดียสินค้า")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, "ยินดีต้อนรับ! เลือกเมนูที่ต้องการได้เลยครับ 👇", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💡 ผู้ช่วยหาไอเดียสินค้า")
def prompt_idea_help(message):
    help_text = "💡 **ผู้ช่วยหาไอเดียสินค้าทำเงิน**\n\nพิมพ์คำสั่ง `/idea [ตามด้วยหมวดหมู่หรือคีย์เวิร์ด]` แล้วส่งมาให้ผมได้เลยครับ!\n\nตัวอย่าง:\n`/idea เสื้อผ้าผู้ชาย`\n`/idea ของใช้หน้าร้อน`\n`/idea แม่และเด็ก`\n\nเดี๋ยวผมจะช่วยคัด 3-5 ไอเดียสินค้าเจาะจงที่น่าเอาไปทำนายหน้ามาให้ครับ! 📦"
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['idea'])
def handle_idea_command(message):
    text = message.text.replace('/idea', '').strip()
    if not text:
        bot.reply_to(message, "⚠️ กรุณาพิมพ์คีย์เวิร์ดด้วยครับ เช่น `/idea เสื้อผ้าผู้ชาย`", parse_mode='Markdown')
        return
    
    bot.reply_to(message, f"กำลังคิดไอเดียปังๆ สำหรับ **{text}**... รอสักครู่ 🎬", parse_mode='Markdown')
    idea_text = get_tiktok_idea(text)
    bot.send_message(message.chat.id, f"💡 **ไอเดียสินค้าทำเงิน: {text}**\n\n{idea_text}")

@bot.message_handler(commands=['check', 'trend'])
@bot.message_handler(func=lambda message: message.text == "📈 เช็คสินค้ากำลังดัน (TikTok ไทย)")
def prompt_time_range(message):
    # ฟังก์ชันแสดงปุ่มเลือกช่วงเวลาเมื่อผู้ใช้กดเช็ค
    markup = InlineKeyboardMarkup()
    btn_daily = InlineKeyboardButton("📅 รายวัน", callback_data="time_daily")
    btn_weekly = InlineKeyboardButton("🗓️ รายสัปดาห์", callback_data="time_weekly")
    btn_monthly = InlineKeyboardButton("📊 รายเดือน", callback_data="time_monthly")
    markup.add(btn_daily, btn_weekly, btn_monthly)
    
    bot.send_message(message.chat.id, "กรุณาเลือกระยะเวลาของรายงานที่ต้องการเช็คครับ 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('time_'))
def prompt_category(call):
    # ผู้ใช้เลือกเวลาแล้ว ให้ถามหมวดหมู่ต่อ
    time_selected = call.data.split('_')[1] # daily, weekly, monthly
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌟 ทั้งหมด", callback_data=f"cat_{time_selected}_ทั้งหมด"),
        InlineKeyboardButton("💄 ความงาม", callback_data=f"cat_{time_selected}_ความงาม"),
        InlineKeyboardButton("👗 เสื้อผ้าแฟชั่น", callback_data=f"cat_{time_selected}_แฟชั่น"),
        InlineKeyboardButton("💊 สุขภาพ", callback_data=f"cat_{time_selected}_สุขภาพ"),
        InlineKeyboardButton("📱 อิเล็กทรอนิกส์", callback_data=f"cat_{time_selected}_ไอที"),
        InlineKeyboardButton("🍳 ของใช้ในบ้าน", callback_data=f"cat_{time_selected}_ของใช้บ้าน"),
        InlineKeyboardButton("🍔 อาหารและเครื่องดื่ม", callback_data=f"cat_{time_selected}_อาหาร")
    )
    
    time_th = {"daily": "รายวัน", "weekly": "รายสัปดาห์", "monthly": "รายเดือน"}
    bot.edit_message_text(f"เลือกหมวดหมู่สินค้าสำหรับรายงาน **{time_th[time_selected]}** 👇", 
                          call.message.chat.id, call.message.message_id, 
                          reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def handle_report_callback(call):
    # ผู้ใช้เลือกหมวดหมู่แล้ว ดึงข้อมูลและส่งรายงาน
    # data: cat_daily_ทั้งหมด
    parts = call.data.split('_')
    time_selected = parts[1]
    category = parts[2]
    
    time_th = {"daily": "รายวัน", "weekly": "รายสัปดาห์", "monthly": "รายเดือน"}
    time_range = time_th[time_selected]
    
    # ลบปุ่มออกจากข้อความเดิม
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, f"กำลังวิเคราะห์ข้อมูลแบบ **{time_range}** (หมวด: {category})... กรุณารอสักครู่ ⏳", parse_mode='Markdown')
    
    data = get_tiktok_best_sellers(time_range, category)
    today_date = datetime.now().strftime('%d/%m/%Y')
    report_message = f"🇹🇭📈 **รายงานเจาะลึกเทรนด์ TikTok ไทย ({time_range} | หมวด: {category}) ประจำวันที่ {today_date}**\n\n{data}\n\n💡 _อัปเดตข้อมูลเพื่อให้คุณไม่พลาดทุกกระแส!_"
    
    bot.send_message(call.message.chat.id, report_message)

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
