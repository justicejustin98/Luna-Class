import requests
import os
import sys
import traceback

def check_and_notify():
    # 確認三峽北大親子展演角 (Z0047)
    api_url = "https://lovebaby.sw.ntpc.gov.tw/api/course/signup/list"
    payload = {"centerId": "Z0047", "page": 1, "pageSize": 50}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Referer": "https://lovebaby.sw.ntpc.gov.tw/"
    }

    try:
        print("--- 正在嘗試抓取三峽北大資料 ---")
        res = requests.post(api_url, json=payload, headers=headers, timeout=20)
        
        # 偵錯：印出狀態碼
        print(f"伺服器狀態碼: {res.status_code}")
        
        # 偵錯：檢查是否為 JSON 格式
        try:
            data = res.json()
        except Exception:
            print("❌ 無法解析資料！伺服器可能擋掉了連線，回應內容如下：")
            print(res.text[:500]) # 印出前 500 字元供參考
            return

        courses = data.get('data', [])
        if not courses:
            print("查無課程資料。")
            return

        match_list = []
        for c in courses:
            date_info = str(c.get('courseDate', ''))
            title = c.get('title', '')
            status = str(c.get('regStatusName', ''))
            
            # 篩選條件：只要包含 (六) 或 (日) 的週末課程
            if "(六)" in date_info or "(日)" in date_info:
                # 排除額滿、截止、候補
                if status and all(x not in status for x in ["額滿", "截止", "候補"]):
                    match_list.append(f"✅ {date_info}\n📖 {title}\n📌 狀態: {status}")

        if match_list:
            msg = "🔥 發現三峽北大週末可報名課程！\n\n" + "\n---\n".join(match_list)
            send_tg(msg)
            print("✅ 通知已發送至 Telegram")
        else:
            print("目前三峽北大沒有符合條件的週末課程。")

    except Exception:
        print("❌ 程式發生嚴重崩潰，詳細錯誤如下：")
        traceback.print_exc() # 這會印出具體是哪一行壞掉
        sys.exit(1)

def send_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    if not token or not chat_id:
        print("錯誤：Secret (TG_TOKEN/ID) 設定遺失")
        return
    
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
    except Exception as e:
        print(f"Telegram 發送失敗: {e}")

if __name__ == "__main__":
    check_and_notify()
