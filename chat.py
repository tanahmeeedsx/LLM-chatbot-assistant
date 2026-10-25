import requests

url = "http://localhost:11434/api/chat"

payload = {
    "model": "qwen2.5:1.5b",
    "stream": False,
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful DevOps tutor. Explain concepts in simple English."
        },
        {
            "role": "user",
            "content": "What is Docker? Explain in two sentences."
        }
    ]
}

response = requests.post(url, json=payload, timeout=120)
response.raise_for_status()

data = response.json()
print(data["message"]["content"])
