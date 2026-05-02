import pytest
from unittest.mock import MagicMock, patch
from App.services.VoiceSearch.Voice_search_service import VoiceSearchService

class TestVoiceSearchService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_semantic = MagicMock()
        with patch('App.services.VoiceSearch.Voice_search_service.get_transcription_provider') as self.mock_get_provider, \
             patch('App.services.VoiceSearch.Voice_search_service.EmbeddingService'), \
             patch('App.services.VoiceSearch.Voice_search_service.get_repo'), \
             patch('App.services.VoiceSearch.Voice_search_service.Cleaner'), \
             patch('App.services.VoiceSearch.Voice_search_service.LanguageDetector'):
            
            self.mock_transcription = self.mock_get_provider.return_value
            self.service = VoiceSearchService(self.mock_semantic)
            yield

    def test_search_success(self):
        # Setup mocks
        self.mock_transcription.transcribe.return_value = "aspirin"
        self.mock_semantic.search.return_value = [{"id": "1", "score": 0.9}]
        
        # Call search
        audio_mock = MagicMock()
        results = self.service.search(audio_mock)
        
        assert len(results) == 1
        assert results[0]["id"] == "1"
        self.mock_transcription.transcribe.assert_called_once_with(audio_mock)
        self.mock_semantic.search.assert_called_once_with(query="aspirin", top_k=10, with_vectors=False)

    def test_search_empty_audio(self):
        results = self.service.search(None)
        assert results == []
        self.mock_transcription.transcribe.assert_not_called()

    def test_search_transcription_failed(self):
        self.mock_transcription.transcribe.return_value = ""
        results = self.service.search(MagicMock())
        assert results == []
        self.mock_semantic.search.assert_not_called()
