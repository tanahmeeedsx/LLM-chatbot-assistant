import requests

url = "http://localhost:11434/api/chat"

messages = [
    {
        "role": "system",
        "content": (
            "Classify DevOps incidents using the examples. "
            "Return only: SEVERITY - ACTION"
        )
    },
    {
        "role": "user",
        "content": "Incident: CPU usage is 95% for 10 minutes."
    },
    {
        "role": "assistant",
        "content": "HIGH - Investigate processes and CPU usage"
    },
    {
        "role": "user",
        "content": "Incident: Disk usage is 40%."
    },
    {
        "role": "assistant",
        "content": "LOW - Continue monitoring disk usage"
    },
    {
        "role": "user",
        "content": "Incident: Application is returning HTTP 500 errors."
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
