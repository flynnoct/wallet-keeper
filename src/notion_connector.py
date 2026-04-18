import json
from workers import fetch

NOTION_API_VERSION = "2026-03-11"
NOTION_PAGES_URL = "https://api.notion.com/v1/pages"


async def publish_to_notion(record: dict, user: str, env):

    user = json.loads(env.ALLOWED_USERS).get(user)
    notion_token = user.get("notion_api_key")
    database_id = user.get("notion_database_id")
    if not notion_token or not database_id:
        return False

    body = {
        "parent": {
            "type": "data_source_id",
            "data_source_id": database_id
        },
        "properties": {
            "Name": {
                "type": "title",
                "title": [{ "type": "text", "text": { "content": record.get("name", "") } }]
            },
            "Amount": {
                "type": "number",
                "number": record.get("amount", 0)
            },
            "Date": {
                "type": "date",
                "date": { "start": record.get("date", "") }
            },
            "Category": {
                "type": "select",
                "select": { "name": record.get("category", "") }
            },
            "Channel": {
                "type": "select",
                "select": { "name": record.get("channel", "") }
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION
    }

    response = await fetch(NOTION_PAGES_URL, method="POST", headers=headers, body=json.dumps(body))
    return response.status == 200
