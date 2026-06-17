from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    def generate_review(self, prompt: str) -> str:
        pass
