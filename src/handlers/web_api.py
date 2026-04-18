import base64


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
    data_type = body.get("type", "").lower()
    if data_type not in ["text", "image", "audio"]:
        return {"status": "error", "message": "Invalid data type. Must be 'text', 'image', or 'audio'"}
    
    # Extract the data
    raw_content = body.get("content")
    if not raw_content:
        return {"status": "error", "message": "Content is required"}
    
    # Handle the content based on the data type
    if data_type == "text":
        content = str(raw_content)
    else:  # For image and audio, we expect a base64-encoded string 
        try:
            content = base64.b64decode(raw_content)
        except Exception:
            return {"status": "error", "message": "Invalid base64 content"}

    return {
        "status": "success",
        "content_type": data_type, 
        "content": content,
        "web_id": web_id
    }