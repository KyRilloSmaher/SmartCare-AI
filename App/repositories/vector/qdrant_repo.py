# qdrant_repo.py
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, CreateCollection
from App.repositories.vector.base import VectorRepository
from App.config.base import BaseConfig
from App.observability.logger import get_logger

logger = get_logger(__name__)

class QdrantRepository(VectorRepository):
    """Qdrant Cloud vector store implementation with robust error handling"""

    VECTOR_NAME = "abstract-dense-vector"

    def __init__(self):
        # Qdrant Cloud URL (without port for HTTPS)
        url = BaseConfig.QDRANT_URL
        
        # Clean URL
        if url.startswith("https://") and ":6333" in url:
            url = url.replace(":6333", "")
            logger.info(f"Removed port 6333 from HTTPS URL")
        
        self.client = QdrantClient(
            url=url,
            api_key=BaseConfig.QDRANT_API_KEY,
            timeout=60,
            prefer_grpc=False,  # Use HTTP for Cloud
        )
        self.collection = BaseConfig.QDRANT_COLLECTION
        
        logger.info("Qdrant Cloud repository initialized", 
                   extra={"collection": self.collection})

    def initialize(self) -> None:
        """Ensure Qdrant collection exists with proper schema"""
        try:
            # Try to get collection info
            try:
                collection_info = self.client.get_collection(self.collection)
                logger.info(f"Qdrant collection already exists: {self.collection}")
                
                # Try to parse vector size from config
                try:
                    vectors_config = collection_info.config.params.vectors
                    if hasattr(vectors_config, 'size'):
                        vector_size = vectors_config.size
                    elif isinstance(vectors_config, dict) and self.VECTOR_NAME in vectors_config:
                        vector_size = vectors_config[self.VECTOR_NAME].size
                    else:
                        vector_size = 1536  # Default to our expected size
                    
                    logger.info(f"Collection vector size: {vector_size}")
                except:
                    logger.warning("Could not determine collection vector size")
                    
                return
                
            except Exception as e:
                if "not found" in str(e).lower():
                    logger.info(f"Collection not found, will create: {self.collection}")
                else:
                    # Collection exists but schema parsing failed
                    logger.warning(f"Collection exists but schema parsing failed: {e}")
                    logger.info("Assuming collection already exists and continuing...")
                    return
            
            # Create new collection with proper schema
            logger.info(f"Creating new Qdrant collection: {self.collection}")
            
            # Use CreateCollection for better compatibility
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config={
                    self.VECTOR_NAME: VectorParams(
                        size=1536,
                        distance=Distance.COSINE
                    )
                },
                # Optional: Add these for better compatibility
                optimizers_config=None,
                hnsw_config=None,
                quantization_config=None,
            )
            
            logger.info(f"Successfully created collection: {self.collection}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {str(e)}", exc_info=True)
            # Don't raise, just log - collection might already exist with different schema
            logger.info("Continuing despite initialization error...")

    def add(
        self,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """Upsert vectors into Qdrant Cloud"""
        try:
            # Prepare points with named vectors
            points = [
                PointStruct(
                    id=pid,
                    vector={self.VECTOR_NAME: embedding},
                    payload=meta
                )
                for pid, embedding, meta in zip(ids, vectors, metadata)
            ]

            # Upsert in batches
            batch_size = 50
            success_count = 0
            
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                try:
                    self.client.upsert(
                        collection_name=self.collection,
                        points=batch,
                        wait=True
                    )
                    success_count += len(batch)
                    logger.debug(f"Upserted batch {i//batch_size + 1}: {len(batch)} vectors")
                except Exception as batch_error:
                    logger.error(f"Batch {i//batch_size + 1} failed: {batch_error}")
                    # Try individual points
                    for point in batch:
                        try:
                            self.client.upsert(
                                collection_name=self.collection,
                                points=[point],
                                wait=False  # Don't wait for individual points
                            )
                            success_count += 1
                        except Exception as point_error:
                            logger.error(f"Failed to upsert point {point.id}: {point_error}")
            
            logger.info(f"Successfully added {success_count}/{len(points)} vectors to Qdrant Cloud")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Qdrant Cloud upsert failed: {str(e)}", exc_info=True)
            raise

    def delete(self, ids: List[str]) -> bool:
        """Delete vectors by IDs"""
        try:
            self.client.delete(
                collection_name=self.collection, 
                points_selector={"ids": ids}
            )
            return True
        except Exception as e:
            logger.error(f"Qdrant Cloud delete failed: {str(e)}", exc_info=True)
            raise


    def get_vector(self, product_id: str) -> Optional[List[float]]:
        """
        Retrieve the stored vector for a specific product ID
        """
        try:
            result = self.client.retrieve(
                collection_name=self.collection,
                ids=[product_id],
                with_vectors=True
            )

            if not result:
                logger.warning(f"No vector found for product ID: {product_id}")
                return None

            point = result[0]

            # Named vector support
            if isinstance(point.vector, dict):
                return point.vector.get(self.VECTOR_NAME)

            # Fallback (non-named vector)
            return point.vector

        except Exception as e:
            logger.error(
                f"Failed to retrieve vector for product ID {product_id}: {str(e)}",
                exc_info=True
            )
            return None

    def search(self,query_vector: List[float],top_k: int = 10,with_vectors: bool = False) -> List[Dict[str, Any]]:
        """Vector similarity search (named vector)"""
        try:
            results = self.client.search(
                collection_name=self.collection,
                query_vector=(self.VECTOR_NAME, query_vector),
                limit=top_k,
                with_vectors=with_vectors
            )

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
                for hit in results
            ]

        except Exception as e:
            logger.error(f"Qdrant search failed: {str(e)}", exc_info=True)
            raise
