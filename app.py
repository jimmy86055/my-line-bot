# 檔案名稱：app.py 【最新最終版 - 支援單一學生 & 全班名單查詢】
import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# --- 【重要】請再次確認這裡填寫的是您自己的三把鑰匙 ---
CHANNEL_SECRET = 'U60dd82a9d304a8cd06e104e920af21e4'
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

        # 檢查後端回傳的狀態
        status = data.get('status')

        if status == 'success_single':
            # 如果是單一學生的資料
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

        elif status == 'success_multiple':
            # 如果是多筆學生的名單
            student_list = data.get('data', [])
            # 組合名單文字，記得確認試算表標題是'幼生姓名'
            student_names = [f"· {s.get('幼生姓名', '')}" for s in student_list]

            reply_text = f"📖 {keyword} 全班名單：\n--------------------\n" + "\n".join(student_names)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

        else: # status == 'not_found' or 'error'
            reply_text = f"❌ 查無「{keyword}」的相關資料"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

    except:
        reply_text = "⚠️ 系統連線異常，請稍後再試。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

