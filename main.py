from flask import Flask, request
import os
import requests

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

# შენი ლინკები - მერე შეცვალე შენზე
GROUP_LINK = "https://www.facebook.com/groups/yourgroup"
WEBSITE_LINK = "https://yourwebsite.ge"

CITIES = ["თბილისი", "ბათუმი", "ქუთაისი", "რუსთავი", "ზუგდიდი"]
LISTINGS = {
    "თბილისი": [
        {"title": "2 ოთახიანი ბინა ვაკეში", "price": "120,000 $", "link": WEBSITE_LINK + "/listing1"},
        {"title": "3 ოთახიანი ბინა საბურთალოზე", "price": "150,000 $", "link": WEBSITE_LINK + "/listing2"}
    ],
    "ბათუმი": [
        {"title": "ზღვის ხედით ბინა", "price": "90,000 $", "link": WEBSITE_LINK + "/listing3"}
    ]
}

def call_send_api(sender_id, message):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": sender_id}, "message": message}
    requests.post(url, json=payload)

def send_text(sender_id, text):
    call_send_api(sender_id, {"text": text})

def send_buttons(sender_id, text, buttons):
    message = {"attachment": {"type": "template", "payload": {"template_type": "button", "text": text, "buttons": buttons}}}
    call_send_api(sender_id, message)

def handle_message(sender_id, message_text):
    text = message_text.lower()

    if text == "start":
        buttons = [
            {"type": "postback", "title": "🏠 ყიდვა", "payload": "BUY"},
            {"type": "postback", "title": "🔑 ქირა", "payload": "RENT"},
            {"type": "postback", "title": "💰 გირავნობა", "payload": "MORTGAGE"},
            {"type": "postback", "title": "📢 გაყიდვა", "payload": "SELL"}
        ]
        send_buttons(sender_id, "გამარჯობა! რით შემიძლია დაგეხმაროთ?", buttons)
    else:
        send_text(sender_id, "მენიუსთვის დაწერეთ START")

def handle_postback(sender_id, payload):
    if payload == "BUY":
        buttons = [{"type": "postback", "title": city, "payload": f"CITY_BUY_{city}"} for city in CITIES]
        send_buttons(sender_id, "აირჩიეთ ქალაქი:", buttons)
    elif payload == "RENT":
        send_text(sender_id, "ქირის განყოფილება მალე დაემატება")
    elif payload == "MORTGAGE":
        send_text(sender_id, "გირავნობის განყოფილება მალე დაემატება")
    elif payload == "SELL":
        send_buttons(sender_id, "გაყიდვისთვის მოგვწერეთ ჯგუფში:", [{"type": "web_url", "url": GROUP_LINK, "title": "ჩვენი ჯგუფი"}])
    elif payload.startswith("CITY_BUY_"):
        city = payload.replace("CITY_BUY_", "")
        if city in LISTINGS:
            for item in LISTINGS[city]:
                send_text(sender_id, f"{item['title']}\nფასი: {item['price']}\n{link: {item['link']}}")
        else:
            send_text(sender_id, "ამ ქალაქში ამჟამად განცხადებები არ არის")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Verification failed'

    if request.method == 'POST':
        data = request.get_json()
        for entry in data.get('entry', []):
            for event in entry.get('messaging', []):
                sender_id = event['sender']['id']
                if 'message' in event and 'text' in event['message']:
                    handle_message(sender_id, event['message']['text'])
                if 'postback' in event:
                    handle_postback(sender_id, event['postback']['payload'])
        return 'ok', 200

def setup_get_started():
    url = f"https://graph.facebook.com/v18.0/me/messenger_profile?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "get_started": {"payload": "START"},
        "greeting": [{"locale": "default", "text": "გამარჯობა! Udzravi qonebis ofisi-ს ბოტი გესალმებათ 👋"}]
    }
    requests.post(url, json=payload)

setup_get_started()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
