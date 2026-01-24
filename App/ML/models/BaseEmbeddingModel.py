from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np


class BaseEmbeddingModel(ABC):
    """
    Interface for all embedding models.
    Any embedding implementation MUST follow this contract.
    """

    @property
    @abstractmethod
    def dim(self) -> int:
        """Embedding vector dimension"""
        pass

    @abstractmethod

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Convert a list of texts into embedding vectors.

        Args:
            texts: List of cleaned text strings

        Returns:
            np.ndarray of shape (len(texts), dim)
        """
        pass

