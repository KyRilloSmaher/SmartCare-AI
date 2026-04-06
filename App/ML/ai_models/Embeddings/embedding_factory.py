from App.ML.ai_models.Embeddings import BaseEmbeddingModel
from App.ML.ai_models.Embeddings.embedding_model  import HuggingFaceEmbeddingService


def get_embedding_model() -> BaseEmbeddingModel:
    """
    Central place to choose embedding provider
    """
    #return OpenAIEmbeddingModel()
    return HuggingFaceEmbeddingService()
