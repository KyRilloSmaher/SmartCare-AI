import pytest
from unittest.mock import MagicMock, patch
from App.services.SemanticSearchService.semantic_search_service import SemanticSearchService


class TestSemanticSearchService:

    @pytest.fixture(autouse=True)
    def setup(self):

        with patch('App.services.SemanticSearchService.semantic_search_service.EmbeddingService') as self.mock_embedding, \
             patch('App.services.SemanticSearchService.semantic_search_service.get_repo') as self.mock_get_repo, \
             patch('App.services.SemanticSearchService.semantic_search_service.Cleaner') as self.mock_cleaner, \
             patch('App.services.SemanticSearchService.semantic_search_service.LanguageDetector') as self.mock_lang, \
             patch('App.services.SemanticSearchService.semantic_search_service.get_intent_model') as self.mock_intent:

            # -----------------------------
            # Mock embedding service
            # -----------------------------
            self.mock_emb_instance = self.mock_embedding.return_value
            self.mock_emb_instance.embed_texts.return_value = [[0.1] * 384]

            # -----------------------------
            # Mock vector repo
            # -----------------------------
            self.mock_repo_instance = self.mock_get_repo.return_value
            self.mock_repo_instance.search.return_value = [
                {"id": "1", "score": 0.95}
            ]

            # -----------------------------
            # Mock cleaner
            # -----------------------------
            self.mock_cleaner_instance = self.mock_cleaner.return_value
            self.mock_cleaner_instance.clean_text.return_value = "cleaned query"

            # -----------------------------
            # Mock language detector
            # -----------------------------
            self.mock_lang_instance = self.mock_lang.return_value
            self.mock_lang_instance.detect_language.return_value = "en"

            # -----------------------------
            # 🔥 NEW: Mock intent model
            # -----------------------------
            self.mock_intent_instance = self.mock_intent.return_value
            self.mock_intent_instance.predict.return_value = 1  # default = medical

            yield

    # ---------------------------------------------------------
    # ✅ 1. SUCCESS CASE (medical query)
    # ---------------------------------------------------------
    def test_search_success(self):
        service = SemanticSearchService()

        results = service.search("aspirin")

        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["id"] == "1"

        self.mock_repo_instance.search.assert_called_once()

    # ---------------------------------------------------------
    # ✅ 2. EMPTY QUERY
    # ---------------------------------------------------------
    def test_search_empty_query(self):
        service = SemanticSearchService()

        results = service.search("")

        assert results == []
        self.mock_repo_instance.search.assert_not_called()

    # ---------------------------------------------------------
    # ❌ 3. NON-MEDICAL QUERY (NOW CONTROLLED BY ML MODEL)
    # ---------------------------------------------------------
    def test_non_medical_query(self):
        # 🔥 force model to classify as NOT medical
        self.mock_intent_instance.predict.return_value = 0

        service = SemanticSearchService()

        results = service.search("how to bake a cake")

        assert isinstance(results, dict)
        assert results["success"] is False
        assert "only allowed for medical purposes" in results["error"].lower()

        self.mock_repo_instance.search.assert_not_called()

    # ---------------------------------------------------------
    # 🚨 4. SAFE MEDICAL QUERY FLOW
    # ---------------------------------------------------------
    def test_medical_query_flow(self):
        self.mock_intent_instance.predict.return_value = 1

        service = SemanticSearchService()

        results = service.search("headache medicine")

        assert isinstance(results, list)
        self.mock_repo_instance.search.assert_called_once()

    # ---------------------------------------------------------
    # ⚠️ 5. INTENT MODEL FAILURE FALLBACK
    # ---------------------------------------------------------
    def test_intent_model_failure(self):
        self.mock_intent_instance.predict.side_effect = Exception("model crashed")

        service = SemanticSearchService()

        results = service.search("aspirin")

        # should safely fail (your service returns False -> rejected)
        assert isinstance(results, dict)
        assert results["success"] is False
        self.mock_repo_instance.search.assert_not_called()