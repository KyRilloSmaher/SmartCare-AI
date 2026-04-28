from typing import Optional

from flask import Blueprint, jsonify, request
from werkzeug.datastructures import FileStorage
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator
from App.services.Chat.IChatService import IChatService
from App.services.service_providers import get_chat_service
from App.config.feature_flags import FeatureFlags
from App.observability.logger import get_logger
from App.utils.exceptions import ValidationError

logger = get_logger(__name__)
bp = Blueprint("chat", __name__)

# ── Request / Response schemas ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: Optional[str] = None
    ingredients: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_at_least_one(self):
        if not self.question and not self.ingredients:
            raise ValueError("Either 'question' or 'ingredients' must be provided")
        return self


class ChatResponse(BaseModel):
    question: Optional[str]
    ingredients: Optional[list[str]]
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
        return jsonify({
            "error": "Feature disabled",
            "message": "Chat is currently disabled",
        }), 503

    try:
        question = None
        ingredients = None
        audio_file: Optional[FileStorage] = None

        content_type = request.content_type or ""

        # ── JSON ─────────────────────────────
        if content_type.startswith("application/json"):
            data = ChatRequest(**request.get_json())

            question = data.question
            ingredients = data.ingredients

        # ── MULTIPART ───────────────────────
        elif content_type.startswith("multipart/form-data"):
            question = request.form.get("question")

            # Handle list of ingredients
            ingredients = request.form.getlist("ingredients")

            audio_file = request.files.get("audio")

            if not audio_file:
                raise ValidationError("Audio file is required")

        else:
            raise ValidationError("Unsupported content type")

        logger.info("Chat | question=%s | ingredients=%s", question, ingredients)

        service: IChatService = get_chat_service()

        answer = service.ask(
            question=question,
            ingredients=ingredients,
            audio_file=audio_file
        )

        response = ChatResponse(
            question=question,
            ingredients=ingredients,
            answer=answer
        )

        return jsonify(response.model_dump()), 200

    except PydanticValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "message": e.errors()
        }), 400

    except ValidationError as e:
        return jsonify({
            "error": "Validation Error",
            "message": e.message
        }), e.status_code

    except Exception as e:
        logger.error("Unexpected error in chat: %s", e, exc_info=True)
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e)
        }), 500