from workers import Response, WorkerEntrypoint
from urllib.parse import urlparse

from llm_processor import extract
from handlers import web_api as web_api_handler

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
        # TODO: Add logic

        extracted_record = await extract(result["content_type"], result["content"], self.env)
        import json
        return Response(json.dumps(extracted_record), status=200)
