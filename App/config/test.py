"""
Testing configuration class
"""
import os
from .base import BaseConfig

class TestConfig(BaseConfig):
    """Testing configuration"""
    
    ENV = 'testing'
    TESTING = True
    DEBUG = True
    
    # Use dummy/in-memory values for testing
    VECTOR_DB_TYPE = 'faiss'
    FAISS_INDEX_PATH = ':memory:'
    
    # Disable heavy features if needed, or mock them
    FEATURE_SEMANTIC_SEARCH = True
    FEATURE_DRUG_INTELLIGENCE = True
    FEATURE_CONTRAINDICATIONS = True
    
    # Mock API Keys to avoid using real ones during tests
    OPENAI_API_KEY = 'mock-key'
    HuggingFace_API_KEY = 'mock-key'
    OCR_API_KEY = 'mock-key'
    OPENROUTER_API_KEY = 'mock-key'
