import requests
import os
from datetime import datetime

def check_and_notify():
    api_url = "https://lovebaby.sw.ntpc.gov.tw/api/course/signup/list"
    payload = {"centerId": "Z0047", "page": 1, "pageSize": 50} 
    
    try:
        res = requests.post(api_url, json=payload, timeout=15)
        courses = res.json().get('data', [])
        
        match_list = []
        debug_info = []
        
        for i, c in enumerate(courses):
            date_info = str(c.get('courseDate', ''))
            title = c.get('title', '')
            status = str(c.get('regStatusName', ''))
            
            # 記錄前 3 筆原始資料，用來抓漏
            if i < 3:
                debug_info.append(f"日期: {date_info} | 狀態: {status} | 課名: {title}")
            
            # 智慧判斷是否為週末 (解析 YYYY-MM-DD)
            is_weekend = False
            if "(六)" in date_info or "(日)" in date_info:
                is_weekend = True
            else:
                try:
                    # 擷取純日期部分並轉換格式
                    date_str = date_info.split(" ")[0].split("T")[0].replace("/", "-")
                    d_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if d_obj.weekday() >= 5: # 5是週六, 6是週日
                        is_weekend = True
                except:
                    pass
            
            # 只要是六日，且狀態沒有顯示額滿、截止、候補，就抓出來
            if is_weekend:
                if status and "額滿" not in status and "截止" not in status and "候補" not in status:
                    match_list.append(f"✅ {date_info}\n📖 {title}\n📌 狀態: {status}")
                elif not status or status == "None": 
                    # 有時候可報名時，狀態文字剛好是空的
                    match_list.append(f"✅ {date_info}\n📖 {title}\n📌 狀態: (可報名)")

        if match_list:
            msg = "🔥 發現三峽北大週末可報名課程！\n\n" + "\n---\n".join(match_list)
            send_tg(msg)
        else:
            # 如果還是找不到，就把系統看到的真面目傳給你看
            debug_msg = "⚠️ 程式過濾後沒找到。請看系統抓到的前3筆原始資料長怎樣：\n\n" + "\n".join(debug_info)
            send_tg(debug_msg)
            
    except Exception as e:
        send_tg(f"❌ 執行發生錯誤: {e}")

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
