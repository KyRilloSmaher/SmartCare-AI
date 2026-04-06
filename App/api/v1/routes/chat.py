from typing import Optional

from flask import Blueprint, jsonify, request
from werkzeug.datastructures import FileStorage
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from App.services.Chat.IChatService import IChatService
from App.services.service_providers import get_chat_service
from App.config.feature_flags import FeatureFlags
from App.observability.logger import get_logger
from App.utils.exceptions import ValidationError

logger = get_logger(__name__)
bp = Blueprint("chat", __name__)

# ── Request / Response schemas ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    ingredient: str = Field(..., min_length=1)
    question: Optional[str] = None


class ChatResponse(BaseModel):
    ingredient: str
    question: str
    answer: str

# ── Endpoint ──────────────────────────────────────────────────────────────────

@bp.route("/chat", methods=["POST"])
def chat():
    """
    Chat endpoint.

    Supports:
    - application/json:
        { ingredient, question }

    - multipart/form-data:
        - ingredient: str
        - question: optional
        - audio: optional file
    """

    logger.info("Chat endpoint requested")

    if not FeatureFlags.is_enabled("chat"):
        logger.warning("Chat feature is disabled")
        return jsonify({
            "error": "Feature disabled",
            "message": "Chat is currently disabled",
        }), 503

    try:
        ingredient = None
        question = None
        audio_file: Optional[FileStorage] = None

        # Handle JSON request
        if request.content_type.startswith("application/json"):
            data = ChatRequest(**request.get_json())

            ingredient = data.ingredient
            question = data.question

        # Handle multipart/form-data
        elif request.content_type.startswith("multipart/form-data"):
            ingredient = request.form.get("ingredient")
            question = request.form.get("question")
            audio_file = request.files.get("audio")

            if not audio_file:
                raise ValidationError("Audio FIle is required")

        else:
            raise ValidationError("Unsupported content type")

        logger.info("Chat | ingredient=%s", ingredient)

        # Use interface only
        service: IChatService = get_chat_service()

        answer = service.ask(
            ingredient=ingredient,
            question=question,
            audio_file=audio_file
        )

        response = ChatResponse(
            ingredient=ingredient,
            question=question or "",
            answer=answer
        )

        return jsonify(response.model_dump()), 200

    except PydanticValidationError as e:
        logger.warning("Validation error: %s", e.errors())
        return jsonify({"error": "Validation Error", "message": e.errors()}), 400

    except ValidationError as e:
        logger.warning("Validation error: %s", e.message)
        return jsonify({"error": "Validation Error", "message": e.message}), e.status_code

    except Exception as e:
        logger.error("Unexpected error in chat: %s", e, exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500