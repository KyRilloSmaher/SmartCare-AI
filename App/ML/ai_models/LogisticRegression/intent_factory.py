# App/ML/ai_models/LogisticRegression/intent_factory.py
from pathlib import Path
from App.ML.ai_models.LogisticRegression.intent_sklearn_model import SklearnIntentModel
from App.ML.ai_models.LogisticRegression.base import BaseIntentModel

def get_intent_model() -> BaseIntentModel:
    """
    Central switch for intent detection model
    """
    # Get the current file's directory
    current_dir = Path(__file__).parent
    
    # Build path to model (relative to this file)
    model_path = current_dir / "intent_model.pkl"
    
    #Verify model exists
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at: {model_path}")
    
    return SklearnIntentModel(str(model_path))