from typing import List, Dict, Any

import numpy as np

from App.services.EmbeddingService.embedding_service import EmbeddingService
from App.repositories.vector.repository_factory import get_repo
from App.ML.preprocessing.text_cleaner import Cleaner
from App.ML.preprocessing.language_detector import LanguageDetector
from App.ML.ai_models.LogisticRegression.intent_factory import get_intent_model
from App.observability.logger import get_logger
from App.services.SemanticSearchService.ISemanticSearchService import ISemanticSearchService

logger = get_logger(__name__)


class SemanticSearchService(ISemanticSearchService):

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_repo = get_repo()
        self.cleaner = Cleaner()
        self.lang_detector = LanguageDetector()

        # ML Intent Model 
        self.intent_model = get_intent_model()

        logger.info("SemanticSearchService initialized with ML intent model")

    # ---------------------------------------------------------
    #  ML-based intent classification (REPLACED OLD RULE SYSTEM)
    # ---------------------------------------------------------
    def is_medical_query(self, query: str) -> bool:
        """
        Uses trained ML model instead of cosine similarity heuristic
        """
        try:
            vec = self.embedding_service.embed_texts(query)

            if vec is None or len(vec) == 0:
                return False

            if isinstance(vec, list):
                vec = vec[0]

            vec = np.array(vec)

            pred = self.intent_model.predict(vec)

            logger.info(f"Intent prediction result: {pred}")

            return pred == 1

        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            return False

    # ---------------------------------------------------------
    #  Similarity helper
    # ---------------------------------------------------------
    def _similarity(self, v1, v2):
        return self.vector_repo.similarity(v1, v2)

    # ---------------------------------------------------------
    # MAIN SEARCH PIPELINE
    # ---------------------------------------------------------
    def search(
        self,
        query: str,
        top_k: int = 10,
        with_vectors: bool = False
    ) -> List[Dict[str, Any]]:

        if not query:
            logger.warning("Empty search query received")
            return []

        # Clean input
        cleaned_query = self.cleaner.clean_text(query)

        # Detect language
        lang = self.lang_detector.detect_language(cleaned_query)
        logger.info(f"Detected language: {lang}")

        # Intent filtering 
        if not self.is_medical_query(cleaned_query):
            logger.warning("Rejected non-medical query by intent model")

            return {
                "success": False,
                "error": "Search is only allowed for medical purposes"
            }

        #Embed query (ONLY after validation)
        query_embedding = self.embedding_service.embed_texts(cleaned_query,'query')

        if query_embedding is None or len(query_embedding) == 0:
            logger.error("Failed to generate embedding")
            return []

        # normalize vector
        query_vector = (
            query_embedding[0]
            if isinstance(query_embedding, list)
            else query_embedding[0].tolist()
        )

        #Vector DB search
        results = self.vector_repo.search(
            query_vector=query_vector,
            top_k=top_k,
            with_vectors=with_vectors
        )

        return results