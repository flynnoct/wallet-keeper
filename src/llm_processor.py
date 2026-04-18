import base64
import json
import httpx
from datetime import datetime

SYSTEM_PROMPT = """你是一个记账助手。从用户提供的文字、图片或语音转录中提取消费/收入信息，输出纯JSON。

输出格式：
{
  "name": "消费名称，简短描述（如：星巴克拿铁、晚餐麦当劳）",
  "amount": 数字（正数为支出，负数为收入，单位：元）,
  "date": "YYYY-MM-DD"格式的日期字符串，如果用户没有提供日期，默认为当天。今天的日期是：%s",
  "channel": "支付渠道，从如下列表中选择：微信、支付宝、现金、银行卡、信用卡、其他",
  "category": "类别，从如下列表中选择：餐饮、交通、购物、娱乐、收入、其他"
}
"""


async def extract(kind: str, content, attachment, env) -> dict:
    api_key = env.AI_API_KEY
    api_endpoint = env.AI_API_ENDPOINT
    default_date = datetime.now().strftime("%Y-%m-%d")

    message = [
        {"role": "system", "content": SYSTEM_PROMPT % default_date},
    ]
    model = env.MODEL
    if kind == "text":
        message.append({"role": "user", "content": content})
    elif kind == "image" and attachment:
        message.append({
            "role": "user",
            "content": [{
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{attachment}"}
            }, {
                "type": "text",
                "text": content
            }]
        })
    elif kind == "audio" and attachment:
        audio_bytes = base64.b64decode(attachment)
        whisper_result = await env.AI.run("@cf/openai/whisper", {"audio": list(audio_bytes)})
        transcription = whisper_result.text
        message.append({"role": "user", "content": transcription})
    response = await _extract(message, model, api_key, api_endpoint)
    response_content = json.loads(response.get("choices", [{}])[0].get("message", {}).get("content", ""))
    return response_content


async def _extract(messages, model, api_key, api_endpoint):
    request_body = {
        "model": model,
        "messages": messages,
        "stream": False,
          "thinking": {
            "type": "disabled"
        },
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "extracted_financial_record",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "amount": {"type": "number"},
                        "date": {"type": "string", "format": "date"},
                        "channel": {"type": "string"},
                        "category": {"type": "string"}
                    },
                    "required": ["name", "amount", "date", "channel", "category"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(api_endpoint, headers=headers, content=json.dumps(request_body))
    return json.loads(response.text)
