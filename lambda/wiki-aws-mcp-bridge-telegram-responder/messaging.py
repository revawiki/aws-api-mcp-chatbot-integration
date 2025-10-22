from typing import Any, Dict
import os
import requests
import logging

INTEGRATION_API_URL = "https://api.telegram.org"

def format_outbound_message(out: Any) -> str:
    lines = []

    answer = ""
    warning = ""
    if isinstance(out, dict):
        answer = out.get("answer") or ""
        if not out.get("ok", True):
            err = out.get("error") or "; ".join(out.get("errors", []) or [])
            if err:
                warning = f"Warning: {err}"
    else:
        answer = str(out or "")

    answer = answer.strip()
    if answer:
        lines.append(answer)
    if warning:
        lines.append(warning)

    if not lines:
        lines.append("(no response)")

    return "\n".join(lines)

def send_message(message: str, guid: str) -> Dict[str, Any]:
    token = os.environ.get("INTEGRATION_API_TOKEN")

    if not token:
        logging.error("INTEGRATION_API_TOKEN is not set in environment variables.")
        return {"status": "error", "reason": "Missing API token"}

    if not guid:
        logging.error("WhatsApp Group ID is missing.")
        return {"status": "error", "reason": "Missing WhatsApp group id"}

    api_url = f"{INTEGRATION_API_URL}/bot{token}/sendMessage"

    try:
        response = requests.post(
            api_url,
            json={
                "chat_id": guid,
                "text": message or "(no message)",
                "parse_mode": "Markdown",
            },
            timeout=15,
        )
        response.raise_for_status()

        try:
            return response.json()
        except ValueError:
            logging.warning("Integration response is not JSON; returning text body")
            return {"status": "ok", "body": response.text}
            
    except requests.exceptions.HTTPError as http_err:
        logging.error("HTTP error from Integration: %s - %s", http_err, response.text)
        return {"status": "error", "reason": str(http_err)}
    except requests.exceptions.Timeout:
        logging.error("Integration API request timed out.")
        return {"status": "error", "reason": "Timeout"}
    except requests.exceptions.RequestException as exc:
        logging.error("Unexpected error sending message to Integration: %s", exc)
        return {"status": "error", "reason": str(exc)}