# Lambda Functions

## WhatsApp Listener
**Name:** `wiki-aws-mcp-bridge-whatsapp-listener`

### Purpose
- Receive inbound WhatsApp messages via webhook and forward them to EventBridge.

### Configuration
- **Role:** `wiki-lambda-execution-role`
- **Timeout:** 15-30 seconds
- **Function URL:** Enabled (`AuthType: NONE`) for webhook access.

### Runtime
- Python 3.13

### Layer
- None

### Environment Variables
- `INTEGRATION_AUTH_TOKEN` — Generated secret for validating webhook calls.

## WhatsApp Responder
**Name:** `wiki-aws-mcp-bridge-whatsapp-responder`

### Purpose
- Communicate with MCP and Bedrock.
- Send generated messages to the WhatsApp API Gateway.

### Configuration
- **Role:** `wiki-lambda-execution-role`
- **Timeout:** 60-120 seconds

### Runtime
- Python 3.13

### Layer
- `wiki-pymcp`

### Environment Variables
- `INTEGRATION_API_TOKEN` — Generated token from the WhatsApp gateway.
- `MCP_HOST` — Hostname for the EC2 instance running MCP.
- `SESSION_TABLE_NAME` — DynamoDB table name used for session storage.

## Telegram Listener
**Name:** `wiki-aws-mcp-bridge-telegram-listener`

### Purpose
- Receive inbound Telegram messages via webhook and forward them to EventBridge.

### Configuration
- **Role:** `wiki-lambda-execution-role`
- **Timeout:** 15-30 seconds
- **Function URL:** Enabled (`AuthType: NONE`) for webhook access.

### Runtime
- Python 3.13

### Layer
- None

### Environment Variables
- `INTEGRATION_AUTH_TOKEN` — Generated secret for validating webhook calls.

## Telegram Responder
**Name:** `wiki-aws-mcp-bridge-telegram-responder`

### Purpose
- Communicate with MCP and Bedrock.
- Send outbound replies to Telegram chats using the Bot API.

### Configuration
- **Role:** `wiki-lambda-execution-role`
- **Timeout:** 60-120 seconds

### Runtime
- Python 3.13

### Layer
- `wiki-pymcp`

### Environment Variables
- `INTEGRATION_API_TOKEN` — Generated token from the WhatsApp gateway.
- `MCP_HOST` — Hostname for the EC2 instance running MCP.
- `SESSION_TABLE_NAME` — DynamoDB table name used for session storage.
