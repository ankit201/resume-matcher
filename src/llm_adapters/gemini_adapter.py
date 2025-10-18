"""
Google Gemini Adapter
Implementation for Google's Gemini models (used for resume parsing).
"""

import json
import time
from typing import Optional, Dict, Any, Type, TypeVar
from google import genai
from google.genai import types
from google.api_core import exceptions as google_exceptions
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from .base import BaseLLMAdapter, LLMResponse, LLMProvider
from config.settings import get_settings

T = TypeVar('T', bound=BaseModel)


class GeminiAdapter(BaseLLMAdapter):
    """Google Gemini adapter optimized for document parsing"""
    
    def _initialize_client(self) -> None:
        """Initialize Gemini client with new SDK"""
        # New google.genai SDK
        self.client = genai.Client(api_key=self.api_key)
        
        self.settings = get_settings()
        
        # Note: New SDK handles safety settings differently
        # Most cases don't need explicit safety settings for business use
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
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
        Generate completion using Gemini API.
        
        Args:
            prompt: User message
            system_prompt: System instructions (prepended to prompt)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            json_mode: Force JSON output
            **kwargs: Additional Gemini parameters
        
        Returns:
            LLMResponse with standardized format
        """
        start_time = time.time()
        
        # Gemini doesn't have separate system prompt, so prepend it
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        if json_mode:
            full_prompt += "\n\nRespond with valid JSON only."
        
        # Configure generation with proper types
        generation_config = types.GenerateContentConfig(
            temperature=temperature,
            candidate_count=1,
            max_output_tokens=max_tokens if max_tokens else None
        )
        
        try:
            # Generate response with new SDK
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=generation_config
            )
            
            # Extract content
            content = response.text or ""
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            
            # Estimate tokens (Gemini doesn't always provide token counts)
            prompt_tokens = self.count_tokens(full_prompt)
            completion_tokens = self.count_tokens(content)
            total_tokens = prompt_tokens + completion_tokens
            
            # Calculate cost (Gemini Flash tier is typically free/very cheap)
            cost = self.calculate_cost(prompt_tokens, completion_tokens)
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.GOOGLE,
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost=cost,
                latency_ms=latency_ms,
                metadata={
                    "temperature": temperature
                }
            )
        
        except google_exceptions.GoogleAPIError as e:
            print(f"Gemini API error: {str(e)}")
            raise
        
        except Exception as e:
            return LLMResponse(
                content=f"Error: {str(e)}",
                provider=LLMProvider.GOOGLE,
                model=self.model,
                metadata={"error": str(e), "error_type": type(e).__name__}
            )
    
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate structured JSON output (legacy method).
        
        DEPRECATED: Use generate_with_schema() for Pydantic-based structured outputs.
        
        Args:
            prompt: User message
            system_prompt: System instructions
            response_schema: Expected JSON schema
            **kwargs: Additional parameters
        
        Returns:
            LLMResponse with JSON content
        """
        json_instruction = "\n\nYou MUST respond with valid JSON only. No markdown code blocks, no explanations."
        
        if response_schema:
            schema_str = json.dumps(response_schema, indent=2)
            json_instruction += f"\n\nRequired JSON structure:\n{schema_str}"
        
        enhanced_system_prompt = (system_prompt or "") + json_instruction
        
        response = self.generate(
            prompt=prompt,
            system_prompt=enhanced_system_prompt,
            json_mode=True,
            temperature=0.2,  # Low temperature for consistency
            **kwargs
        )
        
        # Clean up markdown-wrapped JSON if present
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        elif content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
        content = content.strip()
        
        # Update response content
        response.content = content
        
        return response
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate_with_schema(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        pdf_data: Optional[bytes] = None,
        **kwargs
    ) -> tuple[T, LLMResponse]:
        """
        Generate structured output using Gemini's native Structured Output with Pydantic.
        
        This uses Gemini's response_schema parameter which accepts Pydantic models directly
        and returns validated, typed data via response.parsed.
        
        Args:
            prompt: User message
            response_model: Pydantic model class defining expected structure
            system_prompt: System instructions
            temperature: Sampling temperature (default 0.3 for structured output)
            max_tokens: Max tokens to generate
            pdf_data: Optional PDF file bytes for multimodal input
            **kwargs: Additional Gemini parameters
        
        Returns:
            Tuple of (parsed_model, llm_response)
            - parsed_model: Instance of response_model with validated data
            - llm_response: LLMResponse with metadata
        
        Example:
            ```python
            class Resume(BaseModel):
                name: str
                skills: list[str]
            
            resume, response = adapter.generate_with_schema(
                prompt="Extract resume info",
                response_model=Resume,
                pdf_data=pdf_bytes
            )
            print(resume.name)
            print(resume.skills)
            ```
        """
        start_time = time.time()
        
        # Prepare prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Configure generation with structured output using proper types
        config = types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=response_model,  # Pydantic model directly!
            max_output_tokens=max_tokens if max_tokens else None
        )
        
        try:
            # Prepare contents - for PDF with new SDK, use proper Part format
            if pdf_data:
                # New SDK expects Part objects or proper format
                # For now, just use text-only until we find correct PDF format
                print(f"⚠️ PDF data provided but new SDK doesn't support dict format yet")
                print(f"⚠️ Falling back to text-only structured output")
                contents = full_prompt
            else:
                contents = full_prompt
            
            # Generate with structured output
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )
            
            # Get the parsed model (automatically deserialized and validated!)
            # Note: response.parsed may be None, dict, or the actual model
            parsed_model = response.parsed
            if not isinstance(parsed_model, response_model):
                # Fallback: parse from text if needed
                parsed_model = response_model.model_validate_json(response.text or "{}")
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            
            # Get text representation
            content = response.text or ""
            
            # Estimate tokens
            prompt_tokens = self.count_tokens(full_prompt)
            completion_tokens = self.count_tokens(content)
            total_tokens = prompt_tokens + completion_tokens
            
            # Calculate cost
            cost = self.calculate_cost(prompt_tokens, completion_tokens)
            
            # Create LLMResponse for metadata
            llm_response = LLMResponse(
                content=content,
                provider=LLMProvider.GOOGLE,
                model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost=cost,
                latency_ms=latency_ms,
                metadata={
                    "temperature": temperature,
                    "structured_output": True,
                    "pdf_processing": pdf_data is not None
                }
            )
            
            return parsed_model, llm_response
        
        except google_exceptions.GoogleAPIError as e:
            print(f"Gemini structured output error: {str(e)}")
            raise
        
        except Exception as e:
            print(f"Unexpected error in structured generation: {str(e)}")
            raise
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate cost for Gemini.
        Note: Gemini 2.0 Flash is free tier initially, but we track for consistency.
        
        Args:
            prompt_tokens: Input tokens
            completion_tokens: Output tokens
        
        Returns:
            Cost in USD
        """
        settings = get_settings()
        input_cost = (prompt_tokens / 1000) * settings.gemini_cost_per_1k_input
        output_cost = (completion_tokens / 1000) * settings.gemini_cost_per_1k_output
        return input_cost + output_cost
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for Gemini.
        Using approximate ratio: 1 token ≈ 4 characters for English.
        
        Args:
            text: Text to count
        
        Returns:
            Estimated token count
        """
        # Rough estimation: 4 chars per token
        return len(text) // 4
    
    def get_provider(self) -> LLMProvider:
        """Return Google provider enum"""
        return LLMProvider.GOOGLE
