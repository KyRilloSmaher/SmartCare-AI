from App.ML.ai_models.LogisticRegression.intent_sklearn_model import SklearnIntentModel
from App.ML.ai_models.LogisticRegression.base import BaseIntentModel

def get_intent_model() -> BaseIntentModel:
    """
    Central switch for intent detection model
    """

    return SklearnIntentModel("App/ML/ai_models/LogisticRegression/intent_model.pkl")