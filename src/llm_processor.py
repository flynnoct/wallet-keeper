import json
from workers import fetch

SYSTEM_PROMPT = """你是一个记账助手。从用户提供的文字、图片或语音转录中提取消费/收入信息，输出纯 JSON，不要有任何多余文字。

输出格式（所有字段必须存在）：
{
  "name": "消费名称，简短描述（如：星巴克拿铁、滴滴打车）",
  "amount": 数字（正数为支出，负数为收入，单位：元），
  "date": "YYYY-MM-DD",
  "channel": "支付渠道（如：微信支付、支付宝、现金、银行卡）",
  "category": "类别（如：餐饮、交通、购物、娱乐、收入等）"
}

如果某字段无法确定：date 用今天日期，channel 用"未知"，category 用"其他"。"""


async def extract(content_type: str, content, env) -> dict:
    api_key = env.AI_API_KEY
    api_endpoint = env.AI_API_ENDPOINT

    if content_type == "text":
        model = env.MODEL
        message = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content}
        ]
        response = await _extract(message, model, api_key, api_endpoint)
        response_content = json.loads(response.get("choices", [{}])[0].get("message", {}).get("content", ""))
    else:
        pass
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
    response = await fetch(api_endpoint, method="POST", headers=headers, body=json.dumps(request_body))
    response_data = await response.text()
    return json.loads(response_data)
