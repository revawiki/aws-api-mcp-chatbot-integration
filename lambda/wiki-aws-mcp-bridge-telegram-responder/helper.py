import os

def build_stream_url():
    host = os.environ["MCP_HOST"]
    return f"http://{host}/mcp/"

def build_prompt(event):
    text = event.get("text")
    return text