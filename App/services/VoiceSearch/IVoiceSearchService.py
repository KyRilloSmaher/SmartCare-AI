from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from werkzeug.datastructures import FileStorage



class IVoiceSearchService(ABC):

    @abstractmethod
    def search(
        self,
        audio_file: FileStorage,    
        lang: str = "en",
        top_k: int = 10,
        with_vectors: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Perform voice-based semantic search.

        Steps:
        1. Speech → Text
        2. Text → Embedding
        3. Vector → Qdrant search
        """
        pass