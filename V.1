import requests
import schedule
import time
from datetime import datetime

# =================ตั้งค่าตัวแปร=================
TELEGRAM_BOT_TOKEN = 'ใส่_TOKEN_ของบอทคุณที่นี่'
TELEGRAM_CHAT_ID = 'ใส่_CHAT_ID_ของกลุ่มหรือของคุณที่นี่'
# ============================================

def get_tiktok_best_sellers():
    """
    ฟังก์ชันสำหรับดึงข้อมูลจาก TikTok 
    *หมายเหตุ: ในการใช้งานจริง คุณต้องเขียนโค้ดเชื่อมต่อกับ TikTok Shop API หรือ Web Scraper ที่นี่
    """
    # ข้อมูลจำลองสำหรับการทดสอบ
    mock_data = (
        "1. ครีมกันแดด ABC - ยอดขาย 150 ชิ้น\n"
        "2. เสื้อยืดมินิมอล - ยอดขาย 120 ชิ้น\n"
        "3. แก้วเก็บความเย็น - ยอดขาย 85 ชิ้น"
    )
    return mock_data

def send_telegram_message(message):
    """
    ฟังก์ชันสำหรับส่งข้อความไปยัง Telegram
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"[{datetime.now()}] ส่งรายงานสำเร็จ!")
    except Exception as e:
        print(f"[{datetime.now()}] เกิดข้อผิดพลาดในการส่ง: {e}")

def daily_job():
    """
    งานที่จะให้ทำทุกวัน
    """
    print("กำลังดึงข้อมูลและส่งรายงาน...")
    
    # 1. ดึงข้อมูล
    data = get_tiktok_best_sellers()
    
    # 2. จัดรูปแบบข้อความ
    today_date = datetime.now().strftime('%Y-%m-%d')
    message = f"📊 **รายงานสินค้าขายดี TikTok ประจำวัน** ({today_date}):\n\n{data}\n\n💡 โชคดีกับยอดขายวันนี้ครับ!"
    
    # 3. ส่งข้อความ
    send_telegram_message(message)

# =================การตั้งเวลา=================
# ตั้งเวลาให้ทำงานทุกวันเวลา 04:30 
schedule.every().day.at("04:30").do(daily_job)

print("บอทเริ่มทำงานแล้ว... รอเวลาส่งรายงาน (04:30 น.)")

# Loop ให้โปรแกรมทำงานค้างไว้ตลอดเวลาเพื่อรอให้ถึงเวลา
while True:
    schedule.run_pending()
    time.sleep(60) # เช็คเวลาทุกๆ 60 วินาทีเพื่อไม่ให้กินทรัพยากรเครื่องเกินไป
