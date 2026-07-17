from flask import Flask, request
import requests
import os

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

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
    message_text = message_text.lower().strip()
    
    if any(word in message_text for word in ["გამარჯობა", "hi", "hello", "start", "დაწყება"]):
        send_message(sender_id, 
            "გამარჯობა! 👋\nკეთილი იყოს თქვენი მობრძანება უძრავი ქონების ოფისში!\n\nროგორ შემიძლია დაგეხმაროთ?",
            quick_replies=[
                {"title": "🏠 ყიდვა", "payload": "BUY"},
                {"title": "🔑 ქირა", "payload": "RENT"}, 
                {"title": "📞 კონტაქტი", "payload": "CONTACT"}
            ]
        )
    
    elif message_text == "buy":
        send_message(sender_id, "შესანიშნავი! 🏠\nრა გაინტერესებთ?\n1. ბინა\n2. სახლი\n3. კომერციული ფართი")
    
    elif message_text == "rent":
        send_message(sender_id, "გავიგე! 🔑\nქირისთვის რომელი უბანი და ბიუჯეტი გაქვთ?")
    
    elif message_text == "contact":
        send_message(sender_id, "დაგვიკავშირდით 📞\nტელ: 555 12 34 56\nმის: თბილისი, ვაჟა-ფშაველა\nვმუშაობთ: 10:00 - 19:00")
    
    else:
        send_message(sender_id,
            "მადლობა შეტყობინებისთვის: '" + message_text + "' 😊\n\nგთხოვთ აირჩიეთ ქვემოთ ერთ-ერთი ვარიანტი:",
            quick_replies=[
                {"title": "🏠 ყიდვა", "payload": "BUY"},
                {"title": "🔑 ქირა", "payload": "RENT"},
                {"title": "📞 კონტაქტი", "payload": "CONTACT"}
            ]
        )

def handle_postback(sender_id, payload):
    handle_message(sender_id, payload.lower())

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
                    handle_postback(sender_id, messaging_event['postback']['payload'])
        
        return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
