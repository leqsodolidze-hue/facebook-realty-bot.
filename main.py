from flask import Flask, request

app = Flask(__name__)

# დროებით პირდაპირ ჩაწერე რომ პრობლემა არ იყოს
VERIFY_TOKEN = "mysecret123" 

@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Wrong token", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Message received:", data)
    return "ok", 200

if __name__ == '__main__':
    app.run()
