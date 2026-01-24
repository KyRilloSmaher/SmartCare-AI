from datetime import datetime, timezone
from App.repositories.mssql.product_repo import ProductRepository
from App.repositories.mssql.sync_state_repo import VectorSyncStateRepository
from App.observability.logger import get_logger
from App.services.embedding_service import EmbeddingService
from App.repositories.vector.repository_factory import get_repo

logger = get_logger(__name__)

class SyncService:
    SYNC_NAME = "products"
    BATCH_SIZE = 10  # Can increase to 50+ if needed

    def __init__(self):
        self.product_repo = ProductRepository()
        self.sync_state_repo = VectorSyncStateRepository()
        self.embeddingService = EmbeddingService()
        self.vector_repo = get_repo()  # FAISS or Qdrant

    def sync_products(self) -> dict:
        logger.info("Starting product vector sync job")

        last_sync = self.sync_state_repo.get_last_sync(self.SYNC_NAME)
        logger.info(f"Last sync time: {last_sync}")

        products = self.product_repo.get_products_for_sync(last_sync)
        total_products = len(products)
        logger.info(f"Fetched {total_products} products for sync")

        stats = {"processed": 0, "upserted": 0, "deleted": 0, "skipped": 0}

        for i in range(0, total_products, self.BATCH_SIZE):
            batch = products[i:i+self.BATCH_SIZE]
            logger.info(f"Processing batch {i//self.BATCH_SIZE + 1} ({len(batch)} products)")

            texts, ids, metadatas = [], [], []

            for product in batch:
                stats["processed"] += 1
                product_id = str(product.ProductId)

                try:
                    # Delete if not available
                    if product.IsDeleted or not product.IsAvailable:
                        self.vector_repo.delete([product_id])
                        stats["deleted"] += 1
                        logger.info(f"Deleted vector for product {product_id}")
                        continue

                    # Build embedding text
                    text = self._build_embedding_text(product)
                    texts.append(text)
                    ids.append(product_id)

                    # Prepare metadata
                    metadatas.append({
                        "product_id": product_id,
                        "category_id": str(product.CategoryId),
                        "company_id": str(product.CompanyId),
                        "is_available": product.IsAvailable,
                        "dosage_form": product.DosageForm,
                        "price": float(product.Price),
                        "discount_pct": float(product.DiscountPercentage),
                        "rating_avg": float(product.AverageRating),
                        "rating_count": int(product.TotalRatings),
                        "updated_at": product.UpdatedAt.isoformat(),
                        "created_at": product.CreatedAt.isoformat(),
                        "vector_version": "v1",
                        "source": "mssql"
                    })

                except Exception as e:
                    stats["skipped"] += 1
                    logger.error(f"Failed to prepare product {product_id}: {e}", exc_info=True)

            if texts:
                try:
                    embeddings = self.embeddingService.embed_texts(texts)
                    self.vector_repo.add(vectors=embeddings, metadata=metadatas, ids=ids)
                    stats["upserted"] += len(embeddings)
                    logger.info(f"Upserted {len(embeddings)} vectors in batch {i//self.BATCH_SIZE + 1}")
                except Exception as e:
                    stats["skipped"] += len(texts)
                    logger.error(f"Failed to embed batch {[ids]}: {e}", exc_info=True)

        # Update last sync
        now = datetime.now(timezone.utc)
        try:
            self.sync_state_repo.update_last_sync(self.SYNC_NAME, now)
            logger.info(f"Updated last sync timestamp: {now.isoformat()}")
        except Exception as e:
            logger.error(f"Failed to update sync state: {e}", exc_info=True)

        logger.info(f"Product vector sync completed | Stats: {stats}")
        return stats

    @staticmethod
    def _build_embedding_text(product) -> str:
        parts = [
            product.NameEn,
            product.NameAr or "",
            f"Description: {product.Description}",
            f"Medical Description: {product.MedicalDescription}",
            f"Active Ingredients: {product.ActiveIngredients}",
            f"Side Effects: {product.SideEffects or ''}",
            f"Contraindications: {product.Contraindications or ''}",
            f"Tags: {product.Tags}",
            f"Dosage Form: {product.DosageForm or ''}"
        ]
        return " | ".join(parts)
