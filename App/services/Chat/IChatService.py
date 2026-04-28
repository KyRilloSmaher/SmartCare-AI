from abc import ABC, abstractmethod
from typing import List

class IChatService(ABC):

    @abstractmethod
    def ask( self, ingredients: List[str] = None, question: str = None,audio_file=None) -> str:
        pass