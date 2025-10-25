import json, time, re
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from bedrock import bedrock_client, bedrock_converse
from helper import build_stream_url, build_prompt
from session_store import load_session, save_session

MAX_TOOL_TEXT_CHARS = 10000
TIME_LIMIT_SECS = 60

def strip_thinking_tags(text: str) -> str:
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL).strip()
    return text

async def convo_session(event):
    print("Starting phase")
    phase = "start"
    errors = None
    response = None
    messages = []
    conversation_id = event.get("conversation_id")
    stored_session = load_session(conversation_id)
    
    if stored_session:
        print("Checking for stored session messages")
        history = stored_session.get("messages") or []
        if isinstance(history, list):
            messages = [m for m in history if isinstance(m, dict)]

    try:
        stream_url = build_stream_url()
        prompt = build_prompt(event)
        if prompt:
            messages.append({"role": "user", "content": [{"text": prompt}]})
        if not messages:
            return {"ok": False, "phase": phase, "error": "No prompt provided"}

        start = time.monotonic()
        timed_out = False

        try:
            async with streamablehttp_client(stream_url) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
                    print("MCP client session initialized")
                    phase = "initialize"
                    await session.initialize()

                    phase = "list_tools"
                    lt = await session.list_tools()

                    tools = [{
                        "toolSpec": {
                            "name": t.name,
                            "description": t.description or "",
                            "inputSchema": {"json": t.inputSchema},
                        }
                    } for t in lt.tools]

                    print("Tools loaded:", [t["toolSpec"]["name"] for t in tools])

                    br = bedrock_client()

                    print("Entering conversation loop")
                    phase = "first_converse"
                    response = bedrock_converse(br, tools, messages)
                    message = response.get("output", {}).get("message", {})
                    if message:
                        messages.append(message)

                    while response.get("stopReason") == "tool_use":
                        if time.monotonic() - start >= TIME_LIMIT_SECS:
                            timed_out = True
                            messages.append({"role": "user", "content": [{"text": "Tools usage limit reached. Generate answer with anything you get."}]})
                            response = bedrock_converse(br, tools, messages)
                            break

                        print("Handling tool use")
                        phase = "tool_use_dispatch"
                        for block in message.get("content", []):
                            tu = block.get("toolUse")
                            if not tu:
                                continue
                            tool_name = tu["name"]
                            tool_args = tu.get("input", {}) or {}
                            tool_use_id = tu["toolUseId"]

                            phase = f"call_tool:{tool_name}"

                            try:
                                result = await session.call_tool(tool_name, tool_args)
                            except ExceptionGroup as eg:
                                print(f"[WARN] MCP tool '{tool_name}' raised an ExceptionGroup:")
                                for e in eg.exceptions:
                                    print(f"  - {type(e).__name__}: {e}")
                                continue
                            except Exception as e:
                                print(f"[WARN] MCP tool '{tool_name}' failed: {type(e).__name__}: {e}")
                                continue

                            parts = []
                            for p in result.content:
                                tp = getattr(p, "type", None)
                                if tp == "json":
                                    parts.append(json.dumps(p.json, ensure_ascii=False))
                                elif tp == "text":
                                    parts.append(p.text)
                            tool_text = "\n".join(parts) if parts else ""
                            if len(tool_text) > MAX_TOOL_TEXT_CHARS:
                                tool_text = tool_text[:MAX_TOOL_TEXT_CHARS] + "\n...[truncated]"

                            messages.append({
                                "role": "user",
                                "content": [{
                                    "toolResult": {
                                        "toolUseId": tool_use_id,
                                        "content": [{"text": tool_text}],
                                    }
                                }],
                            })

                            print(f"Tools called, continuing conversation")
                            phase = "followup_converse"
                            response = bedrock_converse(br, tools, messages)
                            message = response.get("output", {}).get("message", {})
                            if message:
                                messages.append(message)

        except* Exception as eg:
            errors = [f"{type(e).__name__}: {e}" for e in eg.exceptions]

        if not response:
            return {"ok": False, "phase": phase, "error": "No response from Bedrock"}

        final = response.get("output", {}).get("message", {})

        answer = strip_thinking_tags(
            "\n".join(
                c.get("text") for c in final.get("content", []) if "text" in c
            ).strip()
        )

        if errors is not None:
            return {"ok": False, "phase": phase, "errors": errors, "answer": answer}

        return {"ok": True, "answer": answer}

    except Exception as e:
        return {"ok": False, "phase": phase, "error": f"{type(e).__name__}: {e}"}
    finally:
        try:
            await session.aclose()
        except Exception:
            pass
        print("Conversation completed")
        if conversation_id and messages:
            cleaned_messages = []

            for msg in messages:
                role = msg.get("role")
                content = msg.get("content", [])
                cleaned_content = []

                for block in content:
                    if "text" in block:
                        text = strip_thinking_tags(block["text"])
                        if text.strip():
                            cleaned_content.append({"text": text.strip()})
                    elif "toolUse" in block or "toolResult" in block:
                        continue

                if cleaned_content:
                    cleaned_messages.append({"role": role, "content": cleaned_content})

            save_session(conversation_id, cleaned_messages)
