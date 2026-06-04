import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:3b",
        "prompt": "Say hello in one sentence.",
        "stream": False
    }
)

print(response.json()["response"])