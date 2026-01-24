"""
API v1 Blueprints
"""
from flask import Blueprint

from App.api.v1 import health, semantic_search, contraindications, drug_intelligence, sync


def register_v1_blueprints(app):
    """
    Register all v1 API blueprints
    
    Args:
        app: Flask application instance
    """
    # Create v1 API blueprint
    v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')
    
    # Register route modules
    v1_bp.register_blueprint(health.bp)
    v1_bp.register_blueprint(semantic_search.bp)
    v1_bp.register_blueprint(contraindications.bp)
    v1_bp.register_blueprint(drug_intelligence.bp)
    v1_bp.register_blueprint(sync.bp)
    
    # Register v1 blueprint with app
    app.register_blueprint(v1_bp)
