import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

AUTHORIZATION_TOKEN = os.environ.get("INTEGRATION_AUTH_TOKEN")
EVENT_BUS_NAME = "default"
EVENT_SOURCE = "lambda.telegram.listener"
EVENT_DETAIL_TYPE = "telegram.message.received"

eventbridge_client = boto3.client("events")

def lambda_handler(event, context):
    raw_body = event.get("body")
    parsed_body = json.loads(raw_body)

    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    auth_token = headers.get("x-telegram-bot-api-secret-token")

    if AUTHORIZATION_TOKEN:
        if auth_token != AUTHORIZATION_TOKEN:
            logging.warning("Invalid Authorization token in webhook request")
            return {
                "statusCode": 401,
                "body": json.dumps({"ok": False, "error": "Unauthorized"}),
            }
    try:
        payload = parsed_body
    except json.JSONDecodeError:
        logging.exception("Invalid webhook payload")
        return {
            "statusCode": 400,
            "body": json.dumps({"ok": False, "error": "Invalid payload"}),
        }

    update_type_keys = payload.keys()

    if "message" not in update_type_keys:
        logging.info("Non-message update received: %s", update_type_keys)
        return {"statusCode": 200, "body": json.dumps({"ok": True, "ignored": list(update_type_keys)})}

    message = payload.get("message")
    text = message.get("text")
    print ("Received inquiry:", text)
    session = message.get("chat")
    session_id = str(session.get("id"))
    print ("From source:", session_id)

    if not text or not session_id:
        logging.warning("Payload missing message or sender")
        return {
            "statusCode": 400,
            "body": json.dumps({"ok": False, "error": "Missing message or sender"}),
        }

    response_body = {
        "text": text,
        "sessionId": session_id,
    }

    if not EVENT_BUS_NAME:
        logging.error("EVENT_BUS_NAME environment variable is not configured")
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": "Server misconfiguration"}),
        }

    try:
        eventbridge_client.put_events(
            Entries=[
                {
                    "Source": EVENT_SOURCE,
                    "DetailType": EVENT_DETAIL_TYPE,
                    "Detail": json.dumps(response_body),
                    "EventBusName": EVENT_BUS_NAME,
                }
            ]
        )
    except ClientError:
        logging.exception("Failed to publish message to EventBridge")
        return {
            "statusCode": 502,
            "body": json.dumps({"ok": False, "error": "Event dispatch failed"}),
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Function executed successfully!"}),
    }
