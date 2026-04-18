# Wallet Keeper

一个运行在 Cloudflare Workers 上的个人记账助手，支持通过 Telegram Bot 或 Web API 提交消费记录，由 AI 自动提取结构化信息并保存到 Notion 数据库。

## 功能

- **多渠道输入**：支持 Telegram Bot 和 Web API 两种方式提交记录
- **多媒体识别**：支持文字描述、图片（收据/发票）、语音记录三种输入格式
- **AI 智能提取**：调用大语言模型自动解析自然语言，提取金额、日期、类别等结构化信息
- **自动分类**：自动识别消费类别（餐饮、交通、购物、娱乐、收入等）和支付渠道（微信、支付宝、现金等）
- **Notion 同步**：提取完成后自动将记录写入用户的 Notion 数据库
- **多用户支持**：每个用户独立配置 Notion 工作区和 API Key

## 前置准备

在部署前，你需要准备以下内容：

1. **Cloudflare 账号**，并开通 Workers 服务
2. **Notion 集成**：在 [Notion Developers](https://www.notion.so/my-integrations) 创建 Integration，获取 API Key，并创建用于记账的数据库（需包含 `Name`、`Amount`、`Date`、`Category`、`Channel` 属性）
3. **字节跳动火山引擎账号**（用于 AI 提取），获取 API Key 和模型接入点
4. **Telegram Bot**（可选）：通过 BotFather 创建 Bot，获取 Bot Token

### Notion 数据库结构

数据库需包含以下属性：

| 属性名 | 类型 |
|--------|------|
| Name | Title |
| Amount | Number |
| Date | Date |
| Category | Select |
| Channel | Select |

## 部署

### 1. 克隆并安装依赖

```bash
git clone https://github.com/your-username/wallet-keeper.git
cd wallet-keeper

npm install
uv sync
```

### 2. 配置环境变量

新建 `.dev.vars` 文件，填入以下内容：

```ini
# 火山引擎 AI API Key
AI_API_KEY=your_volcengine_api_key

# Telegram Bot Token（不使用 Telegram 可留空）
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# 用户配置（JSON 格式，支持多用户）
ALLOWED_USERS={"alice":{"telegram_user_id":"123456789","web_id":"3d51dc0f-d798-4312-b50c-199a8ee13e25","notion_database_id":"your_notion_db_id","notion_api_key":"secret_xxx"}}
```

`ALLOWED_USERS` 中每个用户包含以下字段：

| 字段 | 说明 |
|------|------|
| `telegram_user_id` | Telegram 用户 ID（通过 @userinfobot 获取） |
| `web_id` | Web API 鉴权 ID，建议使用 UUID |
| `notion_database_id` | Notion 数据库 ID（从数据库 URL 中提取） |
| `notion_api_key` | Notion Integration 的 API Key |

### 3. 本地开发

```bash
npm run dev
```

服务将在 `http://localhost:8787` 启动。

### 4. 部署到 Cloudflare Workers

```bash
npm run deploy
```

部署成功后，Cloudflare 会返回形如 `https://wallet-keeper.your-subdomain.workers.dev` 的访问地址。

### 5. 配置 Telegram Webhook（使用 Telegram 时）

将 Webhook 指向你的 Worker 地址：

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://wallet-keeper.your-subdomain.workers.dev/telegram/webhook"
```

## 使用指南

### 通过 Telegram Bot

向 Bot 发送以下任意格式的消息即可记账：

**文字**
> 今天午饭吃了麦当劳，花了 38 块，用微信支付的

**图片**
> 发送小票或发票截图，可附带文字说明

**语音**
> 发送语音消息，口述消费内容即可（如"晚上打车回家，花了 26 块"）

Bot 成功处理后会回复提取到的记录详情：

```
✅ 记录已保存
名称：麦当劳午餐
金额：38
日期：2026-04-18
类别：餐饮
渠道：微信
```

### 通过 Web API

**提交文字记录**

```bash
curl -X POST https://wallet-keeper.your-subdomain.workers.dev/api/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_web_id>" \
  -d '{
    "kind": "text",
    "content": "星巴克拿铁 45 元，支付宝付款"
  }'
```

**提交图片记录**

```bash
curl -X POST https://wallet-keeper.your-subdomain.workers.dev/api/submit \
  -H "Content-Type: application/json" \
  -d '{
    "web_id": "<your_web_id>",
    "kind": "image",
    "content": "这是一张超市小票",
    "attachment": "<base64_encoded_image>"
  }'
```

鉴权方式支持两种：
- `Authorization: Bearer <web_id>` 请求头
- 请求体中的 `web_id` 字段

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `kind` | string | 是 | 输入类型：`text` / `image` |
| `content` | string | 是 | 文字描述或图片说明 |
| `attachment` | string | image 时必填 | Base64 编码的图片内容 |
| `web_id` | string | 未使用 Header 时必填 | 用户鉴权 ID |

**返回示例**

```json
{
  "record": {
    "name": "星巴克拿铁",
    "amount": 45,
    "date": "2026-04-18",
    "channel": "支付宝",
    "category": "餐饮"
  },
  "message": "Record saved to Notion"
}
```

**健康检查**

```bash
curl https://wallet-keeper.your-subdomain.workers.dev/health
# 返回: OK
```

## 支持的分类与渠道

**消费类别**：餐饮、交通、购物、娱乐、收入、其他

**支付渠道**：微信、支付宝、现金、银行卡、信用卡、其他

## 技术栈

- **运行环境**：Cloudflare Workers (Python)
- **AI 模型**：字节跳动火山引擎 Doubao
- **语音识别**：Cloudflare Workers AI (Whisper)
- **数据存储**：Notion API
- **Telegram 集成**：Telegram Bot API
