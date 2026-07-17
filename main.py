import os
import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

# შენი ლინკები - აქ ჩასვი შენი რეალური
GROUP_LINK = "https://www.facebook.com/groups/yourgroup" 
WEBSITE_LINK = "https://yourwebsite.ge"

# რეალური ბინები
LISTINGS = {
  "თბილისი": {
    "ყიდვა": [
      f"1. 2 ოთახიანი ბინა, ვაკე - $120,000\nფართი: 65მ²\n[დეტალურად]({WEBSITE_LINK})",
      f"2. 3 ოთახიანი ბინა, საბურთალო - $180,000\nფართი: 90მ²\n[დეტალურად]({WEBSITE_LINK})"
    ],
    "ქირა": ["1. 2 ოთახიანი ბინა, ვაკე - $800/თვე"]
  },
  "ბათუმი": {
    "ყიდვა": [f"1. 1 ოთახიანი, ზღვისპირა - $90,000\n[დეტალურად]({WEBSITE_LINK})"],
    "ქირა": ["1. 1 ოთახიანი, ზღვა 5 წთ - $600/თვე"]
  },
  "ქუთაისი": {
    "ყიდვა": ["1. 3 ოთახიანი ბინა, ცენტრი - $65,000"],
    "ქირა": ["1. 2 ოთახიანი ბინა - $300/თვე"]
  }
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
                
                if 'message' in messaging_event:
                    handle_message(sender_id, messaging_event['message'])
                if 'postback' in messaging_event:
                    handle_postback(sender_id, messaging_event['postback'])
    return "ok", 200

def handle_message(sender_id, message):
    text = message.get('text', '').lower().strip()
    
    if text == 'start' or text == 'დაწყება':
        send_main_menu(sender_id)
        return
    
    if text in LISTINGS: # თუ რეგიონია
        region = text
        action = user_state.get(sender_id, {}).get('action')
        send_listings(sender_id, region, action)
        return
        
    send_text(sender_id, "ვერ გავიგე 😅 დაწერეთ START ან გამოიყენეთ ღილაკები")

def handle_postback(sender_id, postback):
    payload = postback['payload']
    
    if payload == 'START':
        user_state[sender_id] = {}
        send_main_menu(sender_id)
    
    elif payload in ['BUY', 'RENT', 'MORTGAGE', 'SELL']:
        action_map = {'BUY': 'ყიდვა', 'RENT': 'ქირა', 'MORTGAGE': 'გირავნობა', 'SELL': 'გაყიდვა'}
        action = action_map[payload]
        user_state[sender_id] = {'action': action}
        send_regions(sender_id, action)

def send_main_menu(sender_id):
    message_data = {
        "text": "გამარჯობა! 👋\nრა გსურთ?",
        "quick_replies": [
            {"content_type": "text", "title": "🏠 ყიდვა", "payload": "BUY"},
            {"content_type": "text", "title": "🔑 ქირა", "payload": "RENT"},
            {"content_type": "text", "title": "💰 გირავნობა", "payload": "MORTGAGE"},
            {"content_type": "text", "title": "📢 გაყიდვა", "payload": "SELL"}
        ]
    }
    call_send_api(sender_id, message_data)

def send_regions(sender_id, action):
    message_data = {
        "text": f"შესანიშნავი! თქვენ აირჩიეთ: {action}\nახლა აირჩიეთ რეგიონი:",
        "quick_replies": [
            {"content_type": "text", "title": "თბილისი", "payload": "თბილისი"},
            {"content_type": "text", "title": "ბათუმი", "payload": "ბათუმი"},
            {"content_type": "text", "title": "ქუთაისი", "payload": "ქუთაისი"}
        ]
    }
    call_send_api(sender_id, message_data)

def send_listings(sender_id, region, action):
    listings = LISTINGS.get(region, {}).get(action, ["ამ დროისთვის შეთავაზებები არ არის"])
    text = f"🏡 {region} - {action}\n\n" + "\n\n".join(listings) + f"\n\n---\nდამატებითი შეთავაზებები:\nFacebook ჯგუფი: {GROUP_LINK}\nვებგვერდი: {WEBSITE_LINK}"
    call_send_api(sender_id, {"text": text})
    send_main_menu(sender_id) # 1წმ მერე დააბრუნე მენიუში

def call_send_api(sender_id, message_data):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": sender_id}, "message": message_data}
    requests.post(url, json=payload)

def send_text(sender_id, text):
    call_send_api(sender_id, {"text": text})

if __name__ == '__main__':
    app.run(port=3000)
    print("✅ BOT VERSION 3.2 LOADED - ქართული")
