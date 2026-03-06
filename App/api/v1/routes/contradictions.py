"""
Drug-drug contradiction endpoint.
Depends ONLY on IContradictionService — never on ContradictionService directly.
"""
from typing import List

from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from App.services.interfaces import IContradictionService
from App.services import get_contradiction_service
from App.config.feature_flags import FeatureFlags
from App.observability.logger import get_logger
from App.utils.exceptions import ValidationError

logger = get_logger(__name__)
bp_contradictions = Blueprint("contradictions", __name__)


class ContradictionRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    candidate_ids: List[str] = Field(..., min_items=1, max_items=200)
    contradiction_threshold: float = Field(default=-0.25, ge=-1.0, le=0.0)
    exclude_self: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "prod_warfarin",
                "candidate_ids": ["prod_aspirin", "prod_ibuprofen", "prod_paracetamol"],
                "contradiction_threshold": -0.25,
                "exclude_self": True,
            }
        }


class ContradictionResultItem(BaseModel):
    id: str
    score: float


class ContradictionResponse(BaseModel):
    product_id: str
    candidates_checked: int
    contradiction_threshold: float
    contradictions: List[ContradictionResultItem]
    total: int


@bp_contradictions.route("/contradictions/check", methods=["POST"])
def check_contradictions():
    """
    Find all products that contradict a reference product.

    Results are sorted from strongest contradiction (most negative score) first.

    Request body (JSON):
        product_id               str         required
        candidate_ids            List[str]   required (1-200 items)
        contradiction_threshold  float       default -0.25  (-1.0 … 0.0)
        exclude_self             bool        default true

    Responses:
        200  ContradictionResponse
        400  Validation error
        503  Feature disabled
        500  Unexpected server error
    """
    logger.info("Contradiction check requested")

    if not FeatureFlags.is_enabled("contradictions"):
        logger.warning("Contradictions feature is disabled")
        return jsonify({
            "error": "Feature disabled",
            "message": "Contradiction checking is currently disabled",
        }), 503

    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")

        req = ContradictionRequest(**data)
        logger.info(
            "Contradictions | product=%s candidates=%d threshold=%s",
            req.product_id, len(req.candidate_ids), req.contradiction_threshold,
        )

        service: IContradictionService = get_contradiction_service()

        raw = service.find_all_contradictions(
            product_id=req.product_id,
            candidate_ids=req.candidate_ids,
            contradiction_threshold=req.contradiction_threshold,
            exclude_self=req.exclude_self,
        )

        items = [ContradictionResultItem(**r) for r in raw]
        resp = ContradictionResponse(
            product_id=req.product_id,
            candidates_checked=len(req.candidate_ids),
            contradiction_threshold=req.contradiction_threshold,
            contradictions=items,
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
        logger.error("Unexpected error in contradiction check: %s", e, exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500