from flask import Flask, request
import os
import requests

app = Flask(__name__)
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

GROUP_LINK = "https://www.facebook.com/groups/yourgroup"
WEBSITE_LINK = "https://yourwebsite.ge"

TEXTS = {
    "ka": {
        "welcome": "გამარჯობა! აირჩიეთ ენა კომუნიკაციისთვის",
        "menu": "რით შემიძლია დაგეხმაროთ?",
        "buy": "🏠 ყიდვა",
        "rent": "🔑 ქირა",
        "sell": "📢 გაყიდვა",
        "city": "აირჩიეთ ქალაქი:",
        "more": "ყველა განცხადება",
        "no_listings": "ამ ქალაქში ამჟამად განცხადებები არ არის",
        "warning": "⚠️ ყურადღება: ყველა განცხადება და ჯგუფი არის მხოლოდ ქართულ ენაზე"
    },
    "en": {
        "welcome": "Hello! Choose language for communication",
        "menu": "How can I help you?",
        "buy": "🏠 Buy",
        "rent": "🔑 Rent",
        "sell": "📢 Sell",
        "city": "Choose city:",
        "more": "All listings",
        "no_listings": "No listings in this city yet",
        "warning": "⚠️ Attention: All listings and group are only in Georgian"
    },
    "ru": {
        "welcome": "Здравствуйте! Выберите язык для общения",
        "menu": "Чем я могу помочь?",
        "buy": "🏠 Купить",
        "rent": "🔑 Аренда",
        "sell": "📢 Продать",
        "city": "Выберите город:",
        "more": "Все объявления",
        "no_listings": "В этом городе пока нет объявлений",
        "warning": "⚠️ Внимание: Все объявления и группа только на грузинском языке"
    }
}

LISTINGS = {
    "თბილისი": [
        {"title": "2 ოთახიანი ბინა ვაკეში", "price": "120,000 $", "link": WEBSITE_LINK + "/tbilisi1"},
        {"title": "3 ოთახიანი ბინა საბურთალოზე", "price": "150,000 $", "link": WEBSITE_LINK + "/tbilisi2"},
        {"title": "სტუდიო გლდანში", "price": "65,000 $", "link": WEBSITE_LINK + "/tbilisi3"},
        {"title": "4 ოთახიანი ბინა დიღომში", "price": "200,000 $", "link": WEBSITE_LINK + "/tbilisi4"},
    ],
    "ბათუმი": [
        {"title": "ზღვის ხედით ბინა", "price": "90,000 $", "link": WEBSITE_LINK + "/batumi1"},
        {"title": "1 ოთახიანი ახალი რემონტით", "price": "55,000 $", "link": WEBSITE_LINK + "/batumi2"},
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
                        send_language_menu(sender_id)
                    else:
                        lang = user_lang.get(sender_id, "ka")
                        msg = "მენიუსთვის დაწერეთ გამარჯობა" if lang=="ka" else "Type Hello for menu" if lang=="en" else "Напишите Привет для меню"
                        send_text(sender_id, msg)

                if 'postback' in event:
                    payload = event['postback']['payload']
                    handle_postback(sender_id, payload)
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

def send_language_menu(sender_id):
    buttons = [
        {"type": "postback", "title": "🇬🇪 ქართული", "payload": "LANG_ka"},
        {"type": "postback", "title": "🇺🇸 English", "payload": "LANG_en"},
        {"type": "postback", "title": "🇷🇺 Русский", "payload": "LANG_ru"}
    ]
    send_buttons(sender_id, "გამარჯობა! აირჩიეთ ენა / Hello! Choose language / Здравствуйте! Выберите язык", buttons)

def send_menu(sender_id):
    lang = user_lang.get(sender_id, "ka")
    t = TEXTS[lang]
    # ჯერ გაფრთხილება
    send_text(sender_id, t["warning"])
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
        send_language_menu(sender_id)
    elif payload == "BUY":
        lang = user_lang.get(sender_id, "ka")
        t = TEXTS[lang]
        cities = ["თბილისი", "ბათუმი", "ქუთაისი"]
        buttons = [{"type": "postback", "title": city, "payload": f"CITY_BUY_{city}"} for city in cities]
        send_buttons(sender_id, t["city"], buttons)
    elif payload == "RENT":
        lang = user_lang.get(sender_id, "ka")
        t = TEXTS[lang]
        send_text(sender_id, t["warning"] + "\n" + ("ქირის განყოფილება მალე" if lang=="ka" else "Rent section coming soon" if lang=="en" else "Раздел аренды скоро"))
    elif payload == "SELL":
        lang = user_lang.get(sender_id, "ka")
        t = TEXTS[lang]
        send_text(sender_id, t["warning"])
        send_buttons(sender_id, t["sell"] + "?", [{"type": "web_url", "url": GROUP_LINK, "title": "ჯგუფი" if lang=="ka" else "Group"}])
    elif payload.startswith("CITY_BUY_"):
        city = payload.replace("CITY_BUY_", "")
        show_listings(sender_id, city)

def show_listings(sender_id, city):
    lang = user_lang.get(sender_id, "ka")
    t = TEXTS[lang]
    # ყოველთვის ვაჩვენებთ გაფრთხილებას პირველად
    send_text(sender_id, t["warning"])

    if city not in LISTINGS or not LISTINGS[city]:
        send_text(sender_id, t["no_listings"])
        return

    listings = LISTINGS[city]
    for item in listings[:3]: # მხოლოდ 3
        send_text(sender_id, f"🏠 {item['title']}\n💰 {item['price']}\n🔗 {item['link']}")

    if len(listings) > 3:
        buttons = [{"type": "web_url", "url": WEBSITE_LINK + f"/{city.lower()}", "title": t["more"]}]
        send_buttons(sender_id, f"{len(listings)} {t['more']}", buttons)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
