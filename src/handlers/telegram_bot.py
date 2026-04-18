import json
from workers import fetch

TELEGRAM_API_BASE = "https://api.telegram.org/bot"


async def parse(request) -> dict:
    try:
        body = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON body"}

    message = body.get("message")
    if not message:
        return {"status": "error", "message": "No message in update"}
    
    from_user = message.get("from", {})
    telegram_id = from_user.get("id")
    chat_id = message.get("chat", {}).get("id")

    if not telegram_id or not chat_id:
        return {"status": "error", "message": "Cannot identify user or chat"}

    text = message.get("text")
    if not text:
        return {"status": "ignored", "message": "Not a text message"}

    return {
        "status": "success",
        "source": "telegram",
        "content_type": "text",
        "content": text,
        "user_id": str(telegram_id),
        "chat_id": chat_id,
    }


async def send_message(chat_id: int, text: str, env):
    token = env.TELEGRAM_BOT_TOKEN
    url = f"{TELEGRAM_API_BASE}{token}/sendMessage"
    headers = {"Content-Type": "application/json"}
    body = json.dumps({"chat_id": chat_id, "text": text})
    await fetch(url, method="POST", headers=headers, body=body)
