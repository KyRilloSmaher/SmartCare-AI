# App/services/TranscriptionService/whisper_api.py
from App.ML.ai_models.Transcription.ITranscriptionModel import ITranscriptionModel
from werkzeug.datastructures import FileStorage
import openai
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not set in environment")
openai.api_key = OPENAI_API_KEY

class WhisperAPIService(ITranscriptionModel):
    """
    Transcribe audio using OpenAI Whisper API.
    """

    def transcribe(self, audio_file: FileStorage) -> str:
        """
        audio_file: FileStorage (from Flask request.files['file'])
        """
        # Use .stream to provide a file-like object to OpenAI SDK
        file_obj = audio_file.stream

        result = openai.audio.transcriptions.create(
            model="whisper-1",
            file=file_obj
        )
        return result.text