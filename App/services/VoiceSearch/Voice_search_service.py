from typing import List, Dict, Any
from App.services.EmbeddingService.embedding_service import EmbeddingService
from App.ML.ai_models.Transcription.transcription_provider_factory import get_transcription_provider
from App.repositories.vector.repository_factory import get_repo
from App.ML.preprocessing.text_cleaner import Cleaner
from App.ML.preprocessing.language_detector import LanguageDetector
from App.observability.logger import get_logger
from App.services.VoiceSearch.IVoiceSearchService import IVoiceSearchService

logger = get_logger(__name__)


class VoiceSearchService(IVoiceSearchService):

    def __init__(self ,semantic_search_service ):
        self.transcription_service = get_transcription_provider()
        self.embedding_service = EmbeddingService()
        self.vector_repo = get_repo()
        self.cleaner = Cleaner()
        self.lang_detector = LanguageDetector()
        self.semantic_search_service = semantic_search_service
        logger.info("VoiceSearchService initialized")

    def search(
        self,
        audio_file,
        lang: str = "en",
        top_k: int = 10,
        with_vectors: bool = False
    ) -> List[Dict[str, Any]]:

        if not audio_file:
            logger.warning("Empty audio file received")
            return []

        try:
            # Speech → Text
            text = self.transcription_service.transcribe(audio_file)

            if not text:
                logger.error("Transcription returned empty text")
                return []

            logger.info(f"Transcribed text: {text[:100]}...")

            # Search

            results =self.semantic_search_service.search(
                        query=text,
                        top_k=top_k,
                        with_vectors=with_vectors,
                    )

            logger.info(f"Voice search returned {len(results)} results")

            return results

        except Exception as e:
            logger.exception(f"Voice search failed: {str(e)}")
            return []