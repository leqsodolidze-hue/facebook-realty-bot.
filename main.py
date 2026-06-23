from fastapi import FastAPI, Request, Response
import re

app = FastAPI()

# საიდუმლო სიტყვა ფეისბუქისთვის
VERIFY_TOKEN = "chemi_saidumlo_tokeni_123"

def analyze_post(text: str):
    """ამოწმებს პოსტს 'უძრავი ქონების ყიდვის 19 წესი'-ს მიხედვით"""
    
    # წესი 1: ენა
    if not re.search(r'[\u10D0-\u10FA]', text):
        return {"action": "decline", "reason": "მხოლოდ ქართული ენა!"}
        
    # წესი 3: სპამ ფილტრი
    spam_keywords = ["სესხი", "კრიპტო", "t.me", "სამუშაო", "გადაუხადე"]
    if any(word in text.lower() for word in spam_keywords):
        return {"action": "ban", "reason": "სპამი"}

    # წესი 2: ტიპი
    if not ("ყიდვა" in text.lower() or "გაყიდვა" in text.lower() or "ქირავდება" in text.lower() or "დაქირავება" in text.lower()):
        return {"action": "ask", "reason": "მიუთითეთ: იყიდება თუ ქირავდება"}

    # წესი 9: ფასი
    has_price = bool(re.search(r'(ფასი|₾|\$|ლარი|დოლარი)', text.lower())) or bool(re.search(r'\b\d{3,}\b', text))
    if not has_price:
        return {"action": "ask", "reason": "მიუთითეთ ფასი!"}

    # წესი 10: მ2
    has_sq_m = bool(re.search(r'(მ2|კვ|კვადრატული)', text.lower()))
    if not has_sq_m:
        return {"action": "ask", "reason": "მიუთითეთ ფართი (მ2)!"}

    # წესი 11: ლოკაცია
    has_location = bool(re.search(r'(ლოკაცია|უბანი|ქუჩა|მდებარეობა)', text.lower()))
    if not has_location:
        return {"action": "ask", "reason": "მიუთითეთ ლოკაცია!"}

    # წესი 12: ტელეფონი
    has_phone = bool(re.search(r'5\d{2}', text)) # უხეში შემოწმება 5-იანით დაწყებაზე
    if not has_phone:
        return {"action": "ask", "reason": "მიუთითეთ ტელეფონის ნომერი!"}

    return {"action": "approve", "reason": "იდეალურია"}

@app.get("/webhook")
def facebook_verify(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return Response(content="Failed", status_code=403)

@app.post("/webhook")
async def facebook_webhook(request: Request):
    data = await request.json()
    print("მიღებული პოსტი:", data)
    return {"status": "success"}
