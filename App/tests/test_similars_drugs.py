from App.observability.logger import get_logger
from App.services.drug_similars_service import SimilarityService
logger = get_logger(__name__)
class TestSimilarDrugs:
    def test_find_similar_by_id(self , product_id:str):
        logger.info("=================================================\n")
        logger.info(f"Testing find_similar_by_id with product_id: {product_id}\n")
        logger.info("=================================================\n")
        similars_service = SimilarityService()
        results = similars_service.find_similar_by_id(product_id=product_id, top_k=5)
        for r in results:
            logger.info(f"Found similar drug: {r['id']}, score: {r['score']}\n")
        logger.info(f"Results count: {len(results)}\n")
        logger.info("=================================================\n")
