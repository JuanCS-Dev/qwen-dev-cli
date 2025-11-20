"""
Tests for Gemini provider.

Boris Cherny: "Test the happy path, test the sad path, test the weird path."
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os

from qwen_dev_cli.core.providers.gemini import GeminiProvider


class TestGeminiProviderInit:
    """Test GeminiProvider initialization."""
    
    def test_init_without_api_key(self):
        """Should initialize without API key (not available)."""
        with patch.dict(os.environ, {}, clear=True):
            provider = GeminiProvider()
            assert provider.is_available() is False
            assert provider.client is None
    
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    def test_init_with_api_key(self, mock_genai):
        """Should initialize with API key."""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        provider = GeminiProvider(api_key="test-key")
        
        assert provider.api_key == "test-key"
        assert provider.is_available() is True
        mock_genai.configure.assert_called_once_with(api_key="test-key")
    
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    def test_init_with_env_var(self, mock_genai):
        """Should use GEMINI_API_KEY env var."""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'env-key'}):
            provider = GeminiProvider()
            assert provider.api_key == "env-key"
    
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    def test_init_with_custom_model(self, mock_genai):
        """Should use custom model from env."""
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict(os.environ, {
            'GEMINI_API_KEY': 'test-key',
            'GEMINI_MODEL': 'gemini-pro-vision'
        }):
            provider = GeminiProvider()
            assert provider.model_name == "gemini-pro-vision"
            mock_genai.GenerativeModel.assert_called_with("gemini-pro-vision")


class TestGeminiProviderGenerate:
    """Test generation methods."""
    
    @pytest.mark.asyncio
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    async def test_generate_success(self, mock_genai):
        """Should generate text successfully."""
        # Setup mocks
        mock_response = Mock()
        mock_response.text = "Generated response"
        
        mock_client = Mock()
        mock_client.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_client
        
        # Test
        provider = GeminiProvider(api_key="test-key")
        result = await provider.generate([
            {'role': 'user', 'content': 'Hello'}
        ])
        
        assert result == "Generated response"
        mock_client.generate_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_without_client(self):
        """Should raise error if client not available."""
        provider = GeminiProvider()  # No API key
        
        with pytest.raises(RuntimeError, match="not available"):
            await provider.generate([
                {'role': 'user', 'content': 'Hello'}
            ])
    
    @pytest.mark.asyncio
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    async def test_generate_with_parameters(self, mock_genai):
        """Should pass generation parameters correctly."""
        mock_response = Mock()
        mock_response.text = "Response"
        
        mock_client = Mock()
        mock_client.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_client
        
        provider = GeminiProvider(api_key="test-key")
        await provider.generate(
            [{'role': 'user', 'content': 'Test'}],
            max_tokens=1024,
            temperature=0.5
        )
        
        # Check generation_config was passed
        call_args = mock_client.generate_content.call_args
        config = call_args[1]['generation_config']
        assert config['max_output_tokens'] == 1024
        assert config['temperature'] == 0.5


class TestGeminiProviderStreaming:
    """Test streaming generation."""
    
    @pytest.mark.asyncio
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    async def test_stream_generate_success(self, mock_genai):
        """Should stream text chunks successfully."""
        # Setup mock chunks
        mock_chunk1 = Mock()
        mock_chunk1.text = "Hello "
        mock_chunk2 = Mock()
        mock_chunk2.text = "World"
        
        mock_client = Mock()
        mock_client.generate_content.return_value = [mock_chunk1, mock_chunk2]
        mock_genai.GenerativeModel.return_value = mock_client
        
        # Test
        provider = GeminiProvider(api_key="test-key")
        chunks = []
        async for chunk in provider.stream_generate([
            {'role': 'user', 'content': 'Test'}
        ]):
            chunks.append(chunk)
        
        assert chunks == ["Hello ", "World"]
    
    @pytest.mark.asyncio
    async def test_stream_generate_without_client(self):
        """Should raise error if client not available."""
        provider = GeminiProvider()
        
        with pytest.raises(RuntimeError, match="not available"):
            async for _ in provider.stream_generate([
                {'role': 'user', 'content': 'Test'}
            ]):
                pass


class TestGeminiProviderFormatting:
    """Test message formatting."""
    
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    def test_format_single_message(self, mock_genai):
        """Should format single user message."""
        mock_genai.GenerativeModel.return_value = Mock()
        provider = GeminiProvider(api_key="test-key")
        
        result = provider._format_messages([
            {'role': 'user', 'content': 'Hello'}
        ])
        
        assert result == "User: Hello"
    
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    def test_format_multiple_messages(self, mock_genai):
        """Should format conversation with multiple messages."""
        mock_genai.GenerativeModel.return_value = Mock()
        provider = GeminiProvider(api_key="test-key")
        
        result = provider._format_messages([
            {'role': 'system', 'content': 'You are helpful'},
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'},
            {'role': 'user', 'content': 'How are you?'}
        ])
        
        expected = (
            "System: You are helpful\n\n"
            "User: Hello\n\n"
            "Assistant: Hi there!\n\n"
            "User: How are you?"
        )
        assert result == expected


class TestGeminiProviderInfo:
    """Test provider info methods."""
    
    def test_get_model_info_unavailable(self):
        """Should return info when provider not available."""
        provider = GeminiProvider()
        info = provider.get_model_info()
        
        assert info['provider'] == 'gemini'
        assert info['available'] is False
        assert info['supports_streaming'] is True
    
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    def test_get_model_info_available(self, mock_genai):
        """Should return info when provider available."""
        mock_genai.GenerativeModel.return_value = Mock()
        provider = GeminiProvider(api_key="test-key")
        info = provider.get_model_info()
        
        assert info['provider'] == 'gemini'
        assert info['available'] is True
        assert info['model'] == 'gemini-pro'
        assert info['context_window'] == 32768
    
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    def test_count_tokens(self, mock_genai):
        """Should estimate token count."""
        mock_genai.GenerativeModel.return_value = Mock()
        provider = GeminiProvider(api_key="test-key")
        
        # ~4 chars per token
        count = provider.count_tokens("Hello World!")
        assert count == 3  # 12 chars / 4 = 3 tokens


class TestGeminiProviderErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    async def test_generate_api_error(self, mock_genai):
        """Should handle API errors gracefully."""
        mock_client = Mock()
        mock_client.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_client
        
        provider = GeminiProvider(api_key="test-key")
        
        with pytest.raises(Exception, match="API Error"):
            await provider.generate([{'role': 'user', 'content': 'Test'}])
    
    @pytest.mark.asyncio
    @patch('qwen_dev_cli.core.providers.gemini.genai', create=True)
    async def test_stream_generate_api_error(self, mock_genai):
        """Should handle streaming API errors."""
        mock_client = Mock()
        mock_client.generate_content.side_effect = Exception("Stream Error")
        mock_genai.GenerativeModel.return_value = mock_client
        
        provider = GeminiProvider(api_key="test-key")
        
        with pytest.raises(Exception, match="Stream Error"):
            async for _ in provider.stream_generate([
                {'role': 'user', 'content': 'Test'}
            ]):
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
