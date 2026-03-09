import requests
import os

def check_and_notify():
    api_url = "https://lovebaby.sw.ntpc.gov.tw/api/course/signup/list"
    # Z0047 為三峽北大親子館
    payload = {"centerId": "Z0047", "page": 1, "pageSize": 50} 
    
    try:
        res = requests.post(api_url, json=payload, timeout=15)
        courses = res.json().get('data', [])
        
        match_list = []
        for c in courses:
            date_info = c.get('courseDate', '')
            title = c.get('title', '')
            status = c.get('regStatusName', '') 
            
            # 嚴格篩選：只要 (六) 或 (日)
            if "(六)" in date_info or "(日)" in date_info:
                # 排除「已額滿」或「已截止」的課，確保是有名額的
                if "額滿" not in status and "截止" not in status:
                    match_list.append(f"✅ {date_info}\n📖 {title}")

        # 如果有找到符合條件的課程，才發送通知
        if match_list:
            msg = "🔥 發現三峽北大週末可報名課程！\n\n" + "\n---\n".join(match_list)
            send_tg(msg)
            
    except Exception as e:
        print(f"執行發生錯誤: {e}")

def send_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": text,
        "reply_markup": {
            "inline_keyboard": [[{"text": "前往報名頁面 (點擊開啟日曆)", "url": "https://lovebaby.sw.ntpc.gov.tw/#/course-signupcourse/07/Z0047"}]]
        }
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_and_notify()
