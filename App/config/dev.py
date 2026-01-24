"""
Development configuration
"""
from .base import BaseConfig


class DevConfig(BaseConfig):
    """Development configuration"""
    
    DEBUG = True
    ENV = 'development'
    
    # Development: Use FAISS by default
    VECTOR_DB_TYPE = 'faiss'
    
    # More verbose logging in dev
    LOG_LEVEL = 'DEBUG'
