import json

async def auth_id(user_id: str, source: str, env) -> str:
    """
    Verify and return username based on the provided user ID and source.
    """
    allowed_users = json.loads(env.ALLOWED_USERS)
    if source == "web_api":
        for user, properties in allowed_users.items():
            if properties.get("web_id") == user_id:
                return user
    elif source == "telegram":
        for user, properties in allowed_users.items():
            if str(properties.get("telegram_user_id")) == str(user_id):
                return user
    return None
