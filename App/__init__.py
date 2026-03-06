"""
SmartCare-AI Flask Application
"""
from flask import Flask, jsonify

from App.config import get_config
from App.observability.logger import setup_logger
from App.api.v1.routes import register_v1_blueprints

def create_app(config_class=None) -> Flask:
    app = Flask(__name__)

    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # Setup logging
    logger = setup_logger('smartcare', app.config.get('LOG_LEVEL'))
    logger.info(f'Starting SmartCare-AI in {app.config.get("ENV")} mode')

    # Register blueprints
    register_v1_blueprints(app)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(error, exc_info=True)
        return jsonify({'error': 'Internal Server Error'}), 500

    from App.utils.exceptions import SmartCareException

    @app.errorhandler(SmartCareException)
    def handle_smartcare_exception(error):
        return jsonify({'error': error.message}), error.status_code

    logger.info('SmartCare-AI application initialized successfully')
    return app
