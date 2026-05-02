import pytest
from unittest.mock import MagicMock, patch
from App.services.SimilarityService.drug_similars_service import SimilarityService

class TestSimilarityService:
    @pytest.fixture(autouse=True)
    def setup(self):
        with patch('App.services.SimilarityService.drug_similars_service.get_repo') as self.mock_get_repo:
            self.mock_repo_instance = self.mock_get_repo.return_value
            yield

    def test_find_similar_by_id_success(self):
        product_id = "123"
        self.mock_repo_instance.get_vector.return_value = [0.1] * 384
        self.mock_repo_instance.search.return_value = [
            {"id": "123", "score": 1.0},
            {"id": "456", "score": 0.8},
            {"id": "789", "score": 0.7}
        ]
        
        service = SimilarityService()
        results = service.find_similar_by_id(product_id, top_k=2)
        
        # Should exclude self and return 2 results
        assert len(results) == 2
        assert results[0]["id"] == "456"
        assert results[1]["id"] == "789"

    def test_find_similar_by_id_not_found(self):
        self.mock_repo_instance.get_vector.return_value = None
        
        service = SimilarityService()
        results = service.find_similar_by_id("non-existent")
        
        assert results == []
        self.mock_repo_instance.search.assert_not_called()

    def test_find_similar_by_id_threshold(self):
        product_id = "123"
        self.mock_repo_instance.get_vector.return_value = [0.1] * 384
        self.mock_repo_instance.search.return_value = [
            {"id": "456", "score": 0.8},
            {"id": "789", "score": 0.5}
        ]
        
        service = SimilarityService()
        results = service.find_similar_by_id(product_id, score_threshold=0.6)
        
        assert len(results) == 1
        assert results[0]["id"] == "456"
