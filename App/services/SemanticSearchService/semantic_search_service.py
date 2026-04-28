from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from App.services.EmbeddingService.embedding_service import EmbeddingService
from App.repositories.vector.repository_factory import get_repo
from App.ML.preprocessing.text_cleaner import Cleaner
from App.ML.preprocessing.language_detector import LanguageDetector
from App.observability.logger import get_logger
from App.services.SemanticSearchService.ISemanticSearchService import ISemanticSearchService

logger = get_logger(__name__)


class SemanticSearchService(ISemanticSearchService):
    def init(self):
        self.embedding_service = EmbeddingService()
        self.vector_repo = get_repo()
        self.cleaner = Cleaner()
        self.lang_detector = LanguageDetector()
        self.medical_reference = (
            "medications drugs treatment diseases symptoms diagnosis pharmacy medicine dosage side effects"
        )

        
        ref_embedding = self.embedding_service.embed_texts(self.medical_reference)

        if ref_embedding is None or len(ref_embedding) == 0:
            logger.error("Failed to initialize medical reference embedding")
            self.ref_vector = None
        else:
            self.ref_vector = ref_embedding[0] if isinstance(ref_embedding, list) else ref_embedding[0].tolist()

        logger.info("SemanticSearchService initialized")

    def is_medical_query(self, query_vector) -> bool:
        if self.ref_vector is None:
            return True 

        similarity = cosine_similarity([query_vector], [self.ref_vector])[0][0]

        logger.info(f"Medical similarity score: {similarity}")
        return similarity >= 0.60

    def search(
        self,
        query: str,
        top_k: int = 10,
        with_vectors: bool = False
    ) -> List[Dict[str, Any]]:

        if not query:
            logger.warning("Empty search query")
            return []

        #  Clean
        cleaned_query = self.cleaner.clean_text(query)

        #  Detect language
        lang = self.lang_detector.detect_language(cleaned_query)
        logger.info(f"Semantic search query detected language: {lang}")

        # Embed query
        query_embedding = self.embedding_service.embed_texts(cleaned_query)

        if query_embedding is None or len(query_embedding) == 0:
            logger.error("Failed to generate embedding")
            return []

        # normalize vector
        if isinstance(query_embedding, list):
            query_vector = query_embedding[0]
        else:
            query_vector = query_embedding[0].tolist()

        # Semantic validation (NEW)
        if not self.is_medical_query(query_vector):
            logger.warning("Rejected non-medical query")
            return [{
                "error": "❌ Search is only Allowed Fro Medical Purpose"
            }]

        #Search in vector DB
        results = self.vector_repo.search(
            query_vector=query_vector,
            top_k=top_k,
            with_vectors=with_vectors
        )

        return results