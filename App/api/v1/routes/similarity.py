"""
Similar-drug endpoint.
Depends ONLY on ISimilarityService — never on SimilarityService directly.
"""
from typing import List, Optional

from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from App.services.interfaces import ISimilarityService
from App.services.service_providers import get_similarity_service
from App.observability.logger import get_logger
from App.utils.exceptions import ValidationError

logger = get_logger(__name__)
bp_similarity = Blueprint("similarity", __name__)


class SimilarityRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=100)
    score_threshold: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    exclude_self: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_abc",
                "top_k": 5,
                "score_threshold": 0.75,
                "exclude_self": True,
            }
        }


class SimilarityResultItem(BaseModel):
    id: str
    score: float


class SimilarityResponse(BaseModel):
    product_id: str
    top_k: int
    score_threshold: Optional[float]
    results: List[SimilarityResultItem]
    total: int


@bp_similarity.route("/similarity/find", methods=["POST"])
def find_similar():
    """
    Find the most similar products to a given product ID.

    Request body (JSON):
        product_id      str    required
        top_k           int    default 10  (1–100)
        score_threshold float  optional, -1.0 … 1.0
        exclude_self    bool   default true

    Responses:
        200  SimilarityResponse
        400  Validation error
        500  Unexpected server error
    """
    logger.info("Similarity search requested")

    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")

        req = SimilarityRequest(**data)
        logger.info(
            "Similarity | product=%s top_k=%d threshold=%s",
            req.product_id, req.top_k, req.score_threshold,
        )

        service: ISimilarityService = get_similarity_service()

        raw = service.find_similar_by_id(
            product_id=req.product_id,
            top_k=req.top_k,
            score_threshold=req.score_threshold,
            exclude_self=req.exclude_self,
        )

        items = [SimilarityResultItem(**r) for r in raw]
        resp = SimilarityResponse(
            product_id=req.product_id,
            top_k=req.top_k,
            score_threshold=req.score_threshold,
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
        logger.error("Unexpected error in similarity: %s", e, exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

