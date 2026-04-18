import base64
import json


async def parse(request) -> dict:
    try:
        body = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON body"}

    # Extract the ID from the body or the Authorization header
    web_id = body.get("web_id")
    if not web_id:
        auth_header = request.headers.get("Authorization") or ""
        if auth_header.startswith("Bearer "):
            web_id = auth_header[len("Bearer "):]
    if not web_id:
        return {"status": "error", "message": "Web ID is required"}
    
    # Parse the data type
    kind = body.get("kind", "").lower()
    if kind not in ["text", "image", "audio"]:
        return {"status": "error", "message": "Invalid data type. Must be 'text', 'image', or 'audio'"}
    
    # Extract the data
    raw_content = body.get("content")
    if not raw_content:
        return {"status": "error", "message": "Content is required"}
    
    # Handle the content based on the data type
    if kind == "text":
        content = str(raw_content)
        attachment = None
    elif kind == "image":
        try:
            content = str(raw_content)
            attachment = str(body.get("attachment"))
        except Exception:
            return {"status": "error", "message": "Invalid image data"}
    else: # audio
        return {"status": "error", "message": "Unsupported data type"}
    return {
        "status": "success",
        "kind": kind, 
        "content": content,
        "attachment": attachment,
        "web_id": web_id
    }