import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "qwen2.5:1.5b",
    "prompt": "Explain HTTP 500 in one sentence.",
    "stream": False
}

try:
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    print(response.json()["response"])

except requests.exceptions.Timeout:
    print("Error: The request timed out.")

except requests.exceptions.ConnectionError:
    print("Error: Cannot connect to Ollama.")

except requests.exceptions.HTTPError as error:
    print("HTTP error:", error)

except requests.exceptions.RequestException as error:
    print("Request failed:", error)
