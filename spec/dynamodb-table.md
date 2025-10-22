# DynamoDB Table

**Name:** `wiki-dynamo-sandbox`

## Purpose
- Persist session and state data exchanged between Lambda, Bedrock, and MCP services.
- Store conversational history, metadata, and temporary context for the sandbox environment.

## Configuration
- **Partition Key:** `sessionId`
  - Type: `String`
  - Description: Unique identifier representing each user session or conversation instance.
- **Time-to-Live (TTL):** Enabled
  - Attribute: `expireAt`
  - Description: Automatically removes inactive or completed sessions when the epoch time in `expireAt` is reached.
