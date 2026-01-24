from App.ML.models.BaseEmbeddingModel import BaseEmbeddingModel
# from App.ML.models.embedding_model  import OpenAIEmbeddingModel
from App.ML.models.embedding_model  import HuggingFaceEmbeddingService


def get_embedding_model() -> BaseEmbeddingModel:
    """
    Central place to choose embedding provider
    """
    #return OpenAIEmbeddingModel()
    return HuggingFaceEmbeddingService()
