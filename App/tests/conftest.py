import pytest
import os
from unittest.mock import MagicMock, patch
from App import create_app
from App.config.test import TestConfig

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    os.environ['ENV'] = 'testing'
    app = create_app(TestConfig)
    
    # Context is needed for some Flask operations
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def mock_embedding_service():
    with patch('App.services.EmbeddingService.embedding_service.EmbeddingService') as mock:
        instance = mock.return_value
        instance.embed_text.return_value = [0.1] * 384
        instance.embed_texts.return_value = [[0.1] * 384]
        yield instance

@pytest.fixture
def mock_qdrant_client():
    with patch('qdrant_client.QdrantClient') as mock:
        yield mock.return_value

@pytest.fixture
def mock_llm_service():
    # Mocking various LLM service locations
    with patch('App.services.ContradictionService.drug_Contradiction_service.OpenRouterLLM') as mock_or:
        instance = mock_or.return_value
        instance.generate.return_value = "Mock LLM Response"
        yield instance
