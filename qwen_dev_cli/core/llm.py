"""Multi-backend LLM client supporting HuggingFace, Ollama, SambaNova, and Blaze."""

import asyncio
from typing import AsyncGenerator, Optional
from huggingface_hub import InferenceClient
from .config import config


class LLMClient:
    """Unified LLM client with multi-backend support."""
    
    def __init__(self):
        """Initialize all available LLM backends."""
        # HuggingFace
        self.hf_client: Optional[InferenceClient] = None
        if config.hf_token:
            self.hf_client = InferenceClient(token=config.hf_token)
        
        # Ollama
        self.ollama_client = None
        if config.ollama_enabled:
            try:
                import ollama
                self.ollama_client = ollama
            except ImportError:
                print("⚠️  Ollama not installed")
        
        # SambaNova (OpenAI-compatible)
        self.sambanova_client = None
        if hasattr(config, 'sambanova_api_key') and config.sambanova_api_key:
            try:
                from openai import OpenAI
                self.sambanova_client = OpenAI(
                    api_key=config.sambanova_api_key,
                    base_url="https://api.sambanova.ai/v1"
                )
            except ImportError:
                print("⚠️  OpenAI SDK not installed (needed for SambaNova)")
        
        # Blaze (code-specialized)
        self.blaze_client = None
        if hasattr(config, 'blaze_api_key') and config.blaze_api_key:
            # Will implement Blaze client when API details confirmed
            pass
        
        # Default provider
        self.default_provider = "hf"  # Can be changed to "auto" for smart routing
    
    async def stream_chat(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        provider: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion with provider selection.
        
        Args:
            prompt: User prompt
            context: Optional context to inject
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            provider: Provider to use ("hf", "sambanova", "blaze", "ollama", "auto")
            
        Yields:
            Generated text chunks
        """
        max_tokens = max_tokens or config.max_tokens
        temperature = temperature or config.temperature
        provider = provider or self.default_provider
        
        # Build messages
        messages = []
        if context:
            messages.append({
                "role": "system",
                "content": f"You are a helpful coding assistant. Use this context:\n\n{context}"
            })
        messages.append({"role": "user", "content": prompt})
        
        # Route to appropriate provider
        if provider == "auto":
            provider = self._select_best_provider(prompt)
        
        if provider == "sambanova" and self.sambanova_client:
            async for chunk in self._stream_sambanova(messages, max_tokens, temperature):
                yield chunk
        elif provider == "blaze" and self.blaze_client:
            async for chunk in self._stream_blaze(messages, max_tokens, temperature):
                yield chunk
        elif provider == "ollama" and self.ollama_client:
            async for chunk in self._stream_ollama(messages, max_tokens, temperature):
                yield chunk
        else:
            # Default to HuggingFace
            async for chunk in self._stream_hf(messages, max_tokens, temperature):
                yield chunk
    
    def _select_best_provider(self, prompt: str) -> str:
        """Simple provider selection logic."""
        # Code generation tasks -> Blaze (if available)
        code_keywords = ["write", "generate", "create", "function", "class", "code"]
        if any(kw in prompt.lower() for kw in code_keywords) and self.blaze_client:
            return "blaze"
        
        # Fast responses -> SambaNova (if available)
        if self.sambanova_client:
            return "sambanova"
        
        # Default to HF
        return "hf"
    
    async def _stream_hf(
        self,
        messages: list,
        max_tokens: int,
        temperature: float
    ) -> AsyncGenerator[str, None]:
        """Stream from HuggingFace."""
        try:
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
            yield f"❌ HF Error: {str(e)}"
    
    async def _stream_sambanova(
        self,
        messages: list,
        max_tokens: int,
        temperature: float
    ) -> AsyncGenerator[str, None]:
        """Stream from SambaNova (OpenAI-compatible)."""
        try:
            loop = asyncio.get_event_loop()
            
            def _generate():
                return self.sambanova_client.chat.completions.create(
                    model="Meta-Llama-3.1-8B-Instruct",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True
                )
            
            stream = await loop.run_in_executor(None, _generate)
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"❌ SambaNova Error: {str(e)}"
    
    async def _stream_blaze(
        self,
        messages: list,
        max_tokens: int,
        temperature: float
    ) -> AsyncGenerator[str, None]:
        """Stream from Blaze (code-specialized)."""
        # Placeholder for Blaze implementation
        yield "⚠️ Blaze integration coming soon"
    
    async def _stream_ollama(
        self,
        messages: list,
        max_tokens: int,
        temperature: float
    ) -> AsyncGenerator[str, None]:
        """Stream from Ollama local inference."""
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
            yield f"❌ Ollama Error: {str(e)}"
    
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        provider: Optional[str] = None
    ) -> str:
        """Generate complete response (non-streaming).
        
        Args:
            prompt: User prompt
            context: Optional context
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            provider: Provider to use
            
        Returns:
            Complete generated text
        """
        chunks = []
        async for chunk in self.stream_chat(prompt, context, max_tokens, temperature, provider):
            chunks.append(chunk)
        return "".join(chunks)
    
    def validate(self) -> tuple[bool, str]:
        """Validate at least one LLM backend is available.
        
        Returns:
            Tuple of (is_valid, message)
        """
        available = []
        
        if self.hf_client:
            available.append("HuggingFace")
        if self.sambanova_client:
            available.append("SambaNova")
        if self.blaze_client:
            available.append("Blaze")
        if self.ollama_client:
            available.append("Ollama")
        
        if not available:
            return False, "No LLM backend available"
        
        return True, f"Backends available: {', '.join(available)}"
    
    def get_available_providers(self) -> list[str]:
        """Get list of available providers."""
        providers = []
        if self.hf_client:
            providers.append("hf")
        if self.sambanova_client:
            providers.append("sambanova")
        if self.blaze_client:
            providers.append("blaze")
        if self.ollama_client:
            providers.append("ollama")
        providers.append("auto")  # Always available
        return providers


# Global LLM client instance
llm_client = LLMClient()
