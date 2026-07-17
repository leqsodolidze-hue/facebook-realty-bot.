import os
import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

GROUP_LINK = "https://www.facebook.com/groups/yourgroup" 
WEBSITE_LINK = "https://yourwebsite.ge"

LISTINGS = {
  "თბილისი": {
    "ყიდვა": [f"1. 2 ოთახიანი, ვაკე - $120,000\n[დეტალურად]({WEBSITE_LINK})"],
    "ქირა": ["1. 2 ოთახიანი, ვაკე - $800/თვე"]
  },
  "ბათუმი": {"ყიდვა": ["1. 1 ოთახიანი, ზღვისპირა - $90,000"], "ქირა": []},
  "ქუთაისი": {"ყიდვა": ["1. 3 ოთახიანი, ცენტრი - $65,000"], "ქირა": []}
}
user_state = {}

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Error"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                if 'message' in messaging_event and 'text' in messaging_event['message']:
                    handle_message(sender_id, messaging_event['message']['text'])
                if 'postback' in messaging_event:
                    handle_postback(sender_id, messaging_event['postback']['payload'])
    return "ok", 200

def handle_message(sender_id, text):
    text = text.lower().strip()
    if text == 'start' or text == 'დაწყება':
        send_main_menu(sender_id)
    elif text in LISTINGS:
        action = user_state.get(sender_id, {}).get('action')
        send_listings(sender_id, text, action)
    else:
        send_text(sender_id, "დაწერეთ START მენიუსთვის 👇")

def handle_postback(sender_id, payload):
    if payload == 'START':
        send_main_menu(sender_id)
    elif payload in ['BUY', 'RENT', 'MORTGAGE', 'SELL']:
        action_map = {'BUY': 'ყიდვა', 'RENT': 'ქირა', 'MORTGAGE': 'გირავნობა', 'SELL': 'გაყიდვა'}
        user_state[sender_id] = {'action': action_map[payload]}
        send_regions(sender_id, action_map[payload])
    elif payload in ['თბილისი', 'ბათუმი', 'ქუთაისი']:
        action = user_state.get(sender_id, {}).get('action')
        send_listings(sender_id, payload, action)

def send_main_menu(sender_id):
    message_data = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "button",
                "text": "გამარჯობა! 👋\nრა გსურთ?",
                "buttons": [
                    {"type": "postback", "title": "🏠 ყიდვა", "payload": "BUY"},
                    {"type": "postback", "title": "🔑 ქირა", "payload": "RENT"},
                    {"type": "postback", "title": "💰 გირავნობა", "payload": "MORTGAGE"},
                    {"type": "postback", "title": "📢 გაყიდვა", "payload": "SELL"}
                ]
            }
        }
    }
    call_send_api(sender_id, message_data)

def send_regions(sender_id, action):
    message_data = {
        "attachment": {
            "type": "template", 
            "payload": {
                "template_type": "button",
                "text": f"შესანიშნავი! თქვენ აირჩიეთ: {action}\nახლა აირჩიეთ რეგიონი:",
                "buttons": [
                    {"type": "postback", "title": "თბილისი", "payload": "თბილისი"},
                    {"type": "postback", "title": "ბათუმი", "payload": "ბათუმი"},
                    {"type": "postback", "title": "ქუთაისი", "payload": "ქუთაისი"}
                ]
            }
        }
    }
    call_send_api(sender_id, message_data)

def send_listings(sender_id, region, action):
    listings = LISTINGS.get(region, {}).get(action, ["ამ დროისთვის შეთავაზებები არ არის"])
    text = f"🏡 {region} - {action}\n\n" + "\n\n".join(listings) + f"\n\n---\nჯგუფი: {GROUP_LINK}\nსაიტი: {WEBSITE_LINK}"
    send_text(sender_id, text)
    send_main_menu(sender_id)

def call_send_api(sender_id, message_data):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": sender_id}, "message": message_data}
    requests.post(url, json=payload)

def send_text(sender_id, text):
    call_send_api(sender_id, {"text": text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
