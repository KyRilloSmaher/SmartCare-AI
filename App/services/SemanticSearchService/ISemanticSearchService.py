from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class ISemanticSearchService(ABC):

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 10,
        with_vectors: bool = False,
    ) -> List[Dict[str, Any]]:
        """Return products whose embeddings best match query, sorted desc by score."""
        ...
