from flask import Flask, request
import os
import requests

app = Flask(__name__)
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

GROUP_LINK = "https://www.facebook.com/groups/yourgroup" # აქ შენი ჯგუფი ჩასვი

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Verification failed', 403
    
    if request.method == 'POST':
        data = request.get_json()
        for entry in data.get('entry', []):
            for event in entry.get('messaging', []):
                sender_id = event['sender']['id']
                
                # 1. თუ ტექსტია
                if 'message' in event and 'text' in event['message']:
                    text = event['message']['text'].lower()
                    if text == "start":
                        send_menu(sender_id)
                    else:
                        send_text(sender_id, "მენიუსთვის დაწერეთ START")
                
                # 2. თუ ღილაკია დაჭერილი
                if 'postback' in event:
                    payload = event['postback']['payload']
                    if payload == "START" or payload == "GET_STARTED":
                        send_menu(sender_id)
                    elif payload == "BUY":
                        send_text(sender_id, "ყიდვის განყოფილება მალე დაემატება")
                    elif payload == "RENT":
                        send_text(sender_id, "ქირის განყოფილება მალე დაემატება")
                    elif payload == "SELL":
                        send_buttons(sender_id, "გაყიდვისთვის შემოუერთდი ჯგუფს:", 
                            [{"type": "web_url", "url": GROUP_LINK, "title": "ჩვენი ჯგუფი"}])

        return 'ok', 200

def call_send_api(sender_id, message):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": sender_id}, "message": message}
    requests.post(url, json=payload)

def send_text(sender_id, text):
    call_send_api(sender_id, {"text": text})

def send_buttons(sender_id, text, buttons):
    message = {"attachment": {"type": "template", "payload": {"template_type": "button", "text": text, "buttons": buttons}}}
    call_send_api(sender_id, message)

def send_menu(sender_id):
    buttons = [
        {"type": "postback", "title": "🏠 ყიდვა", "payload": "BUY"},
        {"type": "postback", "title": "🔑 ქირა", "payload": "RENT"},
        {"type": "postback", "title": "📢 გაყიდვა", "payload": "SELL"}
    ]
    send_buttons(sender_id, "გამარჯობა! რით შემიძლია დაგეხმაროთ?", buttons)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
