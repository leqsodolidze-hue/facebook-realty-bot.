from flask import Flask, request
import os
import requests

app = Flask(__name__)
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

GROUP_LINK = "https://www.facebook.com/groups/yourgroup"
WEBSITE_LINK = "https://yourwebsite.ge"

def send_text(sender_id, text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": sender_id}, "message": {"text": text}})

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

            # ვინც შემოვა პირდაპირ მივაწოდოთ მენიუ ტექსტად
            message = """გამარჯობა! 👋

აირჩიეთ რითი შემიძლია დაგეხმაროთ:

1️⃣ - ყიდვა 🏠
2️⃣ - ქირა 🔑  
3️⃣ - გაყიდვა 📢

დაწერეთ რიცხვი 1, 2 ან 3

⚠️ ყურადღება: ყველა განცხადება მხოლოდ ქართულად არის

საიტი: """ + WEBSITE_LINK + """
ჯგუფი: """ + GROUP_LINK
            
            send_text(sender_id, message)

    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
