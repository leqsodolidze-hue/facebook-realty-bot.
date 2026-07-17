from flask import Flask, request
import os
import requests

app = Flask(__name__)
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

GROUP_LINK = "https://www.facebook.com/groups/yourgroup"
WEBSITE_LINK = "https://yourwebsite.ge"

user_lang = {}

def send_message(sender_id, message):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": sender_id}, "message": message})

def send_text(sender_id, text):
    send_message(sender_id, {"text": text})

def send_button_template(sender_id, text, buttons):
    payload = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "button",
                "text": text,
                "buttons": buttons
            }
        }
    }
    send_message(sender_id, payload)

def send_language_menu(sender_id):
    buttons = [
        {"type": "postback", "title": "🇬🇪 ქართული", "payload": "LANG_ka"},
        {"type": "postback", "title": "🇺🇸 English", "payload": "LANG_en"},
        {"type": "postback", "title": "🇷🇺 Русский", "payload": "LANG_ru"}
    ]
    send_button_template(sender_id, "გამარჯობა! 👋\nაირჩიეთ ენა / Choose language / Выберите язык", buttons)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Verification failed', 403

    data = request.get_json()
    for entry in data['entry']:
        for messaging_event in entry['messaging']:
            sender_id = messaging_event['sender']['id']

            if 'postback' in messaging_event:
                payload = messaging_event['postback']['payload']

                if payload == "START" or payload == "GET_STARTED":
                    send_language_menu(sender_id) # Get Started-ზე

                elif payload.startswith("LANG_"):
                    lang = payload.split("_")[1]
                    user_lang[sender_id] = lang

                    warning = "⚠️ ყურადღება: ყველა განცხადება მხოლოდ ქართულად არის" if lang=="ka" else "⚠️ Attention: All listings are only in Georgian" if lang=="en" else "⚠️ Внимание: Все объявления только на грузинском"
                    send_text(sender_id, warning)

                    menu_text = "რით შემიძლია დაგეხმაროთ?" if lang=="ka" else "How can I help?" if lang=="en" else "Чем я могу помочь?"
                    buttons = [
                        {"type": "postback", "title": "🏠 ყიდვა" if lang=="ka" else "🏠 Buy" if lang=="en" else "🏠 Купить", "payload": "BUY"},
                        {"type": "postback", "title": "🔑 ქირა" if lang=="ka" else "🔑 Rent" if lang=="en" else "🔑 Аренда", "payload": "RENT"},
                        {"type": "postback", "title": "📢 გაყიდვა" if lang=="ka" else "📢 Sell" if lang=="en" else "📢 Продать", "payload": "SELL"}
                    ]
                    send_button_template(sender_id, menu_text, buttons)

            elif 'message' in messaging_event:
                text = messaging_event['message'].get('text', '').lower()
                # ვინც შემოვა და რამე დაწერს - პირდაპირ მივაწოდოთ მენიუ
                send_language_menu(sender_id)

    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
