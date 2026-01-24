from App.config.base import BaseConfig
from App.repositories.vector.base import VectorRepository
from App.repositories.vector.faiss_repo import FAISSRepository
from App.observability.logger import get_logger
from App.repositories.vector.qdrant_repo import QdrantRepository

logger = get_logger(__name__)

def get_repo() -> VectorRepository :
    """
    Central place to choose Vector Repository 
    """
    vector_type = BaseConfig.VECTOR_DB_TYPE.lower()
    if vector_type == "faiss":
            repo = FAISSRepository()
            repo.initialize()
            logger.info("Using FAISS for vector search")
            return repo
    elif vector_type == "qdrant":
            repo = QdrantRepository()
            repo.initialize()
            logger.info("Using Qdrant for vector search")
            return repo
    else:
            raise ValueError(f"Unsupported vector DB type: {vector_type}")