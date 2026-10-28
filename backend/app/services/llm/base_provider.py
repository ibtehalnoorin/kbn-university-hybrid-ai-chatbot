from abc import ABC, abstractmethod
from typing import Generator, List, Dict, Any, Optional

class BaseLLMProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Checks if the LLM provider service is reachable."""
        pass

    @abstractmethod
    def check_model_availability(self, model_name: str) -> bool:
        """Checks if the specific model is downloaded and available."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """Returns list of installed model names."""
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
        timeout: int = 60
    ) -> str:
        """Generates a synchronous response."""
        pass

    @abstractmethod
    def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
        timeout: int = 60
    ) -> Generator[str, None, None]:
        """Generates a streamed response chunk by chunk."""
        pass
