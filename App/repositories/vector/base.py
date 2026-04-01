# app/repositories/vector/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
class VectorRepository(ABC):
    """Abstract interface for vector database operations"""

    @abstractmethod
    def add(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> bool:
        """Add a single vector to the store"""
        pass
    @abstractmethod
    def get_vector(self, product_id: str) -> Optional[List[float]]:
        """
        Retrieve the stored vector for a specific product ID
        """
        pass
    @abstractmethod
    def search(self, query_vector: List[float], top_k: int = 10 , with_vectors: bool = False) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> bool:
        """Delete vectors by IDs"""
        pass

    @classmethod
    @abstractmethod
    def initialize(cls) -> "VectorRepository":
        """Return initialized vector repository instance"""
        pass

    @classmethod
    @abstractmethod
    def get_product_text(self, product_id: str) -> str:
        """
        Retrieve product text from Qdrant payload
        """
        pass
    @classmethod
    def similarity(self, v1, v2):

        v1 = np.array(v1)
        v2 = np.array(v2)

        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0

        return float(np.dot(v1, v2) / (norm1 * norm2))