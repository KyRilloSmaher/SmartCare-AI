from App.observability.logger import get_logger
from App.services.semantic_search_service import SemanticSearchService
logger = get_logger(__name__)
class TestSemanticSearch:
    def test_search(self ,Query:str):
        logger.info("\n=================================================\n")
        logger.info(f"Testing semantic search with query: {Query}\n")
        logger.info("\n=================================================\n")
        search_service = SemanticSearchService()

        results = search_service.search(
            query=Query,
            top_k=5,
        )

        for r in results:
            logger.info(f"Found result: {r['id']}, score: {r['score']}\n")
        logger.info(f"Results count: {len(results)}\n")
        logger.info("=================================================\n")