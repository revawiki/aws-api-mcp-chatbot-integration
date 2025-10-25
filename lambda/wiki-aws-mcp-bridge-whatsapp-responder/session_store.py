import logging
import os
import time
from typing import Any, Dict, Iterable, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

SESSION_TABLE_NAME = os.environ.get("SESSION_TABLE_NAME")
MAX_SESSION_MESSAGES = 5
SESSION_TTL_SECONDS = 600
SESSION_TTL_ATTRIBUTE = "expireAt"

_dynamodb = None
_table = None

def _get_table():
    global _dynamodb, _table
    if _table is not None:
        return _table
    if not SESSION_TABLE_NAME:
        return None
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", config=Config(read_timeout=3, connect_timeout=2, retries={"max_attempts": 2}))
    _table = _dynamodb.Table(SESSION_TABLE_NAME)
    return _table

def _normalize_messages(messages: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    if not isinstance(messages, list):
        return []
    trimmed = messages[-MAX_SESSION_MESSAGES :] if MAX_SESSION_MESSAGES > 0 else messages
    sanitized = []
    for item in trimmed:
        if isinstance(item, dict):
            sanitized.append(item)
    return sanitized

def _compute_ttl_epoch(now: int) -> Optional[int]:
    if SESSION_TTL_SECONDS <= 0 or not SESSION_TTL_ATTRIBUTE:
        return None
    return now + SESSION_TTL_SECONDS

def load_session(session_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not session_id:
        return None
    table = _get_table()
    if table is None:
        return None
    
    response = table.get_item(Key={"sessionId": session_id})

    item = response.get("Item")
    if not item:
        return None

    ttl_attr = SESSION_TTL_ATTRIBUTE if SESSION_TTL_ATTRIBUTE else None
    
    if ttl_attr and ttl_attr in item:
        expires_at = int(item[ttl_attr])
    else:
        expires_at = None
        
    if expires_at is not None and expires_at <= int(time.time()):
        return None

    messages = _normalize_messages(item.get("messages", []))
    return {"messages": messages}

def save_session(session_id: str, messages: Iterable[Dict[str, Any]]):
    if not session_id:
        return
    table = _get_table()
    if table is None:
        return

    now = int(time.time())

    filtered_messages = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", [])
        if role not in ("user", "assistant"):
            continue

        clean_content = []
        for block in content:
            if "text" in block:
                clean_content.append({"text": block["text"]})

        if clean_content:
            filtered_messages.append({
                "role": role,
                "content": clean_content
            })

    normalized_messages = list(_normalize_messages(filtered_messages))

    item: Dict[str, Any] = {
        "sessionId": session_id,
        "messages": normalized_messages,
        "updatedAt": now,
    }

    ttl_epoch = _compute_ttl_epoch(now)
    if ttl_epoch is not None:
        item[SESSION_TTL_ATTRIBUTE] = ttl_epoch

    try:
        table.put_item(Item=item)
    except (ClientError, BotoCoreError):
        logging.exception("Failed to persist session '%s' to DynamoDB", session_id)
