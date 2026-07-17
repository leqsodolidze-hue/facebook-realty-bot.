print("BOT VERSION 3.1 LOADED")

from flask import Flask, request
import requests
import os

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

GROUP_LINK = "https://www.facebook.com/groups/2319025648223860"
PAGE_LINK = "https://www.facebook.com/profile.php?id=61591712523869"

def send_message(recipient_id, text, quick_replies=None):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    if quick_replies:
        payload["message"]["quick_replies"] = []
        for qr in quick_replies:
            payload["message"]["quick_replies"].append({
                "content_type": "text",
                "title": qr["title"],
                "payload": qr["payload"]
            })
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json=payload)

def handle_message(sender_id, message_text):
    text = message_text.lower().strip()
    print(f"Received: {text}") # ესაც დავამატეთ რომ ლოგში ვნახოთ რა მოდის

    if any(word in text for word in ["გამარჯობა", "hi", "start", "მთავარი"]):
        send_message(sender_id,
            "გამარჯობა! 👋 \nკეთილი იყოს თქვენი მობრძანება უძრავი ქონების ოფისში!\n\nრით შემიძლია დაგეხმაროთ?",
            quick_replies=[
                {"title": "🏠 ყიდვა", "payload": "BUY"},
                {"title": "🔑 ქირა", "payload": "RENT"},
                {"title": "💰 გირავნობა", "payload": "MORTGAGE"},
                {"title": "📢 გაყიდვა", "payload": "SELL"}
            ]
        )

    elif text in ["buy", "rent", "mortgage", "sell"]:
        action = {"buy": "ყიდვა", "rent": "ქირა", "mortgage": "გირავნობა", "sell": "გაყიდვა"}[text]
        send_message(sender_id,
            f"შესანიშნავი! თქვენ აირჩიეთ: {action}\n\nახლა აირჩიეთ რეგიონი:",
            quick_replies=[
                {"title": "თბილისი", "payload": f"{text.upper()}_TBILISI"},
                {"title": "ბათუმი", "payload": f"{text.upper()}_BATUMI"},
                {"title": "ქუთაისი", "payload": f"{text.upper()}_KUTAISI"},
                {"title": "სხვა", "payload": f"{text.upper()}_OTHER"}
            ]
        )

    elif "_TBILISI" in text or "_BATUMI" in text or "_KUTAISI" in text or "_OTHER" in text:
        parts = text.split("_")
        action = parts[0]
        city = "თბილისი" if "TBILISI" in text else "ბათუმი" if "BATUMI" in text else "ქუთაისი" if "KUTAISI" in text else "სხვა რეგიონი"

        if action == "BUY":
            msg = f"{city}-ში იყიდება ამჟამად 🏠\n\n1. 2 ოთახიანი ბინა, ვაკე - 120,000$\n2. 3 ოთახიანი ბინა, საბურთალო - 150,000$\n3. სახლი, დიდუბე - 220,000$\n\nდამატებითი ვარიანტებისთვის ეწვიეთ ჩვენს ჯგუფს:\n{GROUP_LINK}"
        elif action == "RENT":
            msg = f"{city}-ში ქირავდება 🔑\n\n1. 1 ოთახიანი, ვაკე - 500$/თვე\n2. 2 ოთახიანი, საბურთალო - 700$/თვე\n3. სტუდიო, ცენტრი - 400$/თვე\n\nსხვა ვარიანტები: {GROUP_LINK}"
        elif action == "MORTGAGE":
            msg = f"გირავნობის შეთავაზებები {city}-ში 💰\n\nჩვენ გვაქვს საუკეთესო პირობები.\nდეტალები და განაცხადი: {GROUP_LINK}\n\nჩვენი მენეჯერი დაგიკავშირდებათ"
        elif action == "SELL":
            msg = f"დაგვეხმარებით გაყიდვაში {city}-ში! 📢\n\nატვირთეთ თქვენი ქონება ჩვენს ჯგუფში:\n{GROUP_LINK}\n\nან მოგვწერეთ დეტალები აქვე"

        msg += f"\n\nდამატებითი ინფორმაციისთვის ეწვიეთ ჩვენს გვერდს:\n{PAGE_LINK}"

        send_message(sender_id, msg, quick_replies=[{"title": "🔙 მთავარი მენიუ", "payload": "START"}])

    else:
        send_message(sender_id,
            "გთხოვთ აირჩიეთ ქვემოთ ერთ-ერთი ვარიანტი 👇",
            quick_replies=[
                {"title": "🏠 ყიდვა", "payload": "BUY"},
                {"title": "🔑 ქირა", "payload": "RENT"},
                {"title": "💰 გირავნობა", "payload": "MORTGAGE"},
                {"title": "📢 გაყიდვა", "payload": "SELL"}
            ]
        )

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Verification failed', 403
    if request.method == 'POST':
        data = request.get_json()
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                if 'message' in messaging_event and 'text' in messaging_event['message']:
                    handle_message(sender_id, messaging_event['message']['text'])
                elif 'postback' in messaging_event:
                    handle_message(sender_id, messaging_event['postback']['payload'])
        return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
