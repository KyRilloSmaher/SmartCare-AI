from typing import List

from openai import OpenAI
from App.ML.ai_models.Transcription.transcription_provider_factory import get_transcription_provider
from App.config import get_config
from App.observability.logger import get_logger
from App.services.Chat.IChatService import IChatService

logger = get_logger(__name__)


class ChatService(IChatService):

    def __init__(self):
        self.transcription_service = get_transcription_provider()
        self.BaseConfig = get_config()
        self.client = OpenAI(
            base_url= self.BaseConfig.OPENROUTER_BASE_URL,
            api_key= self.BaseConfig.OPENROUTER_API_KEY
        )

    # -------------------------
    # Public Method
    # -------------------------
    def ask(self, ingredients: List[str] = None, question: str = None, audio_file=None) -> str:
        try:
            logger.info("ChatService | Request started")

            ingredients = ingredients or []
            question = (question or "").strip()

            # ── Handle Audio ─────────────────────
            if audio_file:
                logger.info("ChatService | Transcribing audio...")
                transcript = self._transcribe(audio_file)

                if not transcript:
                    raise ValueError("Transcription returned empty text")
            question = f"{question} {transcript}".strip() if question else transcript

            # ── Validation (Aligned with API) ────
            if not question and not ingredients:
                raise ValueError("Either question or ingredients must be provided")

            # ── Build Prompt ─────────────────────
            prompt = self._build_prompt(ingredients, question)

            # ── Retry AI Call ────────────────────
            answer = ""
            last_exception = None

            for attempt in range(3):
                try:
                    answer = self._call_ai(prompt)
                    if answer:
                        break
                except Exception as e:
                    last_exception = e
                    logger.warning(f"AI attempt {attempt+1} failed: {str(e)}")

            if not answer:
                raise RuntimeError("AI failed after retries") from last_exception

            logger.info("ChatService | Success")
            return answer

        except Exception as e:
            logger.error(f"ChatService | Error: {str(e)}", exc_info=True)
            raise
    # -------------------------
    # Private Methods
    # -------------------------

    def _transcribe(self, audio_file) -> str:
        try:
            text = self.transcription_service.transcribe(audio_file)
            return text.strip()
        except Exception as e:
            logger.error("Transcription failed", exc_info=True)
            raise RuntimeError("Audio transcription failed")

    def _build_prompt(self, ingredients: List[str], question: str) -> str:
        ingredient_text = ", ".join(ingredients) if ingredients else "Not provided"

        return f"""
            You are a professional medical assistant.

            If the user question is NOT related to medicines or drugs,
            respond with: "I am not allowed to answer this."

            Active ingredients: {ingredient_text}

            Answer in English.
            Provide GENERAL medical info only (no diagnosis).

            Include:
            - Uses
            - Side effects
            - Contraindications
            - Warnings
            - Drug interactions (if relevant)
            - What conditions it treats

            User Question: {question if question else "Not provided"}
            """

    def _call_ai(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-5.1-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.4
            )

            content = response.choices[0].message.content
            if not content:
                raise RuntimeError("Empty response from AI")

            return content.strip()

        except Exception as e:
            logger.error("AI request failed", exc_info=True)
            raise RuntimeError("AI service unavailable")
        
