import json
from pathlib import Path
import requests

API_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"
PROJECT_DIR = Path.cwd().resolve()

def list_project_files():
    """List files and folders in the current project directory."""
    return sorted(
        item.name + ("/" if item.is_dir() else "")
        for item in PROJECT_DIR.iterdir()
        if item.name != ".venv"
    )

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_project_files",
            "description": "List files and folders in the current project directory.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]

messages = [
    {
        "role": "user",
        "content": "Show me the files in this project. Use the list_project_files tool.",
    }
]

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
print("Model response:", assistant_message)

tool_calls = assistant_message.get("tool_calls", [])

if not tool_calls:
    print("\nThe model did not call a tool. Try running it again.")
    raise SystemExit(0)

messages.append(assistant_message)

for call in tool_calls:
    name = call["function"]["name"]

    if name == "list_project_files":
        result = list_project_files()
    else:
        result = {"error": "Tool not allowed"}

    print(f"\nTool executed: {name}")
    print("Tool result:", result)

    messages.append({
        "role": "tool",
        "content": json.dumps(result),
    })

follow_up = requests.post(
    API_URL,
    json={
        "model": MODEL,
        "stream": False,
        "messages": messages,
    },
    timeout=180,
)
follow_up.raise_for_status()

print("\nFinal answer:")
print(follow_up.json()["message"]["content"])
