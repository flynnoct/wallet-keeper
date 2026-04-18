from workers import Response, WorkerEntrypoint
from urllib.parse import urlparse

from auth import auth_id
from handlers import web_api as web_api_handler
from llm_processor import extract
from notion_connector import publish_to_notion

class Default(WorkerEntrypoint):
    async def fetch(self, request, env):
        url_str = request.url
        path = urlparse(url_str).path
        if path == "/health":
            return Response("OK", status=200)
        # Web API
        elif path == "/api/submit" and request.method == "POST":
            result = await web_api_handler.parse(request)
        # TODO: Telegram Bot
        else:
            return Response("Not Found", status=404)
        if result["status"] == "error":
            return Response(result["message"], status=400)

        # Verify the ID and source
        user = await auth_id(str(result["user_id"]), result["source"], self.env)
        if not user:
            return Response("Unauthorized", status=401)

        extracted_record = await extract(result["content_type"], result["content"], self.env)
        success = await publish_to_notion(extracted_record, user, self.env)
        if success:
            return Response("OK", status=200)
        return Response("Failed to publish to Notion", status=500)
