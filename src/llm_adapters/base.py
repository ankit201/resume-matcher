"""
Base LLM Adapter
Abstract base class defining the interface for all LLM providers.
Following SOLID principles: Single Responsibility, Interface Segregation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers (only Google/Gemini)"""
    GOOGLE = "google"


@dataclass
class LLMResponse:
    """
    Standardized response format from any LLM provider.
    Ensures consistent interface regardless of underlying provider.
    """
    content: str
    provider: LLMProvider
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_cost(self) -> float:
        """Total cost in USD"""
        return self.cost
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            "content": self.content,
            "provider": self.provider.value,
            "model": self.model,
            "tokens": {
                "prompt": self.prompt_tokens,
                "completion": self.completion_tokens,
                "total": self.total_tokens
            },
            "cost": self.cost,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class BaseLLMAdapter(ABC):
    """
    Abstract base class for LLM adapters.
    All concrete adapters must implement these methods.
    """
    
    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize adapter with API credentials.
        
        Args:
            api_key: API key for the LLM provider
            model: Model name to use
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self) -> None:
        """Initialize the provider-specific client. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from the LLM.
        
        Args:
            prompt: User prompt/message
            system_prompt: System instructions (optional)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            json_mode: Whether to force JSON output
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse with standardized format
            
        Raises:
            Exception: If generation fails
        """
        pass
    
    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate structured output (JSON) from the LLM.
        
        Args:
            prompt: User prompt/message
            system_prompt: System instructions (optional)
            response_schema: Expected JSON schema (optional)
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse with JSON content
        """
        pass
    
    @abstractmethod
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate cost in USD for the API call.
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (provider-specific tokenization).
        
        Args:
            text: Text to tokenize
            
        Returns:
            Number of tokens
        """
        pass
    
    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[LLMResponse]:
        """
        Generate completions for multiple prompts.
        Default implementation processes sequentially.
        Subclasses can override for parallel processing.
        
        Args:
            prompts: List of prompts
            system_prompt: System instructions (optional)
            **kwargs: Additional parameters
            
        Returns:
            List of LLMResponse objects
        """
        responses = []
        for prompt in prompts:
            try:
                response = self.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    **kwargs
                )
                responses.append(response)
            except Exception as e:
                # Create error response
                error_response = LLMResponse(
                    content=f"Error: {str(e)}",
                    provider=self.get_provider(),
                    model=self.model,
                    metadata={"error": str(e)}
                )
                responses.append(error_response)
        return responses
    
    @abstractmethod
    def get_provider(self) -> LLMProvider:
        """Return the provider enum for this adapter"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get adapter information"""
        return {
            "provider": self.get_provider().value,
            "model": self.model,
            "config": self.config
        }
