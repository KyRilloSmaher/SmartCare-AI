
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
    """Average pooling with attention mask applied (ignores padding tokens)."""
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

class HuggingFaceEmbeddingService(BaseEmbeddingModel):
    """
    Fully local embedding service using a small Hugging Face model.
    Outputs 1536-dimensional vectors.
    """
    def __init__(self, device: str = None):
        # Use a lightweight model
        self.model_name = "intfloat/e5-small"  # or "intfloat/multilingual-e5-small" for multi-language
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        logger.info(f"Loading local model {self.model_name} on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()

        # Force embedding dimension to 1536
        self._dim = 1536
        logger.info(f"{self.model_name} loaded successfully with embedding dim={self._dim}")

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Embed a single text or a list of texts."""
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, self._dim), dtype=np.float32)

        # Optional prefix for semantic search
        prefixed_texts = [
            f"query: {t}" if i < len(texts)//2 else f"passage: {t}"
            for i, t in enumerate(texts)
        ]

        # Tokenize
        batch_dict = self.tokenizer(
            prefixed_texts,
            max_length=512,
            padding=True,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        # Forward pass
        with torch.no_grad():
            outputs = self.model(**batch_dict)
            embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
            embeddings = F.normalize(embeddings, p=2, dim=1)

        # Convert to numpy
        emb_np = embeddings.cpu().numpy()

        # Ensure 2D array
        if emb_np.ndim == 1:
            emb_np = emb_np.reshape(1, -1)

        # Resize to 1536 if needed
        if emb_np.shape[1] != self._dim:
            pad_width = self._dim - emb_np.shape[1]
            emb_np = np.pad(emb_np, ((0, 0), (0, pad_width)), mode="constant")

        return emb_np

