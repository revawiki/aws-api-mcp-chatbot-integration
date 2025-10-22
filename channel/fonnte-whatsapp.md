# Fonnte WhatsApp Gateway

## Overview
Fonnte is one of the many UNOFFICIAL WhatsApp Gateway created by fellow Indonesian, mas Levi.
This prototype choose Fonnte for ease-of-use in the setup.
**DISCLAIMER** Using UNOFFICIAL WhatsApp Gateway could prone for [BLOCKED ACCOUNT](https://fonnte.com/tutorial/informasi-terkait-banned/), you have been warned!

## Prerequisites
- Fonnte account with a verified WhatsApp number to be-used as bot.
- HTTPS endpoint for the Lambda listener (`wiki-aws-mcp-bridge-whatsapp-listener`).

## First-thing-first
1. Log in to the Fonnte dashboard.
2. Navigate to **Devices** and **Link a new device**.
3. Follow the website guidance to register a WhatsApp account number.
4. Go back to the newly linked device, click **Edit**.
5. Enable **autoread**, click **Update**.

## Creating Dedicated Group
1. Create a WhatsApp group, add the WhatsApp account which you used to register the device.
2. Send any message once.

## Obtaining API Credentials and WhatsApp Group Id
1. For the newly linked devices, click **Token**. This is the API token to be used for INTEGRATION_API_TOKEN in lambda-responder.
2. Go to **Phonebook** -> **WA Group**, click *Update List*. Copy the newly created group id from the list.

## Configure Webhook
1. Go to the newly linked devices, click **Flow**.
2. Create a flow, add Logic **Condition** link-it to start.
3. Configure the condition node, set **Sender = {previously-copied-whasapp-group-id}**
4. Add Action **Webhook** link-it to the previous condition.
5. Configure the webhook node, set **URL** with *lambda function url* and **Secret key** *with your-self generated secret for INTEGRATION_AUTH_TOKEN*.
6. Click **Save**.

## Activate flow
1. Go back to the newly linked device, click **Edit**.
2. Set **Respond Source** to **Flow**.
3. Enable **Group** for autoreply.
4. Click **Update** to save, then click **Reconnect**.

## Testing
1. Send a message regarding AWS inquiries to the dedicated group.
2. Confirm CloudWatch Logs show the listener receiving an event and forwarding to EventBridge.
3. Ensure the responder Lambda posts a reply via the `Fonnte send` API and the chat receives it.
