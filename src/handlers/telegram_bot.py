import base64
import httpx

TELEGRAM_API_BASE = "https://api.telegram.org/bot"
TELEGRAM_FILE_BASE = "https://api.telegram.org/file/bot"


async def _get_data_base64(file_id: str, token: str) -> str:
    get_file_url = f"{TELEGRAM_API_BASE}{token}/getFile?file_id={file_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(get_file_url)
        data = response.json()
        file_path = data["result"]["file_path"]

        download_url = f"{TELEGRAM_FILE_BASE}{token}/{file_path}"
        file_response = await client.get(download_url)
    return base64.b64encode(file_response.content).decode("utf-8")


async def parse(request, env) -> dict:
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

    # Handle photo messages
    photos = message.get("photo")
    if photos:
        largest = max(photos, key=lambda p: p.get("file_size", 0))
        file_id = largest["file_id"]
        caption = message.get("caption", "")
        attachment = await _get_data_base64(file_id, env.TELEGRAM_BOT_TOKEN)
        return {
            "status": "success",
            "source": "telegram",
            "kind": "image",
            "content": caption,
            "attachment": attachment,
            "user_id": str(telegram_id),
            "chat_id": chat_id,
        }

    # Handle voice messages
    voice = message.get("voice")
    if voice:
        file_id = voice["file_id"]
        attachment = await _get_data_base64(file_id, env.TELEGRAM_BOT_TOKEN)
        return {
            "status": "success",
            "source": "telegram",
            "kind": "audio",
            "content": "",
            "attachment": attachment,
            "user_id": str(telegram_id),
            "chat_id": chat_id,
        }

    # Handle text messages
    text = message.get("text")
    return {
        "status": "success",
        "source": "telegram",
        "kind": "text",
        "content": text,
        "attachment": None,
        "user_id": str(telegram_id),
        "chat_id": chat_id,
    }


async def send_message(chat_id: int, text: str, env, parse_mode: str = "HTML"):
    token = env.TELEGRAM_BOT_TOKEN
    url = f"{TELEGRAM_API_BASE}{token}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode})
