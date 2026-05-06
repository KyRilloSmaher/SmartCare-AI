import joblib
import numpy as np
from App.ML.ai_models.LogisticRegression.base import BaseIntentModel

class SklearnIntentModel(BaseIntentModel):

    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)

    def predict(self, vector: np.ndarray) -> int:
        vector = vector.reshape(1, -1)
        return int(self.model.predict(vector)[0])