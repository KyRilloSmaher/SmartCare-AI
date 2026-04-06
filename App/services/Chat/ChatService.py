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
    def ask(self, ingredient: str, question: str = None, audio_file=None) -> str:
        try:
            logger.info("ChatService | Request started")

            #Handle audio if exists
            if audio_file:
                logger.info("ChatService | Transcribing audio...")
                transcript = self._transcribe(audio_file)
                logger.info(f"transcript | {transcript} ...")
                
                if question:
                    question = f"{question} {transcript}"
                else:
                    question = transcript
            else :
                logger.info(f"Aduio File is None")
                #Validation
                if not ingredient:
                    raise ValueError("Ingredient is required")

                if not question or not question.strip():
                    raise ValueError("Question is empty")

            #Build prompt
            prompt = self._build_prompt(ingredient, question)
            
            answer = ''
            # Call AI
            for _ in range(3):
                try:
                    answer = self._call_ai(prompt)
                except:
                    continue
            

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

    def _build_prompt(self, ingredient: str, question: str) -> str:
        return f"""
                You are a professional medical assistant.
                If User Question Is Not related By The Medicines or the drugs 
                Response By I Not Allowd TO Answer.
                
                Active ingredient: {ingredient}

                Answer in English.
                Provide GENERAL medical info only (no diagnosis).

                Include:
                - Uses
                - Side effects
                - Contraindications
                - Warnings
                - Drug interactions (if relevant)
                - What conditions it treats
                
                User Question Is : {question}
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

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error("AI request failed", exc_info=True)
            raise RuntimeError("AI service unavailable")
        