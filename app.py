# 檔案名稱：app.py 【最終修正版 - 移除班級資訊 & 修正鑰匙問題】
import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# --- 【重要】請在這裡，重新貼上您自己的三把鑰匙 ---
CHANNEL_SECRET = '4d92e35cb5d0d79ca1c48683c92180ed'
CHANNEL_ACCESS_TOKEN = 'onEH5gjVrj0VB6CaDmsXsMHhjVjDeSesAp5/qL/EFeu2fRx6vRHrO308PI3AFcojtmySmmW2eq7qnbDLG8GBfmbD9PP+qYn2NPAZJPmLs2bkLwKD3WJA6JRoBNWrpdxcbAXOmofGkbsr4Z0visq/vwdB04t89/1O/w1cDnyilFU='
GAS_API_URL = 'https://script.google.com/macros/s/AKfycbxmTDa78iUMSUNvJtG-PjYlMJu8kgmkmQfI9AVmiTuyTUuKfou5xR6_LRhjaSUMk2gY-w/exec'
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
    keyword = event.message.text
    try:
        response = requests.get(GAS_API_URL, params={'keyword': keyword})
        data = response.json()
        if data.get('status') == 'success':
            student_data = data.get('data', {})
            reply_text = (
                f"👤 {student_data.get('幼生姓名', 'N/A')}\n"
                f"--------------------\n"
                f"🆔 身分證號：{student_data.get('身分證號', 'N/A')}\n"
                f"🚻 性別：{student_data.get('性別', 'N/A')}\n"
                f"🎂 出生日期：{student_data.get('出生日期', 'N/A')}\n"
                f"📞 聯絡電話：{student_data.get('聯絡電話', 'N/A')}\n"
                f"🏠 通訊地址：{student_data.get('通訊地址', 'N/A')}"
            )
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
