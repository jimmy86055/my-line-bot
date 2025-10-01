# 檔案名稱：app.py
import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# --- 您的鑰匙和網址已修正完畢 ---
CHANNEL_SECRET='6861cc94549ab2e7c7532d1db7529445'
CHANNEL_ACCESS_TOKEN='onEH5gjVrj0VB6CaDmsXsMHhjVjDeSesAp5/qL/EFeu2fRx6vRHrO308PI3AFcojtmySmmW2eq7qnbDLG8GBfmbD9PP+qYn2NPAZJPmLs2bkLwKD3WJA6JRoBNWrpdxcbAXOmofGkbsr4Z0visq/vwdB04t89/1O/w1cDnyilFU='
GAS_API_URL='https://script.google.com/macros/s/AKfycbxmTDa78iUMSUNvJtG-PjYlMJu8kgmkmQfI9AVmiTuyTUuKfou5xR6_LRhjaSUMk2gY-w/exec'
# ------------------------------------

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    if user_message.startswith('查詢 '):
        keyword = user_message.split(' ', 1)[1]
        try:
            response = requests.get(GAS_API_URL, params={'keyword': keyword})
            data = response.json()
            if data.get('status') == 'success':
                student_data = data.get('data', {})
                # --- 我們在這裡組合要回傳的漂亮格式 ---
                # 記得確認下面的欄位名稱，跟您Google試算表第一排的標題「完全一樣」
                reply_text = (
                    f"🏫 {student_data.get('班級', 'N/A')} - {student_data.get('幼生姓名', 'N/A')}\n"
                    f"--------------------\n"
                    f"🆔 身分證號：{student_data.get('身分證號', 'N/A')}\n"
                    f"🚻 性別：{student_data.get('性別', 'N/A')}\n"
                    f"🎂 出生日期：{student_data.get('出生日期', 'N/A')}\n"
                    f"📞 聯絡電話：{student_data.get('聯絡電話', 'N/A')}\n"
                    f"🏠 通訊地址：{student_data.get('通訊地址', 'N/A')}"
                )
                # ------------------------------------
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            else:
                reply_text = f"❌ 查無資料：{keyword}"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        except:
            reply_text = "⚠️ 系統連線異常，請稍後再試。"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port)
