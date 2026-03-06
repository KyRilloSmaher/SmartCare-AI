"""
Semantic-search endpoint  →  App/routes/semantic_search.py

Depends ONLY on ISemanticSearchService (the interface).
Never imports SemanticSearchService directly.
"""
from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from App.services.service_providers import ISemanticSearchService
from App.services.service_providers import get_semantic_search_service
from App.config.feature_flags import FeatureFlags
from App.observability.logger import get_logger
from App.utils.exceptions import ValidationError

logger = get_logger(__name__)
bp = Blueprint("semantic_search", __name__)


# ── Request / Response schemas ────────────────────────────────────────────────

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=10, ge=1, le=100)
    with_vectors: bool = Field(default=False, description="Include raw embeddings in results")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "pain relief for elderly patients",
                "top_k": 10,
                "with_vectors": False,
            }
        }


class SemanticSearchResultItem(BaseModel):
    id: str
    score: float
    # any extra metadata the vector store may return
    metadata: Optional[Dict[str, Any]] = None


class SemanticSearchResponse(BaseModel):
    query: str
    top_k: int
    results: List[SemanticSearchResultItem]
    total: int


# ── Endpoint ──────────────────────────────────────────────────────────────────

@bp.route("/semantic-search", methods=["POST"])
def semantic_search():
    """
    Search products using a natural-language query.

    Request body (JSON):
        query        str   required (1–500 chars)
        top_k        int   default 10 (1–100)
        with_vectors bool  default false

    Responses:
        200  SemanticSearchResponse
        400  Validation error
        503  Feature disabled
        500  Unexpected server error
    """
    logger.info("Semantic search requested")

    if not FeatureFlags.is_enabled("semantic_search"):
        logger.warning("Semantic search feature is disabled")
        return jsonify({
            "error": "Feature disabled",
            "message": "Semantic search is currently disabled",
        }), 503

    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")

        req = SemanticSearchRequest(**data)
        logger.info("SemanticSearch | query=%r top_k=%d", req.query, req.top_k)

        # Depend on the INTERFACE
        service: ISemanticSearchService = get_semantic_search_service()

        raw = service.search(
            query=req.query,
            top_k=req.top_k,
            with_vectors=req.with_vectors,
        )

        items = []
        for r in raw:
            items.append(SemanticSearchResultItem(
                id=r["id"],
                score=r["score"],
                metadata={k: v for k, v in r.items() if k not in ("id", "score")} or None,
            ))

        resp = SemanticSearchResponse(
            query=req.query,
            top_k=req.top_k,
            results=items,
            total=len(items),
        )
        return jsonify(resp.model_dump()), 200

    except PydanticValidationError as e:
        logger.warning("Pydantic validation: %s", e)
        raise ValidationError(f"Invalid request: {e.errors()}")
    except ValidationError as e:
        logger.warning("Validation error: %s", e.message)
        return jsonify({"error": "Validation Error", "message": e.message}), e.status_code
    except Exception as e:
        logger.error("Unexpected error in semantic search: %s", e, exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500