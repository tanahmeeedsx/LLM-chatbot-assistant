import requests

url = "http://localhost:11434/api/chat"

messages = [
    {
        "role": "system",
        "content": "You are a helpful DevOps tutor. Answer briefly."
    },
    {
        "role": "user",
        "content": "What is Docker?"
    },
    {
        "role": "assistant",
        "content": "Docker packages applications and dependencies into containers."
    },
    {
        "role": "user",
        "content": "What does it package?"
    }
]

response = requests.post(
    url,
    json={
        "model": "qwen2.5:1.5b",
        "messages": messages,
        "stream": False
    },
    timeout=120
)

response.raise_for_status()
print(response.json()["message"]["content"])
