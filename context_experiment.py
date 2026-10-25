import time
import requests

URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b"

prompts = {
    "Short prompt": "Explain Docker in one sentence.",
    "Medium prompt": (
        "Explain Docker to a beginner DevOps engineer. "
        "Cover images, containers, Dockerfiles, and port mapping. "
        "Give a practical example."
    ),
    "Long prompt": (
        "You are teaching a beginner DevOps engineer. "
        "Explain Docker, images, containers, Dockerfiles, volumes, "
        "networks, port mapping, Docker Compose, and container security. "
        "For every concept, explain what it is, why it matters, and give "
        "a practical example. Use simple English and organize the answer "
        "with headings and numbered lists. "
    ) * 5,
}

for label, prompt in prompts.items():
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [{"role": "user", "content": prompt}],
    }

    start = time.perf_counter()
    response = requests.post(URL, json=payload, timeout=180)
    latency = time.perf_counter() - start
    response.raise_for_status()
    data = response.json()

    print(f"\n--- {label} ---")
    print(f"Prompt tokens: {data.get('prompt_eval_count', 0)}")
    print(f"Output tokens: {data.get('eval_count', 0)}")
    print(f"Latency: {latency:.2f} seconds")
    print("Response preview:", data["message"]["content"][:180])
