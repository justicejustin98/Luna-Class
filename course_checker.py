import requests
import os

def check_and_notify():
    api_url = "https://lovebaby.sw.ntpc.gov.tw/api/course/signup/list"
    # 這裡以泰山中心 Z0047 為例，可依網頁 F12 看到的 API 修改
    payload = {"centerId": "Z0047", "page": 1, "pageSize": 20}
    try:
        res = requests.post(api_url, json=payload, timeout=10)
        courses = res.json().get('data', [])
        match_list = [f"📅 {c['courseDate']}\n📖 {c['title']}" for c in courses 
                      if any(day in c['courseDate'] for day in ["(六)", "(日)"]) 
                      and "我要報名" in c['regStatusName']]
        if match_list:
            send_tg("🔥 發現可報名週末課程！\n\n" + "\n---\n".join(match_list))
    except Exception as e: print(f"Error: {e}")

def send_tg(text):
    token = os.environ.get('TG_TOKEN')
    chat_id = os.environ.get('TG_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "reply_markup": {"inline_keyboard": [[{"text": "立即前往報名", "url": "https://lovebaby.sw.ntpc.gov.tw/#/course-signupcourse/07/Z0047"}]]}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    check_and_notify()
