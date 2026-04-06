
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class IContradictionService(ABC):

    @abstractmethod
    def find_all_contradictions(
        self,
        product_id: str,
        candidate_ids: List[str],
        contradiction_threshold: float = -0.25,
        exclude_self: bool = True,
    ) -> List[Dict[str, Any]]:
        """Return candidates that contradict product_id, sorted asc by score (most negative first)."""
        ...

