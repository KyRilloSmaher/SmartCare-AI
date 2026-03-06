# App/ML/models/LocalEmbeddingModel.py

from typing import List, Union
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from App.ML.models.BaseEmbeddingModel import BaseEmbeddingModel
from App.observability.logger import get_logger

logger = get_logger(__name__)


def average_pool(last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """Mean pooling with attention mask applied."""
    masked = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return masked.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


class HuggingFaceEmbeddingService(BaseEmbeddingModel):
    """
    Fully local embedding service using intfloat/e5-small.
    Output dimension is dynamically read from model config.
    """

    def __init__(self, device: str = None):
        self.model_name = "intfloat/e5-small"
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        logger.info(f"Loading embedding model {self.model_name} on {self.device}...")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

        # 🔥 Dynamic dimension (NO HARDCODE)
        self._dim = self.model.config.hidden_size

        logger.info(
            f"{self.model_name} loaded successfully with embedding_dim={self._dim}"
        )

    @property
    def dim(self) -> int:
        return self._dim

    def embed(
        self,
        texts: Union[str, List[str]],
        prefix: str = "passage"  # must be "query" or "passage"
    ) -> np.ndarray:
        """
        Generate embeddings for text(s).
        E5 models REQUIRE prefix: 'query:' or 'passage:'
        """

        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, self._dim), dtype=np.float32)

        # ✅ Proper E5 formatting
        formatted_texts = [f"{prefix}: {t}" for t in texts]

        batch_dict = self.tokenizer(
            formatted_texts,
            max_length=512,
            padding=True,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**batch_dict)
            embeddings = average_pool(
                outputs.last_hidden_state,
                batch_dict["attention_mask"]
            )
            embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings.cpu().numpy().astype(np.float32)