import requests
import os
import sys

def check_and_notify():
    api_url = "https://lovebaby.sw.ntpc.gov.tw/api/course/signup/list"
    # 三峽北大 Z0047
    payload = {"centerId": "Z0047", "page": 1, "pageSize": 50}
    
    # 模擬真實瀏覽器的完整標頭
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "Origin": "https://lovebaby.sw.ntpc.gov.tw",
        "Referer": "https://lovebaby.sw.ntpc.gov.tw/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    try:
        # 使用 Session 並設定超時
        res = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        # 檢查是否被擋 (403 Forbidden 或 404)
        if res.status_code != 200:
            send_tg(f"⚠️ 警報：伺服器拒絕連線 (狀態碼: {res.status_code})，可能需要調整爬取頻率。")
            return

        # 檢查回傳內容是否為 JSON
        try:
            data = res.json()
        except:
            # 如果不是 JSON，發送前 100 個字元到 Telegram 協助判斷
            content_preview = res.text[:100].replace('<', '[').replace('>', ']')
            send_tg(f"⚠️ 警報：網頁回傳格式錯誤。內容預覽：\n{content_preview}")
            return

        courses = data.get('data', [])
        match_list = []
        
        for c in courses:
            date_info = str(c.get('courseDate', ''))
            title = c.get('title', '')
            status = str(c.get('regStatusName', ''))
            
            # 嚴格篩選六日
            if "(六)" in date_info or "(日)" in date_info:
                # 只有當狀態不是額滿、截止、候補時才通知
                if status and all(x not in status for x in ["額滿", "截止", "候補"]):
                    match_list.append(f"✅ {date_info}\n📖 {title}\n📌 狀態: {status}")

        if match_list:
            msg = "🔥 發現三峽北大週末可報名課程！\n\n" + "\n---\n".join(match_list)
            send_tg(msg)
        else:
            # 這是為了讓你知道程式「活著」但沒課，測試完可以把下面這行刪掉
            # send_tg("🔍 巡邏完畢：目前三峽北大週末課程皆已額滿。")
            print("目前無符合條件課程。")

    except Exception as e:
        send_tg(f"❌ 程式執行發生異常: {str(e)}")

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
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

if __name__ == "__main__":
    check_and_notify()
