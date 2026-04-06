from typing import Any, Dict, List, Optional

from flask import Blueprint, jsonify, request
from werkzeug.datastructures import FileStorage
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from App.services.service_providers import IVoiceSearchService, get_voice_search_service
from App.config.feature_flags import FeatureFlags
from App.observability.logger import get_logger
from App.utils.exceptions import ValidationError

logger = get_logger(__name__)
bp = Blueprint("voice_search", __name__)

# ── Request / Response schemas ────────────────────────────────────────────────

class VoiceSearchResultItem(BaseModel):
    id: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class VoiceSearchResponse(BaseModel):
    top_k: int
    results: List[VoiceSearchResultItem]
    total: int

# ── Endpoint ──────────────────────────────────────────────────────────────────

@bp.route("/voice-search", methods=["POST"])
def voice_search():
    """
    Voice search endpoint.

    Accepts audio file as multipart/form-data:
        - file: Audio file
        - top_k: optional int
        - with_vectors: optional bool
    """
    logger.info("Voice search requested")

    if not FeatureFlags.is_enabled("voice_search"):
        logger.warning("Voice search feature is disabled")
        return jsonify({
            "error": "Feature disabled",
            "message": "Voice search is currently disabled",
        }), 503

    try:
        # Get audio file
        audio_file: FileStorage = request.files.get("file")
        if not audio_file:
            raise ValidationError("Audio file ('file') is required in multipart/form-data")

        # Get optional parameters
        top_k = int(request.form.get("top_k", 10))
        with_vectors = request.form.get("with_vectors", "false").lower() == "true"

        logger.info("VoiceSearch | filename=%s top_k=%d", audio_file.filename, top_k)

        # Use the interface only
        service: IVoiceSearchService = get_voice_search_service()

        raw_results: List[Dict[str, Any]] = service.search(
            audio_file=audio_file,
            top_k=top_k,
            with_vectors=with_vectors
        )

        items = [
            VoiceSearchResultItem(
                id=r["id"],
                score=r["score"],
                metadata={k: v for k, v in r.items() if k not in ("id", "score")} or None
            ) for r in raw_results
        ]

        resp = VoiceSearchResponse(
            top_k=top_k,
            results=items,
            total=len(items)
        )

        return jsonify(resp.model_dump()), 200

    except ValidationError as e:
        logger.warning("Validation error: %s", e.message)
        return jsonify({"error": "Validation Error", "message": e.message}), e.status_code
    except Exception as e:
        logger.error("Unexpected error in voice search: %s", e, exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500