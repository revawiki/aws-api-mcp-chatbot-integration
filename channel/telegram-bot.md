# Telegram Bot Setup

## Prerequisites
- Telegram account with access to the **@BotFather**.
- HTTPS endpoint to the Lambda listener (`wiki-aws-mcp-bridge-telegram-listener`).

## Create the Bot
1. Open Telegram and start a chat with `@BotFather`.
2. Run `/newbot` and follow the prompts to choose the bot name and username.
3. Copy the TELEGRAM BOT TOKEN that BotFather returns; store it securely (needed for outbound responses).

## Configure Webhook
1. Publish the Telegram Lambda listener through API Gateway or a Function URL (AuthType `NONE`).
2. Set the bot webhook to the public HTTPS endpoint:
   ```bash
   curl -X POST 'https://api.telegram.org/bot<your-telegram-bot-token-for-INTEGRATION_API_TOKEN>/setWebhook' \
     -d 'url=https://<your-telegram-lambda-listener-function-url>' \
     -d 'secret_token=<your-self-generated-secret-token-for-INTEGRATION_AUTH_TOKEN>' \
     -d 'allowed_updates=["message"]'
   ```
3. Verify the webhook:
   ```bash
   curl "https://api.telegram.org/bot<your-telegram-bot-token>/getWebhookInfo"
   ```

## Creating Dedicated Group
1. Back to **@BotFather** run `/mybot` then **Bot Settings**
2. Choose **Allow Groups?**, make sure it's enabled (turned on).
3. Go back, choose **Group Privacy**, make sure it's disabled (turned off).
4. Create a new chat group, add the Bot as new member.
5. Makesure Bot shown *'has access to messages'*, otherwise promote the bot to Admin.

## Testing
1. Send a message regarding AWS inquiries to the dedicated group.
2. Confirm CloudWatch Logs show the listener receiving an event and forwarding to EventBridge.
3. Ensure the responder Lambda posts a reply via the `sendMessage` API and the chat receives it.
