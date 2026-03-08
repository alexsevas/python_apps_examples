import requests
import json

class OllamaEngine:

    def __init__(self, model):
        self.model = model


    def stream(self, prompt):
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True
            },
            stream=True
        )
        for line in r.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if "response" in data:
                yield data["response"]