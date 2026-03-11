import subprocess
import requests
import json
from typing import List, Dict, Optional


class OllamaHelper:
    """Вспомогательный класс для работы с Ollama"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
    
    def is_running(self) -> bool:
        """Проверяет, запущена ли Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_ollama(self) -> bool:
        """Пытается запустить Ollama"""
        try:
            # Запускаем Ollama в фоновом режиме
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            # Ждем немного, чтобы сервер успел запуститься
            import time
            time.sleep(2)
            return self.is_running()
        except Exception as e:
            print(f"Failed to start Ollama: {e}")
            return False
    
    def get_local_models(self) -> List[str]:
        """Получает список локально установленных моделей"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return sorted(models)
        except:
            pass
        return []
    
    def get_cloud_models(self) -> List[Dict[str, str]]:
        """Получает список популярных облачных моделей Ollama"""
        # Список популярных моделей, доступных в Ollama Library
        popular_models = [
            {"name": "llama3.2:latest", "description": "Meta Llama 3.2 (latest)"},
            {"name": "llama3.1:latest", "description": "Meta Llama 3.1 (latest)"},
            {"name": "llama3.1:8b", "description": "Meta Llama 3.1 8B"},
            {"name": "llama3.1:70b", "description": "Meta Llama 3.1 70B"},
            {"name": "llama2:latest", "description": "Meta Llama 2 (latest)"},
            {"name": "mistral:latest", "description": "Mistral (latest)"},
            {"name": "mixtral:latest", "description": "Mixtral (latest)"},
            {"name": "phi3:latest", "description": "Microsoft Phi-3 (latest)"},
            {"name": "gemma2:latest", "description": "Google Gemma 2 (latest)"},
            {"name": "qwen2.5:latest", "description": "Qwen 2.5 (latest)"},
            {"name": "codellama:latest", "description": "Code Llama (latest)"},
            {"name": "deepseek-coder:latest", "description": "DeepSeek Coder (latest)"},
        ]
        return popular_models
    
    def pull_model(self, model_name: str, progress_callback=None) -> bool:
        """Скачивает модель из облака"""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name, "stream": True},
                stream=True,
                timeout=None
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if progress_callback:
                            progress_callback(data)
                        if data.get("status") == "success":
                            return True
                return True
        except Exception as e:
            print(f"Failed to pull model: {e}")
            return False
