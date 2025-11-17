"""LLM client for HuggingFace Inference API and Ollama."""

import asyncio
from typing import AsyncGenerator, Optional
from huggingface_hub import InferenceClient
from .config import config


class LLMClient:
    """Unified LLM client supporting HuggingFace and Ollama."""
    
    def __init__(self):
        """Initialize LLM client."""
        self.hf_client: Optional[InferenceClient] = None
        self.ollama_client = None
        
        # Initialize HuggingFace client if token is available
        if config.hf_token:
            self.hf_client = InferenceClient(token=config.hf_token)
        
        # Initialize Ollama client if enabled
        if config.ollama_enabled:
            try:
                import ollama
                self.ollama_client = ollama
            except ImportError:
                print("⚠️  Ollama not installed. Install with: pip install ollama")
    
    async def stream_chat(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion responses.
        
        Args:
            prompt: User prompt
            context: Optional context to inject
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Yields:
            Generated text chunks
        """
        max_tokens = max_tokens or config.max_tokens
        temperature = temperature or config.temperature
        
        # Build messages
        messages = []
        
        if context:
            messages.append({
                "role": "system",
                "content": f"You are a helpful coding assistant. Use this context:\n\n{context}"
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Use HuggingFace if available
        if self.hf_client:
            async for chunk in self._stream_hf(messages, max_tokens, temperature):
                yield chunk
        
        # Fallback to Ollama if HF not available
        elif self.ollama_client:
            async for chunk in self._stream_ollama(messages, max_tokens, temperature):
                yield chunk
        
        else:
            raise ValueError("No LLM backend available. Set HF_TOKEN or enable Ollama.")
    
    async def _stream_hf(
        self,
        messages: list,
        max_tokens: int,
        temperature: float
    ) -> AsyncGenerator[str, None]:
        """Stream from HuggingFace Inference API.
        
        Args:
            messages: Chat messages
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            
        Yields:
            Text chunks
        """
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _generate():
                return self.hf_client.chat_completion(
                    messages=messages,
                    model=config.hf_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True
                )
            
            stream = await loop.run_in_executor(None, _generate)
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"❌ Error: {str(e)}"
    
    async def _stream_ollama(
        self,
        messages: list,
        max_tokens: int,
        temperature: float
    ) -> AsyncGenerator[str, None]:
        """Stream from Ollama local inference.
        
        Args:
            messages: Chat messages
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            
        Yields:
            Text chunks
        """
        try:
            response = self.ollama_client.chat(
                model=config.ollama_model,
                messages=messages,
                stream=True,
                options={
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            )
            
            for chunk in response:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            yield f"❌ Error: {str(e)}"
    
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate complete response (non-streaming).
        
        Args:
            prompt: User prompt
            context: Optional context
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            
        Returns:
            Complete generated text
        """
        chunks = []
        async for chunk in self.stream_chat(prompt, context, max_tokens, temperature):
            chunks.append(chunk)
        return "".join(chunks)
    
    def validate(self) -> tuple[bool, str]:
        """Validate LLM client is ready.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.hf_client and not self.ollama_client:
            return False, "No LLM backend available"
        
        if self.hf_client:
            return True, "HuggingFace Inference API ready"
        
        if self.ollama_client:
            return True, "Ollama ready"
        
        return False, "Unknown error"


# Global LLM client instance
llm_client = LLMClient()
