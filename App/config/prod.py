"""
Production configuration
"""
from .base import BaseConfig


class ProdConfig(BaseConfig):
    """Production configuration"""
    
    DEBUG = False
    ENV = 'production'
    
    # Production: Use Qdrant by default
    VECTOR_DB_TYPE = 'qdrant'
    
    # Production logging
    LOG_LEVEL = 'INFO'
    
    # Ensure secret key is set
    @property
    def SECRET_KEY(self) -> str:
        key = super().SECRET_KEY
        if key == 'dev-secret-key-change-in-production':
            raise ValueError(
                "SECRET_KEY must be set in production environment"
            )
        return key
