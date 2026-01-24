from typing import List
from App.observability.logger import get_logger

logger = get_logger(__name__)

class Chunker:
    """
    Splits long text into smaller chunks for embedding.
    Typically used to keep embeddings under 500 tokens per chunk.
    """

    def __init__(self, chunk_size: int = 250, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        if not text:
            return []
        logger.debug(f"Chunking text length: {len(text)}")
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += self.chunk_size - self.overlap
        logger.debug(f"Created {len(chunks)} chunks")
        return chunks
