"""
Health check endpoint
"""
from flask import Blueprint, jsonify
from datetime import datetime

from App.observability.logger import get_logger
from App.config.feature_flags import FeatureFlags

logger = get_logger(__name__)

bp = Blueprint('health', __name__)


@bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON response with service status
    """
    logger.debug('Health check requested')
    
    return jsonify({
        'status': 'healthy',
        'service': 'SmartCare-AI',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'features': FeatureFlags.get_all()
    }), 200
