
"""
Service interfaces (ABCs) for drug intelligence services.
All route files import ONLY from here — never from a concrete service module.
"""
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

