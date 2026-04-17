from workers import Response, WorkerEntrypoint
from urllib.parse import urlparse

from connectors import web_api as web_api_connector

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url_str = request.url
        path = urlparse(url_str).path
        if path == "/health":
            return Response("OK", status=200)
        # Web API
        elif path == "/api/submit" and request.method == "POST":
            result = await web_api_connector.parse(request)
            if result["status"] == "error":
                return Response(result["message"], status=400)
            # Process the content as needed (e.g., store it, trigger actions, etc.)
            # For demonstration, we just return the parsed content
            import json
            return Response(json.dumps(result), status=200)
