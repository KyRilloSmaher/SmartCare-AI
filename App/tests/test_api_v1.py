import pytest
import json
import io
from unittest.mock import MagicMock, patch

class TestApiV1:
    def test_health_check(self, client):
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

    @patch('App.api.v1.routes.semantic_search.get_semantic_search_service')
    def test_semantic_search_success(self, mock_get_service, client):
        # Setup mock service
        mock_service = MagicMock()
        mock_service.search.return_value = [
            {"id": "1", "score": 0.9, "name": "Aspirin"}
        ]
        mock_get_service.return_value = mock_service
        
        # Call endpoint
        response = client.post('/api/v1/semantic-search', 
                             data=json.dumps({"query": "pain relief", "top_k": 5}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['query'] == "pain relief"
        assert len(data['results']) == 1
        assert data['results'][0]['id'] == "1"
        mock_service.search.assert_called_once_with(query="pain relief", top_k=5, with_vectors=False)

    def test_semantic_search_validation_error(self, client):
        # Missing 'query' field
        response = client.post('/api/v1/semantic-search', 
                             data=json.dumps({"top_k": 5}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    @patch('App.api.v1.routes.semantic_search.FeatureFlags.is_enabled')
    def test_semantic_search_disabled(self, mock_is_enabled, client):
        mock_is_enabled.return_value = False
        
        response = client.post('/api/v1/semantic-search', 
                             data=json.dumps({"query": "pain relief"}),
                             content_type='application/json')
        
        assert response.status_code == 503
        data = response.get_json()
        assert data['error'] == "Feature disabled"

    @patch('App.api.v1.routes.drug_extraction.get_drug_name_extraction_service')
    def test_extract_drug_success(self, mock_get_service, client):
        mock_service = MagicMock()
        mock_service.extract.return_value = {
            "detections": [{"bbox": [10, 10, 50, 50], "confidence": 0.9}],
            "active_ingredients": ["Aspirin"]
        }
        mock_get_service.return_value = mock_service
        
        data = {'file': (io.BytesIO(b"fake image"), 'test.png')}
        response = client.post('/api/v1/extract-drug', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        res_data = response.get_json()
        assert "Aspirin" in res_data["active_ingredients"]
        assert len(res_data["detections"]) == 1

    @patch('App.api.v1.routes.voice_search.get_voice_search_service')
    def test_voice_search_success(self, mock_get_service, client):
        mock_service = MagicMock()
        mock_service.search.return_value = [{"id": "1", "score": 0.8}]
        mock_get_service.return_value = mock_service
        
        data = {'file': (io.BytesIO(b"fake audio"), 'test.wav'), 'top_k': '5'}
        response = client.post('/api/v1/voice-search', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        res_data = response.get_json()
        assert len(res_data["results"]) == 1
        assert res_data["total"] == 1

    @patch('App.api.v1.routes.chat.get_chat_service')
    def test_chat_json_success(self, mock_get_service, client):
        mock_service = MagicMock()
        mock_service.ask.return_value = "AI Answer"
        mock_get_service.return_value = mock_service
        
        payload = {"question": "What is aspirin?", "ingredients": ["Aspirin"]}
        response = client.post('/api/v1/chat', data=json.dumps(payload), content_type='application/json')
        
        assert response.status_code == 200
        res_data = response.get_json()
        assert res_data["answer"] == "AI Answer"

    @patch('App.api.v1.routes.chat.get_chat_service')
    def test_chat_multipart_success(self, mock_get_service, client):
        mock_service = MagicMock()
        mock_service.ask.return_value = "Audio AI Answer"
        mock_get_service.return_value = mock_service
        
        data = {
            'audio': (io.BytesIO(b"fake audio"), 'test.wav'),
            'question': 'How to use?',
            'ingredients': ['Aspirin']
        }
        response = client.post('/api/v1/chat', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        res_data = response.get_json()
        assert res_data["answer"] == "Audio AI Answer"
