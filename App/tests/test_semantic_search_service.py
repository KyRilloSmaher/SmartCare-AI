import pytest
from unittest.mock import MagicMock, patch
from App.services.SemanticSearchService.semantic_search_service import SemanticSearchService

class TestSemanticSearchService:
    @pytest.fixture(autouse=True)
    def setup(self):
        with patch('App.services.SemanticSearchService.semantic_search_service.EmbeddingService') as self.mock_embedding, \
             patch('App.services.SemanticSearchService.semantic_search_service.get_repo') as self.mock_get_repo, \
             patch('App.services.SemanticSearchService.semantic_search_service.Cleaner') as self.mock_cleaner, \
             patch('App.services.SemanticSearchService.semantic_search_service.LanguageDetector') as self.mock_lang:
            
            self.mock_emb_instance = self.mock_embedding.return_value
            self.mock_emb_instance.embed_texts.return_value = [[0.1]*384]
            
            self.mock_repo_instance = self.mock_get_repo.return_value
            self.mock_repo_instance.similarity.return_value = 0.9 # Default to medical
            self.mock_repo_instance.search.return_value = [{"id": "1", "score": 0.95}]
            
            self.mock_cleaner_instance = self.mock_cleaner.return_value
            self.mock_cleaner_instance.clean_text.return_value = "cleaned query"
            
            self.mock_lang_instance = self.mock_lang.return_value
            self.mock_lang_instance.detect_language.return_value = "en"
            
            yield

    def test_search_success(self):
        service = SemanticSearchService()
        results = service.search("aspirin")
        
        assert len(results) == 1
        assert results[0]["id"] == "1"
        self.mock_repo_instance.search.assert_called_once()

    def test_search_empty_query(self):
        service = SemanticSearchService()
        results = service.search("")
        
        assert results == []
        self.mock_repo_instance.search.assert_not_called()

    def test_non_medical_query(self):
        self.mock_repo_instance.similarity.return_value = 0.2 # Non-medical
        
        service = SemanticSearchService()
        results = service.search("how to bake a cake")
        
        assert len(results) == 1
        assert "error" in results[0]
        assert "Medical Purpose" in results[0]["error"]
        self.mock_repo_instance.search.assert_not_called()
