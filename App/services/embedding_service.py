
from App.ML.models.embedding_factory import get_embedding_model
from typing import List
from App.observability.logger import get_logger

logger = get_logger(__name__)
class EmbeddingService:
    def __init__(self):
        self.model =get_embedding_model()
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        logger.debug(f"Embedding {len(texts)} texts")
        return self.model.embed(texts)

    def embed_text(self, text: str) -> List[float]:
        list =[text]
        return self.model.embed(list)
