import pytest
from unittest.mock import MagicMock, patch
from App.services.ContradictionService.drug_Contradiction_service import ContradictionService

class TestContradictionService:
    @pytest.fixture(autouse=True)
    def setup(self):
        with patch('App.services.ContradictionService.drug_Contradiction_service.get_repo') as self.mock_get_repo:
            self.mock_repo_instance = self.mock_get_repo.return_value
            yield

    def test_find_all_contradictions_success(self):
        product_id = "1"
        candidate_ids = ["2", "3"]
        
        self.mock_repo_instance.get_vector.side_effect = lambda id: [0.1]*384 if id in ["1", "2", "3"] else None
        self.mock_repo_instance.similarity.return_value = 0.8
        self.mock_repo_instance.get_product_text.side_effect = lambda id: {
            "1": "This drug increases blood pressure",
            "2": "This drug decreases blood pressure",
            "3": "This drug increases heart rate"
        }.get(id, "")
        
        service = ContradictionService()
        results = service.find_all_contradictions(product_id, candidate_ids)
        
        # Result 2 should be a contradiction (increase vs decrease)
        # Result 3 should NOT be (increase vs increase)
        assert len(results) == 1
        assert results[0]["id"] == "2"
        assert results[0]["score"] == -0.8

    def test_is_opposite_effect(self):
        service = ContradictionService()
        assert service._is_opposite_effect("increase heart rate", "decrease heart rate") is True
        assert service._is_opposite_effect("stimulate brain", "inhibit brain") is True
        assert service._is_opposite_effect("increase heart rate", "increase blood pressure") is False
        assert service._is_opposite_effect("vasodilation", "vasoconstriction") is True

    def test_find_all_contradictions_no_vector(self):
        self.mock_repo_instance.get_vector.return_value = None
        service = ContradictionService()
        results = service.find_all_contradictions("1", ["2"])
        assert results == []
