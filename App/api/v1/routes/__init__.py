# App/api/v1/routes/__init__.py
from flask import Blueprint

from App.api.v1.routes import health, sync
from App.api.v1.routes import contradictions  # Import the module, not the function
from App.api.v1.routes import similarity      # Import the module, not the function


def register_v1_blueprints(app):
    """
    Register all v1 API blueprints
    """
    # Import route modules here to avoid circular imports
    from . import semantic_search

    v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

    # Register route modules - use the blueprint objects from each module
    v1_bp.register_blueprint(health.bp)
    v1_bp.register_blueprint(semantic_search.bp)
    v1_bp.register_blueprint(contradictions.bp_contradictions)  # Use the correct blueprint name
    v1_bp.register_blueprint(similarity.bp_similarity)          # Use the correct blueprint name
    v1_bp.register_blueprint(sync.bp)

    # Register v1 blueprint with app
    app.register_blueprint(v1_bp)