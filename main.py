import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "qwen2.5:1.5b",
    "prompt": "Explain API calling in simple English in two sentences.",
    "stream": False
}

response = requests.post(url, json=payload, timeout=120)

print("Status code:", response.status_code)
response.raise_for_status()

data = response.json()
print("AI response:", data["response"])
