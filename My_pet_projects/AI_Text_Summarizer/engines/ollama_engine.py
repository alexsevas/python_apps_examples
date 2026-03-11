import requests
import json

class OllamaEngine:

    def __init__(self, model):
        self.model = model
        self.base_url = "http://localhost:11434"

    def stream(self, prompt):
        try:
            # Используем tuple (connect_timeout, read_timeout)
            # connect_timeout - время на установку соединения (5 сек)
            # read_timeout - время ожидания ответа (300 сек = 5 минут)
            r = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True,
                timeout=(5, 300)
            )
            r.raise_for_status()
            
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
                    
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama. Make sure Ollama is running on localhost:11434")
        except requests.exceptions.Timeout:
            raise Exception("Connection to Ollama timed out. The model might be loading or the request is too complex.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception(f"Model '{self.model}' not found. Please pull it first: ollama pull {self.model}")
            else:
                raise Exception(f"Ollama error: {e}")