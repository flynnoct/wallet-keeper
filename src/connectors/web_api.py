import base64


async def parse(request) -> dict:
    try:
        body = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON body"}

    # Extract the API key from the body or the Authorization header
    api_key = body.get("api_key")
    if not api_key:
        auth_header = request.headers.get("Authorization") or ""
        if auth_header.startswith("Bearer "):
            api_key = auth_header[len("Bearer "):]
    if not api_key:
        return {"status": "error", "message": "API key is required"}
    
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
        "id": api_key
    }