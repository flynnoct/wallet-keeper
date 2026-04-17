import json

async def verify_id(user_id: str, source: str, env) -> bool:
    allowed_users = json.loads(env.ALLOWED_USERS)
    if source == "web_api":
        for user in allowed_users:
            if user.get("web_id") == user_id:
                return True
    return False
