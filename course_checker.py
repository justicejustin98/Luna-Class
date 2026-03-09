import requests
import os

def check_and_notify():
    # 確認為三峽北大 Z0047
    api_url = "https://lovebaby.sw.ntpc.gov.tw/api/course/signup/list"
    payload = {"centerId": "Z0047", "page": 1, "pageSize": 20}
    
    # 1. 先發送一則連線測試訊息，確保 Secret 設定正確
    send_tg("🚀 系統連線檢查：三峽北大(Z0047)巡邏員已上工！")

    try:
        res = requests.post(api_url, json=payload, timeout=15)
        courses = res.json().get('data', [])
        
        match_list = []
        for c in courses:
            date_info = c.get('courseDate', '')
            title = c.get('title', '')
            status = c.get('regStatusName', '') 
            
            # 判斷六日
            if any(day in date_info for day in ["(六)", "(日)"]):
                # 判斷是否「我要報名」
                if "我要報名" in status:
                    match_list.append(f"✅ 【可以報名！】\n📅 {date_info}\n📖 {title}")
                else:
                    # 如果想在測試時看到額滿的課，可以取消下面這行的註解
                    # match_list.append(f"❌ 【名額已滿】\n📅 {date_info}\n📖 {title}")
                    pass

        if match_list:
            send_tg("🔥 發現三峽北大週末課程！\n\n" + "\n---\n".join(match_list))
            
    except Exception as e:
        print(f"Error: {e}")

def send_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": text,
        "reply_markup": {
            "inline_keyboard": [[{"text": "前往報名頁面", "url": "https://lovebaby.sw.ntpc.gov.tw/#/course-signupcourse/07/Z0047"}]]
        }
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_and_notify()
