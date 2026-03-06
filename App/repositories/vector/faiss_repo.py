from typing import List, Dict, Any, Optional
import os
import pickle
import faiss
import numpy as np

from App.repositories.vector.base import VectorRepository
from App.config.base import BaseConfig
from App.observability.logger import get_logger

logger = get_logger(__name__)


class FAISSRepository(VectorRepository):
    """FAISS vector store with Qdrant-like behavior"""

    def __init__(self, vectorSize:int):
        self.index_dir = BaseConfig.FAISS_INDEX_PATH
        self.index_file = os.path.join(self.index_dir, "index.faiss")
        self.meta_file = os.path.join(self.index_dir, "meta.pkl")
        self.vec_file = os.path.join(self.index_dir, "vectors.pkl")

        self.dim = vectorSize  # must match embedding model

        self.index: Optional[faiss.IndexIDMap] = None
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.vectors: Dict[str, List[float]] = {}  # raw vectors

        os.makedirs(self.index_dir, exist_ok=True)
        logger.info("FAISS repository initialized")

    # --------------------------------------------------
    # Initialization
    # --------------------------------------------------
    def initialize(self) -> None:
        if os.path.exists(self.index_file):
            logger.info("Loading existing FAISS index")
            self.index = faiss.read_index(self.index_file)

            if os.path.exists(self.meta_file):
                with open(self.meta_file, "rb") as f:
                    self.metadata = pickle.load(f)

            if os.path.exists(self.vec_file):
                with open(self.vec_file, "rb") as f:
                    self.vectors = pickle.load(f)
        else:
            logger.info("Creating new FAISS index")
            base = faiss.IndexFlatIP(self.dim)
            self.index = faiss.IndexIDMap(base)
            self._persist()

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------
    def _to_faiss_id(self, string_id: str) -> int:
        """Stable string → int64 mapping"""
        return int(string_id.replace("-", ""), 16) % (2**63 - 1)

    def _persist(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, "wb") as f:
            pickle.dump(self.metadata, f)
        with open(self.vec_file, "wb") as f:
            pickle.dump(self.vectors, f)

    # --------------------------------------------------
    # Add / Upsert
    # --------------------------------------------------
    def add(
        self,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: List[str],
    ) -> bool:
        if not vectors:
            return False

        if len(vectors) != len(ids):
            raise ValueError("Vectors and IDs length mismatch")

        arr = np.array(vectors, dtype="float32")

        if arr.ndim != 2 or arr.shape[1] != self.dim:
            raise ValueError(f"Expected shape (n, {self.dim}), got {arr.shape}")

        # Normalize for cosine similarity
        faiss.normalize_L2(arr)

        faiss_ids = np.array(
            [self._to_faiss_id(pid) for pid in ids],
            dtype="int64",
        )

        self.index.add_with_ids(arr, faiss_ids)

        for pid, fid, meta, vec in zip(ids, faiss_ids, metadata, vectors):
            meta = meta.copy()
            meta["product_id"] = pid
            meta["_faiss_id"] = int(fid)

            self.metadata[str(fid)] = meta
            self.vectors[str(fid)] = vec  # store raw vector

        self._persist()
        logger.info(f"Added {len(ids)} vectors to FAISS index")
        return True

    # --------------------------------------------------
    # Search
    # --------------------------------------------------
    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        with_vectors: bool = False,
    ) -> List[Dict[str, Any]]:

        query = np.array([query_vector], dtype="float32")
        faiss.normalize_L2(query)

        scores, ids = self.index.search(query, top_k)

        results = []
        for score, fid in zip(scores[0], ids[0]):
            if fid == -1:
                continue

            meta = self.metadata.get(str(fid))
            if not meta:
                continue

            result = {
                "id": meta.get("product_id"),
                "score": float(score),
                "metadata": meta,
            }

            if with_vectors:
                result["vector"] = self.vectors.get(str(fid))

            results.append(result)

        return results

    # --------------------------------------------------
    # Get vector (Qdrant parity)
    # --------------------------------------------------
    def get_vector(self, product_id: str) -> Optional[List[float]]:
        fid = self._to_faiss_id(product_id)
        vector = self.vectors.get(str(fid))

        if vector is None:
            logger.warning(f"No vector found for product ID: {product_id}")
            return None

        return vector

    # --------------------------------------------------
    # Delete
    # --------------------------------------------------
    def delete(self, ids: List[str]) -> bool:
        faiss_ids = np.array(
            [self._to_faiss_id(pid) for pid in ids],
            dtype="int64",
        )

        for fid in faiss_ids:
            self.metadata.pop(str(fid), None)
            self.vectors.pop(str(fid), None)

        self.index.remove_ids(faiss_ids)
        self._persist()
        return True
