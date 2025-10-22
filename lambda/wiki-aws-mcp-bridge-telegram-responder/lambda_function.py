import json
import logging
import os
import anyio

from mcp_runner import convo_session
from messaging import format_outbound_message, send_message

def lambda_handler(event, context):
    raw_body = event.get("detail")
    parsed_body = raw_body

    try:
        payload = parsed_body
    except json.JSONDecodeError:
        logging.exception("Invalid payload")
        return {
            "statusCode": 400,
            "body": json.dumps({"ok": False, "error": "Invalid payload"}),
        }

    text = payload.get("text")
    session_id = payload.get("sessionId")

    if not text or not session_id:
        logging.warning("Payload missing text or sessionId")
        return {
            "statusCode": 400,
            "body": json.dumps({"ok": False, "error": "Missing text or sessionId"}),
        }

    conversation_id = f"telegram:{session_id}"
    convo_event = {
        "text": text,
        "conversation_id": conversation_id,
    }

    try:
        print("Initializing conversation session")
        out = anyio.run(convo_session, convo_event)
    except Exception as ex:
        logging.exception("Error executing conversation session")
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": str(ex)}),
        }

    response_text = format_outbound_message(out)
    send_result = send_message(response_text, session_id)

    return {
        "statusCode": 200,
        "body": json.dumps({ "message": "Function executed successfully!" }),
    }
