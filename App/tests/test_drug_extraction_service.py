import pytest
import io
from unittest.mock import MagicMock, patch
from App.services.DrugNameExtraction.DrugNameExtractionService import DrugNameExtractionService

class TestDrugExtractionService:
    @pytest.fixture(autouse=True)
    def setup(self):
        with patch('App.services.DrugNameExtraction.DrugNameExtractionService.YOLO') as self.mock_yolo:
            # Mock YOLO initialization
            self.service = DrugNameExtractionService()
            yield

    @patch('App.services.DrugNameExtraction.DrugNameExtractionService.requests.post')
    @patch('App.services.DrugNameExtraction.DrugNameExtractionService.Image.open')
    def test_extract_success(self, mock_image_open, mock_post):
        # Setup image mock
        mock_img = MagicMock()
        mock_image_open.return_value.convert.return_value = mock_img
        
        # Setup YOLO mock
        mock_results = MagicMock()
        mock_box = MagicMock()
        mock_box.xyxy = [MagicMock(tolist=lambda: [10, 10, 50, 50])]
        mock_box.conf = [0.95]
        mock_results.boxes = [mock_box]
        self.mock_yolo.return_value.return_value = [mock_results]
        
        # Setup OCR mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ParsedResults": [{"ParsedText": "PANADOL"}]
        }
        mock_post.return_value = mock_response
        
        # Call extract
        file_mock = io.BytesIO(b"dummy image data")
        result = self.service.extract(file_mock)
        
        assert "active_ingredients" in result
        assert "PANADOL" in result["active_ingredients"]
        assert len(result["detections"]) == 1
        assert result["detections"][0]["confidence"] == 0.95

    def test_extract_no_detections(self):
        # Setup YOLO mock with no boxes
        mock_results = MagicMock()
        mock_results.boxes = []
        self.mock_yolo.return_value.return_value = [mock_results]
        
        # Call extract
        file_mock = io.BytesIO(b"dummy image data")
        with patch('App.services.DrugNameExtraction.DrugNameExtractionService.Image.open'):
            result = self.service.extract(file_mock)
        
        assert result["detections"] == []
        assert result["active_ingredients"] == []

    def test_remove_duplicates(self):
        texts = ["Aspirin", "aspirin", "Panadol", "ASPIRIN"]
        unique = self.service._remove_duplicates(texts)
        assert unique == ["Aspirin", "Panadol"]
