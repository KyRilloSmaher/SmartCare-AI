from typing import Any, Dict, List
from flask import Blueprint, jsonify, request
from werkzeug.datastructures import FileStorage
from pydantic import BaseModel
from App.services.DrugNameExtraction.IDrugNameExtractionService import IDrugNameExtractionService
from App.services.service_providers import get_drug_name_extraction_service
from App.config.feature_flags import FeatureFlags
from App.observability.logger import get_logger
from App.utils.exceptions import ValidationError

logger = get_logger(__name__)
bp = Blueprint("drug_extraction", __name__)

# ── Request / Response schemas ────────────────────────────────────────────────

class DetectionItem(BaseModel):
    bbox: List[int]
    confidence: float


class DrugExtractionResponse(BaseModel):
    detections: List[DetectionItem]
    active_ingredients: List[str]

# ── Endpoint ──────────────────────────────────────────────────────────────────

@bp.route("/extract-drug", methods=["POST"])
def extract_drug():
    """
    Drug extraction endpoint.

    Accepts multipart/form-data:
        - file: image file
    """

    logger.info("Drug extraction requested")

    if not FeatureFlags.is_enabled("drug_extraction"):
        logger.warning("Drug extraction feature is disabled")
        return jsonify({
            "error": "Feature disabled",
            "message": "Drug extraction is currently disabled",
        }), 503

    try:
        #Get image file
        image_file: FileStorage = request.files.get("file")

        if not image_file:
            raise ValidationError("Image file ('file') is required")

        logger.info("DrugExtraction | filename=%s", image_file.filename)

        service: IDrugNameExtractionService = get_drug_name_extraction_service()

        result: Dict[str, Any] = service.extract(image_file)

        detections = [
            DetectionItem(**d) for d in result.get("detections", [])
        ]

        response = DrugExtractionResponse(
            detections=detections,
            active_ingredients=result.get("active_ingredients", [])
        )

        return jsonify(response.model_dump()), 200

    except ValidationError as e:
        logger.warning("Validation error: %s", e.message)
        return jsonify({"error": "Validation Error", "message": e.message}), e.status_code

    except Exception as e:
        logger.error("Unexpected error in drug extraction: %s", e, exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500