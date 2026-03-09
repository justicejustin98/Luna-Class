import requests
import os
from datetime import datetime

def check_and_notify():
    # 三峽北大親子館 Z0047
    api_url = "https://lovebaby.sw.ntpc.gov.tw/api/course/signup/list"
    payload = {"centerId": "Z0047", "page": 1, "pageSize": 50} 
    
    # 模擬真人瀏覽器標頭，避免 line1 column1 錯誤
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://lovebaby.sw.ntpc.gov.tw",
        "Referer": "https://lovebaby.sw.ntpc.gov.tw/"
    }
    
    try:
        # 使用 Session 維持連線狀態
        session = requests.Session()
        res = session.post(api_url, json=payload, headers=headers, timeout=20)
        
        # 偵錯點 1：如果狀態碼不是 200，直接回報
        if res.status_code != 200:
            print(f"Server returned status code: {res.status_code}")
            return

        # 偵錯點 2：檢查內容是否為 HTML (如果是 HTML 則無法解析成 JSON)
        if "<html" in res.text.lower():
            print("收到的是網頁 HTML 而非資料，可能被防火牆攔截。")
            return

        data = res.json()
        courses = data.get('data', [])
        match_list = []
        
        for c in courses:
            date_info = str(c.get('courseDate', ''))
            title = c.get('title', '')
            status = str(c.get('regStatusName', ''))
            
            # 判斷週末 (六、日)
            is_weekend = any(day in date_info for day in ["(六)", "(日)"])
            
            # 如果文字沒寫六日，用日期推算
            if not is_weekend:
                try:
                    date_str = date_info.split(" ")[0].replace("/", "-")
                    d_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if d_obj.weekday() >= 5:
                        is_weekend = True
                except:
                    pass
            
            # 篩選條件：週末 且 有名額
            if is_weekend:
                # 只要不是額滿、截止、候補，就視為可報名
                if status and all(x not in status for x in ["額滿", "截止", "候補"]):
                    match_list.append(f"✅ {date_info}\n📖 {title}\n📌 狀態: {status}")
                elif not status or status == "None":
                    match_list.append(f"✅ {date_info}\n📖 {title}\n📌 狀態: (可報名)")

        if match_list:
            msg = "🔥 發現三峽北大週末可報名課程！\n\n" + "\n---\n".join(match_list)
            send_tg(msg)
        else:
            print("目前無符合條件之週末課程。")
            
    except Exception as e:
        print(f"執行出錯: {e}")

def send_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    if not token or not chat_id: return
    
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
    check_and_
