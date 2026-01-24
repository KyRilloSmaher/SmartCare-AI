# App/services/similarity_service.py
from typing import List, Dict, Any, Optional
from App.services.embedding_service import EmbeddingService
from App.repositories.vector.repository_factory import get_repo
from App.observability.logger import get_logger
import numpy as np

logger = get_logger(__name__)

class SimilarityService:
    def __init__(self):
        self.vector_repo = get_repo()
        logger.info("SimilarityService initialized")

    def find_similar_by_id(
        self,
        product_id: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        exclude_self: bool = True
    ) -> List[Dict[str, Any]]:

        # 1️⃣ Get exact stored vector
        query_vector = self.vector_repo.get_vector(product_id)
        if not query_vector:
            logger.warning(f"No vector found for product {product_id}")
            return []

        # 2️⃣ Search neighbors
        results = self.vector_repo.search(
            query_vector=query_vector,
            top_k=top_k + (1 if exclude_self else 0)
        )

        # 3️⃣ Filter
        filtered = []
        for r in results:
            if exclude_self and r["id"] == product_id:
                continue
            if score_threshold is not None and r["score"] < score_threshold:
                continue
            filtered.append(r)
            if len(filtered) >= top_k:
                break

        return filtered

    
