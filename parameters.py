import time
import requests

URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"

prompt = (
    "Suggest 3 creative names for a fictional DevOps monitoring tool. "
    "Return only the 3 names."
)

experiments = [
    {"temperature": 0.0, "top_p": 0.9},
    {"temperature": 0.7, "top_p": 0.9},
    {"temperature": 0.7, "top_p": 0.5},
    {"temperature": 0.7, "top_p": 1.0},
]

for params in experiments:
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [{"role": "user", "content": prompt}],
        "options": params,
    }

    start = time.perf_counter()
    response = requests.post(URL, json=payload, timeout=180)
    latency = time.perf_counter() - start
    response.raise_for_status()
    data = response.json()

    prompt_tokens = data.get("prompt_eval_count", 0)
    output_tokens = data.get("eval_count", 0)
    eval_duration = data.get("eval_duration", 0)
    tokens_per_second = (
        output_tokens / (eval_duration / 1_000_000_000)
        if eval_duration else 0
    )

    print("\n" + "=" * 45)
    print(f"Temperature: {params['temperature']}, Top-P: {params['top_p']}")
    print("Output:", data["message"]["content"])
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Total tokens: {prompt_tokens + output_tokens}")
    print(f"Response latency: {latency:.2f} seconds")
    print(f"Generation speed: {tokens_per_second:.2f} tokens/sec")
