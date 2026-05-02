import pytest
from unittest.mock import MagicMock, patch
from App.services.Chat.ChatService import ChatService

class TestChatService:
    @pytest.fixture(autouse=True)
    def setup(self):
        with patch('App.services.Chat.ChatService.get_transcription_provider') as self.mock_get_provider, \
             patch('App.services.Chat.ChatService.OpenAI') as self.mock_openai:
            
            self.mock_transcription = self.mock_get_provider.return_value
            self.mock_client = self.mock_openai.return_value
            self.service = ChatService()
            yield

    def test_ask_text_only(self):
        # Setup mocks
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Aspirin is for pain."
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call ask
        answer = self.service.ask(question="What is Aspirin?")
        
        assert "Aspirin is for pain" in answer
        self.mock_client.chat.completions.create.assert_called_once()
        # Verify prompt contains the question
        args, kwargs = self.mock_client.chat.completions.create.call_args
        prompt = kwargs['messages'][1]['content']
        assert "What is Aspirin?" in prompt

    def test_ask_with_ingredients(self):
        # Setup mocks
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Combination response."
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call ask
        answer = self.service.ask(ingredients=["Paracetamol", "Caffeine"], question="Side effects?")
        
        assert "Combination response" in answer
        args, kwargs = self.mock_client.chat.completions.create.call_args
        prompt = kwargs['messages'][1]['content']
        assert "Paracetamol, Caffeine" in prompt
        assert "Side effects?" in prompt

    def test_ask_with_audio(self):
        # Setup mocks
        self.mock_transcription.transcribe.return_value = "how to use it"
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Usage instructions."
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Call ask
        audio_mock = MagicMock()
        answer = self.service.ask(audio_file=audio_mock)
        
        assert "Usage instructions" in answer
        self.mock_transcription.transcribe.assert_called_once_with(audio_mock)
        args, kwargs = self.mock_client.chat.completions.create.call_args
        prompt = kwargs['messages'][1]['content']
        assert "how to use it" in prompt

    def test_retry_logic(self):
        # Fail twice, succeed third time
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Success"
        self.mock_client.chat.completions.create.side_effect = [
            Exception("Fail 1"),
            Exception("Fail 2"),
            mock_response
        ]
        
        answer = self.service.ask(question="Test")
        assert answer == "Success"
        assert self.mock_client.chat.completions.create.call_count == 3
