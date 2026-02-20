from typing import List, Dict, Any, Optional
from App.services.embedding_service import EmbeddingService
from App.repositories.vector.repository_factory import get_repo
from App.ML.preprocessing.text_cleaner import Cleaner
from App.ML.preprocessing.language_detector import LanguageDetector
from App.observability.logger import get_logger

logger = get_logger(__name__)


class SemanticSearchService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_repo = get_repo()
        self.cleaner = Cleaner()
        self.lang_detector = LanguageDetector()

        logger.info("SemanticSearchService initialized")

    def search(
        self,
        query: str,
        top_k: int = 10,
        with_vectors: bool = False
    ) -> List[Dict[str, Any]]:

        if not query:
            logger.warning("Empty search query")
            return []

        # 1️⃣ Clean
        cleaned_query = self.cleaner.clean_text(query)

        # 2️⃣ Detect language (optional - for logging)
        lang = self.lang_detector.detect_language(cleaned_query)
        logger.info(f"Semantic search query detected language: {lang}")

        # 3️⃣ Embed
        query_vector = self.embedding_service.embed_texts(cleaned_query)

        if query_vector is None or len(query_vector) == 0:
             logger.error("Failed to generate embedding")
             return []

        # embed() غالبًا بيرجع 2D array
        if isinstance(query_vector, list):
            vector = query_vector[0]
        else:
            vector = query_vector[0].tolist()

        # 4️⃣ Search in vector DB
        results = self.vector_repo.search(
            query_vector=vector,
            top_k=top_k,
            with_vectors=with_vectors
        )

        return results
    

