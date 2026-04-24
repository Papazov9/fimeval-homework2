from abc import ABC, abstractmethod
from typing import Any


class BasePredictor(ABC):
    @abstractmethod
    def predict(self, image: Any, language: str) -> str:
        ...
