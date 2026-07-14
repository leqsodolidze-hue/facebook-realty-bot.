from flask import Flask, request
import os
import requests

app = Flask(__name__)
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN') # Render-იდან აიღებს secret123-ს
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN') # ესეც დაგვჭირდება მესიჯების გასაგზავნად

@app.route('/webhook', methods=['GET'])
def verify():
    # Facebook აქ ამოწმებს
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == VERIFY_TOKEN:
        return challenge 
    return 'Error: Wrong token', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    # აქ მოგვივა მესიჯები
    data = request.get_json()
    print(data)
    return 'ok', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 10000))
