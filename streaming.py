import requests
import json

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:1.5b",
        "prompt": "Explain Docker in five short sentences.",
        "stream": True
    },
    stream=True,
    timeout=120
)

response.raise_for_status()

for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk.get("response", ""), end="", flush=True)

print()
