from flask import Flask, request
import os
import requests

app = Flask(__name__)

# === აქ ჩასვი შენი მონაცემები ===
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

# აქ ჩასვი შენი ნამდვილი ლინკები
GROUP_LINK = "https://www.facebook.com/groups/yourgroup" 
WEBSITE_LINK = "https://yourwebsite.ge"
# =================================

def send_text(sender_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    data = {
        "recipient": {"id": sender_id},
        "message": {"text": text}
    }
    requests.post(url, json=data)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Facebook-ის ვერიფიკაცია
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Verification failed', 403

    data = request.get_json()
    
    for entry in data['entry']:
        for messaging_event in entry['messaging']:
            sender_id = messaging_event['sender']['id']

            if 'message' in messaging_event:
                text = messaging_event['message'].get('text', '').strip().lower()

                # მენიუს გამოძახება
                if text == "menu" or text == "მენიუ" or text == "start":
                    text = ""

                # 1 - ყიდვა
                if text == "1":
                    reply = f"""🏠 ყიდვა

იხილეთ ჩვენი უახლესი შეთავაზებები:

🌐 საიტი: {WEBSITE_LINK}
👥 ჯგუფი: {GROUP_LINK}

დასაბრუნებლად დაწერეთ: მენიუ"""
                    send_text(sender_id, reply)

                # 2 - ქირა
                elif text == "2":
                    reply = f"""🔑 ქირა

იხილეთ ჩვენი უახლესი შეთავაზებები:

🌐 საიტი: {WEBSITE_LINK}
👥 ჯგუფი: {GROUP_LINK}

დასაბრუნებლად დაწერეთ: მენიუ"""
                    send_text(sender_id, reply)

                # 3 - გაყიდვა
                elif text == "3":
                    reply = f"""📢 გაყიდვა

გსურთ განცხადების განთავსება?
დაგვიკავშირდით ან დაპოსტეთ ჯგუფში:

👥 ჯგუფი: {GROUP_LINK}

დასაბრუნებლად დაწერეთ: მენიუ"""
                    send_text(sender_id, reply)

                # ყველაფერი დანარჩენი = მენიუ
                else:
                    menu = f"""გამარჯობა! 👋

აირჩიეთ რითი შემიძლია დაგეხმაროთ:

1️⃣ - ყიდვა 🏠
2️⃣ - ქირა 🔑  
3️⃣ - გაყიდვა 📢

დაწერეთ რიცხვი 1, 2 ან 3

⚠️ ყურადღება: ყველა განცხადება მხოლოდ ქართულად არის

🌐 საიტი: {WEBSITE_LINK}
👥 ჯგუფი: {GROUP_LINK}"""
                    send_text(sender_id, menu)

    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
