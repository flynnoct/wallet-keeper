import logging
from workers import Response, WorkerEntrypoint
from urllib.parse import urlparse

from auth import auth_id
from handlers import web_api as web_api_handler
from handlers import telegram_bot as telegram_bot_handler
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
            if result["status"] == "error":
                return Response(result["message"], status=400)
            
            # Verify the ID and source
            web_id = result["web_id"]
            username = await auth_id(web_id, "web_api", self.env)
            if not username:
                return Response("Unauthorized", status=401)

            # Extract the record and publish to Notion
            kind = result["kind"]
            content = result["content"]
            attachment = result["attachment"]
            extracted_record = await extract(kind, content, attachment, self.env)
            success = await publish_to_notion(extracted_record, username, self.env)
            if success:
                return Response("Published to Notion", status=200)
            return Response("Failed to publish to Notion", status=500)


        # Telegram Bot webhook
        elif path == "/telegram/webhook" and request.method == "POST":
            result = await telegram_bot_handler.parse(request)
            if result["status"] == "error":
                return Response("OK", status=200)
            if result["status"] == "ignored":
                return Response("OK", status=200)  # Always 200 to Telegram
            
            chat_id = result["chat_id"]
            user_id = result["user_id"]
            username = await auth_id(user_id, "telegram", self.env)

            if not username:
                await telegram_bot_handler.send_message(chat_id, "未授权，请联系管理员。", self.env)
                return Response("OK", status=200)
            
            content_type = result["content_type"]
            content = result["content"]
            extracted_record = await extract(content_type, content, self.env)
            success = await publish_to_notion(extracted_record, username, self.env)
            if success:
                reply = (
                    f"名称：{extracted_record.get('name')}\n"
                    f"金额：{extracted_record.get('amount')} 元\n"
                    f"日期：{extracted_record.get('date')}\n"
                    f"类别：{extracted_record.get('category')}\n"
                    f"渠道：{extracted_record.get('channel')}"
                )
                await telegram_bot_handler.send_message(chat_id, "Record saved!\n" + reply, self.env)
                return Response("OK", status=200)
            else:
                await telegram_bot_handler.send_message(chat_id, "Failed to save record.", self.env)
                return Response("OK", status=200)
        else:
            return Response("Not Found", status=404)
