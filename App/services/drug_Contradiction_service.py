# App/services/contradiction_service.py
from typing import List, Dict, Any
from App.repositories.vector.repository_factory import get_repo
from App.observability.logger import get_logger

logger = get_logger(__name__)

class ContradictionService:
    """
    Service to handle product contradiction checks based on vector similarity.
    Returns all contradicting products sorted by most negative (highest contradiction).
    """

    def __init__(self):
        self.vector_repo = get_repo()
        logger.info("ContradictionService initialized")

    # ===========================
    # Find all contradictions
    # ===========================
    def find_all_contradictions(
        self,
        product_id: str,
        candidate_ids: List[str],
        contradiction_threshold: float = -0.25,
        exclude_self: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Check all candidates and return a list of products that contradict the given product.

        Args:
            product_id (str): ID of the product to check.
            candidate_ids (List[str]): List of candidate product IDs to compare against.
            contradiction_threshold (float): Score below which products are considered contradictory.
            exclude_self (bool): Whether to ignore the product itself if present in candidate_ids.

        Returns:
            List[Dict[str, Any]]: List of dicts with 'id' and 'score', sorted by most negative score.
        """

        query_vector = self.vector_repo.get_vector(product_id)
        if not query_vector:
            logger.warning(f"No vector found for product {product_id}")
            return []

        contradictions = []

        for cid in candidate_ids:

            if exclude_self and cid == product_id:
                continue

            candidate_vector = self.vector_repo.get_vector(cid)
            if not candidate_vector:
                continue

            score = self.vector_repo.similarity(query_vector, candidate_vector)

            if score <= contradiction_threshold:
                contradictions.append({
                    "id": cid,
                    "score": score
                })
                logger.info(
                    f"Product {product_id} contradicts with {cid} (score={score})"
                )

        # Sort from most negative (strongest contradiction) to least
        contradictions.sort(key=lambda x: x["score"])

        return contradictions