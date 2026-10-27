import json
import shutil
import requests
from pathlib import Path

API_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"
PROJECT_DIR = Path.cwd().resolve()
MAX_ROUNDS = 5


def list_project_files():
    return sorted(
        item.name + ("/" if item.is_dir() else "")
        for item in PROJECT_DIR.iterdir()
        if item.name != ".venv"
    )


def get_disk_usage():
    usage = shutil.disk_usage(PROJECT_DIR)
    return {
        "total_gb": round(usage.total / 1024**3, 2),
        "used_gb": round((usage.total - usage.free) / 1024**3, 2),
        "free_gb": round(usage.free / 1024**3, 2),
    }


tool_functions = {
    "list_project_files": list_project_files,
    "get_disk_usage": get_disk_usage,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_project_files",
            "description": "List files and folders in the current project.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_disk_usage",
            "description": "Get total, used, and free disk space.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

messages = [{
    "role": "user",
    "content": (
        "Check the project files and disk usage. "
        "Use the tools and summarize the results."
    ),
}]

for round_number in range(1, MAX_ROUNDS + 1):
    response = requests.post(
        API_URL,
        json={
            "model": MODEL,
            "stream": False,
            "messages": messages,
            "tools": tools,
        },
        timeout=180,
    )
    response.raise_for_status()

    assistant_message = response.json()["message"]
    messages.append(assistant_message)

    tool_calls = assistant_message.get("tool_calls", [])

    if not tool_calls:
        print("\nFinal answer:")
        print(assistant_message.get("content", ""))
        break

    print(f"\nAgent round {round_number}: {len(tool_calls)} tool call(s)")

    for call in tool_calls:
        name = call["function"]["name"]

        if name not in tool_functions:
            result = {"error": f"Tool not allowed: {name}"}
        else:
            try:
                result = tool_functions[name]()
            except Exception as error:
                result = {"error": str(error)}

        print(f"Executed: {name}")
        print(f"Result: {result}")

        messages.append({
            "role": "tool",
            "content": json.dumps(result),
        })
else:
    print(f"\nStopped: reached the {MAX_ROUNDS}-round limit.")
