"""
LangChain wrapper for Google Gemini with structured output support.
This adapter uses LangChain's ChatGoogleGenerativeAI for consistent interface.
"""

from typing import Type, Optional, Any, Dict
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os


class GeminiStructuredLLM:
    """
    LangChain-based wrapper for Gemini with structured output support.
    
    Uses LangChain's ChatGoogleGenerativeAI and PydanticOutputParser for
    reliable structured outputs.
    """
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.2,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Gemini LLM adapter.
        
        Args:
            model: Gemini model name (default: gemini-2.5-flash)
            temperature: Sampling temperature (0.0-1.0)
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            **kwargs: Additional arguments for ChatGoogleGenerativeAI
        """
        self.model_name = model
        self.temperature = temperature
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Initialize LangChain Gemini chat model
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=self.api_key,
            convert_system_message_to_human=True,  # Gemini compatibility
            **kwargs
        )
    
    def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
        system_message: Optional[str] = None,
        **kwargs
    ) -> BaseModel:
        """
        Generate a structured response using Pydantic schema.
        
        Args:
            prompt: User prompt/query
            schema: Pydantic model class defining the output structure
            system_message: Optional system message for context
            **kwargs: Additional generation parameters
        
        Returns:
            Instance of the provided Pydantic schema with parsed data
        """
        # Create parser for the schema
        parser = PydanticOutputParser(pydantic_object=schema)
        
        # Build prompt with format instructions
        format_instructions = parser.get_format_instructions()
        
        # Create chat prompt template
        if system_message:
            template = ChatPromptTemplate.from_messages([
                ("system", system_message),
                ("human", "{prompt}\n\n{format_instructions}")
            ])
        else:
            template = ChatPromptTemplate.from_messages([
                ("human", "{prompt}\n\n{format_instructions}")
            ])
        
        # Format the prompt
        messages = template.format_messages(
            prompt=prompt,
            format_instructions=format_instructions
        )
        
        # Generate response
        response = self.llm.invoke(messages, **kwargs)
        
        # Parse the response
        try:
            # Ensure content is a string (AIMessage.content can be str or list)
            content = response.content if isinstance(response.content, str) else str(response.content)
            parsed = parser.parse(content)
            return parsed
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {e}\nResponse: {response.content}")
    
    def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate plain text response (non-structured).
        
        Args:
            prompt: User prompt/query
            system_message: Optional system message for context
            **kwargs: Additional generation parameters
        
        Returns:
            Generated text response
        """
        # Create chat prompt template
        if system_message:
            template = ChatPromptTemplate.from_messages([
                ("system", system_message),
                ("human", "{prompt}")
            ])
        else:
            template = ChatPromptTemplate.from_messages([
                ("human", "{prompt}")
            ])
        
        # Format the prompt
        messages = template.format_messages(prompt=prompt)
        
        # Generate response
        response = self.llm.invoke(messages, **kwargs)
        
        # Ensure content is a string (AIMessage.content can be str or list)
        content = response.content if isinstance(response.content, str) else str(response.content)
        return content
    
    def batch_generate_structured(
        self,
        prompts: list[str],
        schema: Type[BaseModel],
        system_message: Optional[str] = None,
        **kwargs
    ) -> list[BaseModel]:
        """
        Generate multiple structured responses in batch.
        
        Args:
            prompts: List of user prompts
            schema: Pydantic model class defining the output structure
            system_message: Optional system message for context
            **kwargs: Additional generation parameters
        
        Returns:
            List of parsed Pydantic schema instances
        """
        parser = PydanticOutputParser(pydantic_object=schema)
        format_instructions = parser.get_format_instructions()
        
        # Create chat prompt template
        if system_message:
            template = ChatPromptTemplate.from_messages([
                ("system", system_message),
                ("human", "{prompt}\n\n{format_instructions}")
            ])
        else:
            template = ChatPromptTemplate.from_messages([
                ("human", "{prompt}\n\n{format_instructions}")
            ])
        
        # Format all prompts - batch expects list of inputs, not list of list of messages
        from typing import cast
        from langchain_core.language_models import LanguageModelInput
        
        all_messages: list[LanguageModelInput] = [
            template.format_messages(
                prompt=prompt,
                format_instructions=format_instructions
            )
            for prompt in prompts
        ]
        
        # Batch generate
        responses = self.llm.batch(all_messages, **kwargs)
        
        # Parse all responses
        results = []
        for response in responses:
            try:
                # Ensure content is a string (AIMessage.content can be str or list)
                content = response.content if isinstance(response.content, str) else str(response.content)
                parsed = parser.parse(content)
                results.append(parsed)
            except Exception as e:
                raise ValueError(f"Failed to parse LLM response: {e}\nResponse: {response.content}")
        
        return results
    
    def __repr__(self) -> str:
        return f"GeminiStructuredLLM(model={self.model_name}, temperature={self.temperature})"


# Convenience function for quick instantiation
def create_gemini_llm(
    model: str = "gemini-2.5-flash",
    temperature: float = 0.2,
    **kwargs
) -> GeminiStructuredLLM:
    """
    Create a Gemini LLM instance with default settings.
    
    Args:
        model: Gemini model name
        temperature: Sampling temperature
        **kwargs: Additional arguments
    
    Returns:
        Configured GeminiStructuredLLM instance
    """
    return GeminiStructuredLLM(model=model, temperature=temperature, **kwargs)
