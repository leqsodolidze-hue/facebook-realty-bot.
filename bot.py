import os
import requests
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# 1. აქ ჩასვი შენი Token-ები
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN') # მაგ: "leqso123"

# 2. Excel ბაზა
df = pd.read_excel('udzravi_goneba_database.xlsx')

# 3. მესიჯის გაგზავნის ფუნქცია
def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text}
    }
    requests.post(url, json=payload)

# 4. მენიუს დაყენება
def setup_menu():
    url = f"https://graph.facebook.com/v18.0/me/messenger_profile?access_token={PAGE_ACCESS_TOKEN}"
    data = {
        "get_started": {"payload": "GET_STARTED"},
        "persistent_menu": [{
            "locale": "default",
            "composer_input_disabled": False,
            "call_to_actions": [
                {"type": "postback", "title": "🏠 ყიდვა", "payload": "BUY"},
                {"type": "postback", "title": "🔑 ქირა", "payload": "RENT"},
                {"type": "postback", "title": "📞 კონტაქტი", "payload": "CONTACT"}
            ]
        }]
    }
    requests.post(url, json=data)

# 5. Webhook Verify
@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return 'Verification failed', 403

# 6. როცა მესიჯი მოდის
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    for entry in data['entry']:
        for messaging_event in entry['messaging']:
            sender_id = messaging_event['sender']['id']
            
            if messaging_event.get('message'):
                text = messaging_event['message'].get('text', '')
                send_message(sender_id, f"გამარჯობა! მიღებულია: {text}\n\nაირჩიე მენიუდან რა გაინტერესებს")
                
            if messaging_event.get('postback'):
                payload = messaging_event['postback']['payload']
                if payload == 'BUY':
                    send_message(sender_id, "კარგი, ყიდვა გაინტერესებს. რა ბიუჯეტი გაქვს?")
                elif payload == 'RENT':
                    send_message(sender_id, "კარგი, ქირა გაინტერესებს. რა რაიონში გინდა?")
                elif payload == 'CONTACT':
                    send_message(sender_id, "დაგვიკავშირდი: 555 12 34 56")
    
    return 'ok', 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    setup_menu() # ეს 1-ჯერ გაუშვებს და დაყენდება მენიუ
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
