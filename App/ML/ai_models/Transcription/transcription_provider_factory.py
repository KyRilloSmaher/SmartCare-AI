
import os
from App.ML.ai_models.Transcription.WhisperAPI import WhisperAPIService
from App.ML.ai_models.Transcription.WhisperLocalmodel import WhisperLocalService

def get_transcription_provider():
    provider = os.getenv("TRANSCRIPTION_PROVIDER", "api")

    if provider == "local":
        return WhisperLocalService()
    else:
        return WhisperAPIService()