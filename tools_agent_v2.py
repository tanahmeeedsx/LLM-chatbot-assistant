import json
import shutil
from pathlib import Path
import requests

API_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"
PROJECT_DIR = Path.cwd().resolve()

def list_project_files():
    return sorted(
        item.name + ("/" if item.is_dir() else "")
        for item in PROJECT_DIR.iterdir()
        if item.name != ".venv"
    )

def get_disk_usage():
    usage = shutil.disk_usage(PROJECT_DIR)
    return {
        "total_gb": round(usage.total / (1024 ** 3), 2),
        "used_gb": round((usage.total - usage.free) / (1024 ** 3), 2),
        "free_gb": round(usage.free / (1024 ** 3), 2),
    }

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_project_files",
            "description": "List files and folders in the current project.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_disk_usage",
            "description": "Get total, used, and free disk space for the project filesystem.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

tool_functions = {
    "list_project_files": list_project_files,
    "get_disk_usage": get_disk_usage,
}

messages = [{
    "role": "user",
    "content": "Use the available tools to show project files and disk usage. Summarize both results."
}]

response = requests.post(
    API_URL,
    json={"model": MODEL, "stream": False, "messages": messages, "tools": tools},
    timeout=180,
)
response.raise_for_status()
assistant_message = response.json()["message"]
messages.append(assistant_message)

tool_calls = assistant_message.get("tool_calls", [])
if not tool_calls:
    print("Model did not call a tool:", assistant_message.get("content", ""))
    raise SystemExit(0)

for call in tool_calls:
    name = call["function"]["name"]
    if name not in tool_functions:
        result = {"error": "Tool not allowed"}
    else:
        result = tool_functions[name]()
    print(f"\nTool: {name}\nResult: {result}")
    messages.append({"role": "tool", "content": json.dumps(result)})

response = requests.post(
    API_URL,
    json={"model": MODEL, "stream": False, "messages": messages},
    timeout=180,
)
response.raise_for_status()
print("\nAgent summary:")
print(response.json()["message"]["content"])
