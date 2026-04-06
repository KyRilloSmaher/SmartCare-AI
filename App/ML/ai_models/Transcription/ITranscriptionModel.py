# transcription_interface.py
from abc import ABC, abstractmethod

class ITranscriptionModel(ABC):

    @abstractmethod
    def transcribe(self, audio_file) -> str:
        pass