import os
from fastapi import FastAPI, Request, Response

app = FastAPI()
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'my_secret_token_123')

@app.get("/webhook")
async def verify(request: Request):
    if request.query_params.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=request.query_params.get("hub.challenge"), status_code=200)
    return Response(status_code=403)

@app.post("/webhook")
async def webhook(request: Request):
    return Response(status_code=200)

@app.get("/")
async def home():
    return "Bot is running!"
