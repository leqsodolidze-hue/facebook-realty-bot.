from flask import Flask, request
import os
import requests

app = Flask(__name__)
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

GROUP_LINK = "https://www.facebook.com/groups/yourgroup"
WEBSITE_LINK = "https://yourwebsite.ge"

TEXTS = {
    "ka": {"welcome": "გამარჯობა! აირჩიეთ ენა", "menu": "რით შემიძლია დაგეხმაროთ?", "buy": "🏠 ყიდვა", "rent": "🔑 ქირა", "sell": "📢 გაყიდვა", "city": "აირჩიეთ ქალაქი:", "more": "ყველა განცხადება", "no_listings": "ამ ქალაქში განცხადებები არ არის", "warning": "⚠️ ყურადღება: ყველა განცხადება მხოლოდ ქართულად არის"},
    "en": {"welcome": "Hello! Choose language", "menu": "How can I help you?", "buy": "🏠 Buy", "rent": "🔑 Rent", "sell": "📢 Sell", "city": "Choose city:", "more": "All listings", "no_listings": "No listings in this city", "warning": "⚠️ Attention: All listings are only in Georgian"},
    "ru": {"welcome": "Здравствуйте! Выберите язык", "menu": "Чем я могу помочь?", "buy": "🏠 Купить", "rent": "🔑 Аренда", "sell": "📢 Продать", "city": "Выберите город:", "more": "Все объявления", "no_listings": "В этом городе нет объявлений", "warning": "⚠️ Внимание: Все объявления только на грузинском"}
}

LISTINGS = {
    "თბილისი": [
        {"title": "2 ოთახიანი ბინა ვაკეში", "price": "120,000 $", "link": WEBSITE_LINK + "/tbilisi1"},
        {"title": "3 ოთახიანი ბინა საბურთალოზე", "price": "150,000 $", "link": WEBSITE_LINK + "/tbilisi2"},
        {"title": "სტუდიო გლდანში", "price": "65,000 $", "link": WEBSITE_LINK + "/tbilisi3"},
    ],
    "ბათუმი": [
        {"title": "ზღვის ხედით ბინა", "price": "90,000 $", "link": WEBSITE_LINK + "/batumi1"},
    ]
}

user_lang = {}

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

                if 'message' in event and 'text' in event['message']:
                    text = event['message']['text'].lower().replace(" ", "")
                    if text in ["start", "გამარჯობა", "gamarjoba", "hello", "zdravstvuyte", "привет"]:
                        send_language_buttons(sender_id) # ღილაკებით ვაგზავნით
                    else:
                        lang = user_lang.get(sender_id, "ka")
                        send_text(sender_id, "მენიუსთვის დაწერეთ გამარჯობა" if lang=="ka" else "Type Hello for menu" if lang=="en" else "Напишите Привет для меню")

                if 'postback' in event:
                    payload = event['postback']['payload']
                    handle_postback(sender_id, payload)
        return 'ok', 200

def call_send_api(sender_id, message):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": sender_id}, "message": message})

def send_text(sender_id, text):
    call_send_api(sender_id, {"text": text})

def send_buttons(sender_id, text, buttons):
    call_send_api(sender_id, {"attachment": {"type": "template", "payload": {"template_type": "button", "text": text, "buttons": buttons}}})

def send_language_buttons(sender_id):
    buttons = [
        {"type": "postback", "title": "🇬🇪 ქართული", "payload": "LANG_ka"},
        {"type": "postback", "title": "🇺🇸 English", "payload": "LANG_en"},
        {"type": "postback", "title": "🇷🇺 Русский", "payload": "LANG_ru"}
    ]
    send_buttons(sender_id, "გამარჯობა! აირჩიეთ ენა / Hello! Choose language / Здравствуйте! Выберите язык", buttons)

def send_menu(sender_id):
    lang = user_lang.get(sender_id, "ka")
    t = TEXTS
    send_text(sender_id, t["warning"]) # ჯერ გაფრთხილება
    buttons = [
        {"type": "postback", "title": t["buy"], "payload": "BUY"},
        {"type": "postback", "title": t["rent"], "payload": "RENT"},
        {"type": "postback", "title": t["sell"], "payload": "SELL"}
    ]
    send_buttons(sender_id, t["menu"], buttons)

def handle_postback(sender_id, payload):
    global user_lang
    if payload.startswith("LANG_"):
        user_lang[sender_id] = payload.replace("LANG_", "")
        send_menu(sender_id)
    elif payload == "START" or payload == "GET_STARTED":
        send_language_buttons(sender_id)
    elif payload == "BUY":
        t = TEXTS
        cities = ["თბილისი", "ბათუმი", "ქუთაისი"]
        buttons = [{"type": "postback", "title": city, "payload": f"CITY_{city}"} for city in cities]
        send_buttons(sender_id, t["city"], buttons)
    elif payload == "RENT":
        lang = user_lang.get(sender_id, "ka")
        send_text(sender_id, TEXTS[lang]["warning"] + "\n" + ("ქირა მალე" if lang=="ka" else "Rent soon" if lang=="en" else "Аренда скоро"))
    elif payload == "SELL":
        lang = user_lang.get(sender_id, "ka")
        send_text(sender_id, TEXTS[lang]["warning"])
        send_buttons(sender_id, TEXTS[lang]["sell"] + "?", [{"type": "web_url", "url": GROUP_LINK, "title": "ჯგუფი" if lang=="ka" else "Group"}])
    elif payload.startswith("CITY_"):
        city = payload.replace("CITY_", "")
        show_listings(sender_id, city)

def show_listings(sender_id, city):
    lang = user_lang.get(sender_id, "ka")
    t = TEXTS
    send_text(sender_id, t["warning"])
    if city not in LISTINGS or not LISTINGS[city]:
        send_text(sender_id, t["no_listings"])
        return
    for item in LISTINGS[city][:3]:
        send_text(sender_id, f"🏠 {item['title']}\n💰 {item['price']}\n🔗 {item['link']}")
    if len(LISTINGS[city]) > 3:
        send_buttons(sender_id, f"{len(LISTINGS[city])} {t['more']}", [{"type": "web_url", "url": WEBSITE_LINK + f"/{city.lower()}", "title": t["more"]}])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
