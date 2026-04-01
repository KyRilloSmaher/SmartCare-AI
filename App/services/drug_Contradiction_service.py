# App/services/contradiction_service.py

from typing import List, Dict, Any
from App.repositories.vector.repository_factory import get_repo
from App.observability.logger import get_logger

logger = get_logger(__name__)


class ContradictionService:

    def __init__(self):
        self.vector_repo = get_repo()
        logger.info("ContradictionService initialized")

    def _similarity(self, v1, v2):
        return self.vector_repo.similarity(v1, v2)

    def _is_opposite_effect(self, text1: str, text2: str) -> bool:

        text1 = text1.lower()
        text2 = text2.lower()

        opposite_pairs = [
            ("increase", "decrease"),
            ("activate", "block"),
            ("stimulate", "inhibit"),
            ("raise", "lower"),
            ("agonist", "antagonist"),
            ("bronchodilation", "bronchoconstriction"),
            ("vasodilation", "vasoconstriction"),
            ("sedative", "stimulant")
        ]

        for a, b in opposite_pairs:
            if (a in text1 and b in text2) or (b in text1 and a in text2):
                return True

        return False

    def find_all_contradictions(
        self,
        product_id: str,
        candidate_ids: List[str],
        similarity_threshold: float = 0.65,
        exclude_self: bool = True
    ) -> List[Dict[str, Any]]:

        query_vector = self.vector_repo.get_vector(product_id)

        if not query_vector:
            logger.warning(f"No vector found for product {product_id}")
            return []

        query_text = self.vector_repo.get_product_text(product_id)

        contradictions = []

        for cid in candidate_ids:

            if exclude_self and cid == product_id:
                continue

            candidate_vector = self.vector_repo.get_vector(cid)

            if not candidate_vector:
                continue
            similarity = self._similarity(query_vector, candidate_vector)
            if similarity < similarity_threshold:
                continue

            candidate_text = self.vector_repo.get_product_text(cid)

            if self._is_opposite_effect(query_text, candidate_text):

                score = -similarity

                contradictions.append({
                    "id": cid,
                    "score": score
                })

                logger.info(
                    f"Contradiction detected between {product_id} and {cid} (score={score})"
                )

        contradictions.sort(key=lambda x: x["score"])

        return contradictions