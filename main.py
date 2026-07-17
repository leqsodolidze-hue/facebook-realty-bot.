from flask import Flask, request
import os
import requests

app = Flask(__name__)
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

#!!! აქ შენი ლინკები ჩასვი!!!
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

                # 1. START ღილაკზე - ენები
                if payload == "START" or payload == "GET_STARTED":
                    buttons = [
                        {"type": "postback", "title": "🇬🇪 ქართული", "payload": "LANG_ka"},
                        {"type": "postback", "title": "🇺🇸 English", "payload": "LANG_en"},
                        {"type": "postback", "title": "🇷🇺 Русский", "payload": "LANG_ru"}
                    ]
                    send_button_template(sender_id, "აირჩიეთ ენა / Choose language / Выберите язык", buttons)

                # 2. ენის არჩევისას - მენიუ
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

                # 3. ყიდვაზე - ქალაქები
                elif payload == "BUY":
                    lang = user_lang.get(sender_id, "ka")
                    city_text = "აირჩიეთ ქალაქი:" if lang=="ka" else "Choose city:" if lang=="en" else "Выберите город:"
                    buttons = [
                        {"type": "postback", "title": "თბილისი", "payload": "CITY_თბილისი"},
                        {"type": "postback", "title": "ბათუმი", "payload": "CITY_ბათუმი"},
                        {"type": "postback", "title": "ქუთაისი", "payload": "CITY_ქუთაისი"}
                    ]
                    send_button_template(sender_id, city_text, buttons)

                # 4. ქალაქის არჩევისას
                elif payload.startswith("CITY_"):
                    lang = user_lang.get(sender_id, "ka")
                    city = payload.split("_")[1]
                    warning = "⚠️ ყურადღება: ყველა განცხადება მხოლოდ ქართულად არის" if lang=="ka" else "⚠️ Attention: All listings are only in Georgian" if lang=="en" else "⚠️ Внимание: Все объявления только на грузинском"
                    send_text(sender_id, warning)
                    send_text(sender_id, f"{city}-ში განცხადებები: \n1. 2 ოთ. ბინა - 120,000$\n2. 3 ოთ. ბინა - 150,000$")

            elif 'message' in messaging_event:
                text = messaging_event['message']['text'].lower()
                if "გამარჯობა" in text or "hello" in text or "привет" in text or "start" in text:
                    buttons = [
                        {"type": "postback", "title": "🇬🇪 ქართული", "payload": "LANG_ka"},
                        {"type": "postback", "title": "🇺🇸 English", "payload": "LANG_en"},
                        {"type": "postback", "title": "🇷🇺 Русский", "payload": "LANG_ru"}
                    ]
                    send_button_template(sender_id, "აირჩიეთ ენა / Choose language / Выберите язык", buttons)

    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
