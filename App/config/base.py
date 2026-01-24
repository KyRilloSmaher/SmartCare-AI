"""
Base configuration class
"""
import os
from typing import Optional


class BaseConfig:
    """Base configuration with common settings"""
    
    # Flask
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Environment
    ENV: str = os.getenv('ENV', 'development')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Vector Database
    VECTOR_DB_TYPE: str = os.getenv('VECTOR_DB_TYPE', 'faiss').lower()
    
    # FAISS Settings
    FAISS_INDEX_PATH: str = os.getenv('FAISS_INDEX_PATH', './faiss_index')
    
    # Qdrant Settings
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")
    
    
    # MSSQL
    MSSQL_CONNECTION_STRING = os.getenv("MSSQL_CONNECTION_STRING")
    # Feature flags
    FEATURE_SEMANTIC_SEARCH = os.getenv("FEATURE_SEMANTIC_SEARCH") == "true"
    FEATURE_DRUG_INTELLIGENCE = os.getenv("FEATURE_DRUG_INTELLIGENCE") == "true"
    FEATURE_CONTRAINDICATIONS = os.getenv("FEATURE_CONTRAINDICATIONS") == "true"
    #openAi
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    HuggingFace_API_KEY = os.getenv("HuggingFace_API_KEY")
    # API
    API_V1_PREFIX: str = '/api/v1'
    

