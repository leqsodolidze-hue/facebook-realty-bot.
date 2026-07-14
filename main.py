from flask import Flask, request
import os

app = Flask(__name__)
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN') 
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')

@app.route('/webhook', methods=['GET']) # << ეს უკვე გაქვს
def verify():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == VERIFY_TOKEN:
        return challenge
    return 'Error: Wrong token', 403

@app.route('/webhook', methods=['POST']) # <<<< ეს დაუმატე ბოლოში
def webhook():
    data = request.get_json()
    print("Facebook sent:", data)
    return "ok", 200

if __name__ == '__main__':
    app.run()
