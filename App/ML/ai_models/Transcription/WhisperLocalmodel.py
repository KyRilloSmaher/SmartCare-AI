
import os
import tempfile
import textwrap
from openai import OpenAI
from faster_whisper import WhisperModel
from App.ML.ai_models.Transcription.ITranscriptionModel import ITranscriptionModel

class WhisperLocalService(ITranscriptionModel):

    def __init__(self):
        self.model = WhisperModel("tiny", device="cpu", compute_type="float32")

    
    def transcribe(self,audio_file) -> str:
        """
        audio_file: streamlit UploadedFile from st.audio_input
        """
        if audio_file is None:
            return ""

        audio_bytes = audio_file.getvalue()

        suffix = ".wav"
        if getattr(audio_file, "name", None) and "." in audio_file.name:
            suffix = "." + audio_file.name.split(".")[-1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            segments, info = self.model.transcribe(
                tmp_path,
                language="en", 
                beam_size=5,
                vad_filter=True, 
            )
            text_parts = [seg.text.strip() for seg in segments if seg.text.strip()]
            return " ".join(text_parts).strip()
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass