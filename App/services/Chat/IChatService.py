from abc import ABC, abstractmethod

class IChatService(ABC):

    @abstractmethod
    def ask(self, ingredient: str, question: str, audio_file=None) -> str:
        pass