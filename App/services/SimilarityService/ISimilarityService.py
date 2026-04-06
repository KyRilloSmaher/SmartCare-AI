
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ISimilarityService(ABC):

    @abstractmethod
    def find_similar_by_id(
        self,
        product_id: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        exclude_self: bool = True,
    ) -> List[Dict[str, Any]]:
        """Return products most similar to product_id, sorted desc by score."""
        ...
