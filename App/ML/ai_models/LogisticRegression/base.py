from abc import ABC, abstractmethod
import numpy as np

class BaseIntentModel(ABC):

    @abstractmethod
    def predict(self, vector: np.ndarray) -> int:
        pass