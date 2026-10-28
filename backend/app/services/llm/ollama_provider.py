import json
import logging
import requests
from typing import Generator, List, Dict, Any
from app.services.llm.base_provider import BaseLLMProvider
from app.utils.errors import ServiceUnavailableError

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "qwen2.5:7b"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    def is_available(self) -> bool:
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return res.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if res.status_code == 200:
                data = res.json()
                return [m.get("name") for m in data.get("models", [])]
            return []
        except Exception as e:
            logger.warning(f"Error listing Ollama models: {e}")
            return []

    def check_model_availability(self, model_name: str) -> bool:
        models = self.list_models()
        if not models:
            return False
        # Match exact name or name without tag
        for m in models:
            if m == model_name or m.startswith(f"{model_name}:") or model_name.startswith(f"{m}:"):
                return True
        return False

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
        timeout: int = 60,
        model: str = None
    ) -> str:
        selected_model = model or self.default_model
        if not self.is_available():
            raise ServiceUnavailableError("Ollama service is currently not reachable at " + self.base_url)

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": selected_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            res = requests.post(url, json=payload, timeout=timeout)
            if res.status_code != 200:
                raise ServiceUnavailableError(f"Ollama generation failed (HTTP {res.status_code}): {res.text}")
            data = res.json()
            return data.get("message", {}).get("content", "")
        except requests.exceptions.Timeout:
            raise ServiceUnavailableError(f"Ollama request timed out after {timeout} seconds.")
        except requests.exceptions.RequestException as e:
            raise ServiceUnavailableError(f"Failed to communicate with Ollama: {str(e)}")

    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
        timeout: int = 60,
        model: str = None
    ) -> Generator[str, None, None]:
        selected_model = model or self.default_model
        if not self.is_available():
            raise ServiceUnavailableError("Ollama service is currently not reachable at " + self.base_url)

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": selected_model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            res = requests.post(url, json=payload, stream=True, timeout=timeout)
            if res.status_code != 200:
                raise ServiceUnavailableError(f"Ollama stream initiation failed (HTTP {res.status_code})")

            for line in res.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    data = json.loads(decoded)
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk
                    if data.get("done", False):
                        break
        except requests.exceptions.Timeout:
            raise ServiceUnavailableError("Ollama stream timed out.")
        except requests.exceptions.RequestException as e:
            raise ServiceUnavailableError(f"Ollama streaming connection error: {str(e)}")
