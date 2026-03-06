# App/repositories/vector/qdrant_repo.py

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)
from App.repositories.vector.base import VectorRepository
from App.config.base import BaseConfig
from App.observability.logger import get_logger

logger = get_logger(__name__)


class QdrantRepository(VectorRepository):
    """
    Qdrant Cloud vector store implementation
    Fully dynamic vector size (model-agnostic)
    """

    VECTOR_NAME = "abstract-dense-vector"

    def __init__(self, vector_size: int):
        self.vector_size = vector_size
        self.collection = BaseConfig.QDRANT_COLLECTION

        url = BaseConfig.QDRANT_URL

        # Clean HTTPS URL if port is included
        if url.startswith("https://") and ":6333" in url:
            url = url.replace(":6333", "")
            logger.info("Removed port 6333 from HTTPS URL")

        self.client = QdrantClient(
            url=url,
            api_key=BaseConfig.QDRANT_API_KEY,
            timeout=60,
            prefer_grpc=False,  # Required for Cloud
        )

        logger.info(
            "Qdrant Cloud repository initialized",
            extra={
                "collection": self.collection,
                "vector_size": self.vector_size
            }
        )

    # ---------------------------------------------------
    # Initialization
    # ---------------------------------------------------

    def initialize(self) -> None:
        """Ensure collection exists with correct vector size"""
        try:
            try:
                info = self.client.get_collection(self.collection)

                # Extract vector size
                vectors_config = info.config.params.vectors

                if hasattr(vectors_config, "size"):
                    existing_size = vectors_config.size
                elif isinstance(vectors_config, dict):
                    existing_size = vectors_config[self.VECTOR_NAME].size
                else:
                    existing_size = None

                if existing_size != self.vector_size:
                    logger.warning(
                        f"Vector size mismatch. "
                        f"Existing={existing_size}, Expected={self.vector_size}"
                    )
                    logger.warning("Recreating collection with correct schema...")
                    self.client.delete_collection(self.collection)
                    self._create_collection()
                else:
                    logger.info("Collection already exists with correct schema")

            except Exception:
                logger.info("Collection not found. Creating new one...")
                self._create_collection()

        except Exception as e:
            logger.error("Failed to initialize Qdrant collection", exc_info=True)
            raise

    def _create_collection(self):
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config={
                self.VECTOR_NAME: VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            }
        )

        logger.info(
            f"Collection '{self.collection}' created "
            f"with vector size {self.vector_size}"
        )

    # ---------------------------------------------------
    # Add Vectors
    # ---------------------------------------------------

    def add(
        self,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:

        try:
            points = [
                PointStruct(
                    id=pid,
                    vector={self.VECTOR_NAME: vector},
                    payload=meta
                )
                for pid, vector, meta in zip(ids, vectors, metadata)
            ]

            self.client.upsert(
                collection_name=self.collection,
                points=points,
                wait=True
            )

            logger.info(f"Inserted {len(points)} vectors")
            return True

        except Exception as e:
            logger.error("Qdrant upsert failed", exc_info=True)
            raise

    # ---------------------------------------------------
    # Search
    # ---------------------------------------------------

    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        with_vectors: bool = False
    ) -> List[Dict[str, Any]]:

        try:
            results = self.client.query_points(
                collection_name=self.collection,
                query=query_vector, 
                using=self.VECTOR_NAME, 
                limit=top_k,
                with_vectors=with_vectors
            )

            hits = results.points if hasattr(results, "points") else results

            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "metadata": hit.payload,
                    "vector": (
                        hit.vector.get(self.VECTOR_NAME)
                        if with_vectors and isinstance(hit.vector, dict)
                        else None
                    )
                }
                for hit in hits
            ]

        except Exception:
            logger.error("Qdrant search failed", exc_info=True)
            raise

    # ---------------------------------------------------
    # Delete
    # ---------------------------------------------------

    def delete(self, ids: List[str]) -> bool:
        try:
            self.client.delete(
                collection_name=self.collection,
                points_selector={"ids": ids}
            )
            return True

        except Exception:
            logger.error("Qdrant delete failed", exc_info=True)
            raise

    # ---------------------------------------------------
    # Retrieve
    # ---------------------------------------------------

    def get_vector(self, point_id: str) -> Optional[List[float]]:

        try:
            result = self.client.retrieve(
                collection_name=self.collection,
                ids=[point_id],
                with_vectors=True
            )

            if not result:
                return None

            point = result[0]

            if isinstance(point.vector, dict):
                return point.vector.get(self.VECTOR_NAME)

            return point.vector

        except Exception:
            logger.error("Qdrant retrieve failed", exc_info=True)
            return None