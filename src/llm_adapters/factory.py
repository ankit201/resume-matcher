"""
LLM Adapter Factory
Factory pattern for creating LLM adapters with proper dependency injection.
Simplified to only support Gemini provider.
"""

from typing import Optional
from .base import BaseLLMAdapter, LLMProvider
from .gemini_adapter import GeminiAdapter
from .langchain_gemini import GeminiStructuredLLM
from config.settings import get_settings


class LLMFactory:
    """
    Simplified factory for creating Gemini LLM adapters.
    Supports both legacy adapter and new LangChain-based adapter.
    """
    
    @staticmethod
    def create_adapter(
        provider: LLMProvider = LLMProvider.GOOGLE,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> BaseLLMAdapter:
        """
        Create a Gemini LLM adapter.
        
        Args:
            provider: LLM provider (only GOOGLE/Gemini supported)
            api_key: API key (if None, loads from settings)
            model: Model name (if None, loads from settings)
            **kwargs: Additional configuration
        
        Returns:
            Initialized Gemini adapter
        
        Raises:
            ValueError: If provider is not GOOGLE
        """
        if provider != LLMProvider.GOOGLE:
            raise ValueError(f"Only Gemini (GOOGLE) provider is supported. Got: {provider}")
        
        settings = get_settings()
        
        return GeminiAdapter(
            api_key=api_key or settings.google_api_key,
            model=model or settings.gemini_model,
            **kwargs
        )
    
    @staticmethod
    def create_gemini_adapter(
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> GeminiAdapter:
        """Create Gemini adapter (legacy adapter with native SDK)"""
        settings = get_settings()
        return GeminiAdapter(
            api_key=api_key or settings.google_api_key,
            model=model or settings.gemini_model,
            **kwargs
        )
    
    @staticmethod
    def create_langchain_gemini(
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        **kwargs
    ) -> GeminiStructuredLLM:
        """Create LangChain-based Gemini adapter with structured outputs"""
        settings = get_settings()
        return GeminiStructuredLLM(
            model=model or settings.gemini_model,
            temperature=temperature,
            api_key=api_key or settings.google_api_key,
            **kwargs
        )
    
    @staticmethod
    def get_default_adapter() -> BaseLLMAdapter:
        """
        Get the default adapter (Gemini).
        
        Returns:
            Default Gemini LLM adapter
        """
        return LLMFactory.create_gemini_adapter()
    
    @staticmethod
    def get_parsing_adapter() -> BaseLLMAdapter:
        """
        Get the adapter optimized for document parsing (Gemini Flash).
        
        Returns:
            Parsing-optimized Gemini adapter
        """
        return LLMFactory.create_gemini_adapter()
