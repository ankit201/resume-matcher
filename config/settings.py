"""
Application Configuration
Centralized settings management using Pydantic
"""

import os
from typing import Literal, Optional
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with validation and environment variable support.
    Following best practices: type safety, validation, and single source of truth.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Keys (only Gemini supported)
    google_api_key: str = Field(default="", description="Google AI API key")
    
    # Model Configuration
    gemini_model: str = Field(default="gemini-2.5-flash", description="Gemini model")
    
    # Application Settings
    environment: Literal["development", "production", "staging"] = Field(default="development")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    max_retries: int = Field(default=3, ge=1, le=10)
    timeout_seconds: int = Field(default=60, ge=10, le=300)
    
    # Matching Configuration
    semantic_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Min cosine similarity")
    min_match_score: int = Field(default=60, ge=0, le=100, description="Minimum overall match score")
    
    # Scoring Weights (must sum to 1.0)
    weight_technical_skills: float = Field(default=0.30, ge=0.0, le=1.0)
    weight_experience: float = Field(default=0.30, ge=0.0, le=1.0)
    weight_education: float = Field(default=0.15, ge=0.0, le=1.0)
    weight_cultural_fit: float = Field(default=0.15, ge=0.0, le=1.0)
    weight_growth_potential: float = Field(default=0.10, ge=0.0, le=1.0)
    
    # Cost Tracking
    track_costs: bool = Field(default=True)
    gemini_cost_per_1k_input: float = Field(default=0.00)  # Flash tier is free
    gemini_cost_per_1k_output: float = Field(default=0.00)
    
    # Embedding Model
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    
    # Vector Store Configuration
    vector_store_path: str = Field(default="./data/vector_store", description="ChromaDB persistence directory")
    vector_store_collection: str = Field(default="resumes", description="Collection name for resumes")
    
    # Vendor Comparison Baseline (for ROI calculation)
    baseline_vendor_annual_cost: float = Field(default=2_000_000.0)
    baseline_vendor_false_rejection_rate: float = Field(default=0.40)
    baseline_vendor_avg_time_to_shortlist_days: int = Field(default=21)
    
    @field_validator("weight_technical_skills", "weight_experience", "weight_education", 
                     "weight_cultural_fit", "weight_growth_potential")
    @classmethod
    def validate_weights(cls, v, info):
        """Ensure all weights are valid percentages"""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Weight must be between 0.0 and 1.0, got {v}")
        return v
    
    def validate_weights_sum(self) -> bool:
        """Validate that all scoring weights sum to 1.0"""
        total = (
            self.weight_technical_skills +
            self.weight_experience +
            self.weight_education +
            self.weight_cultural_fit +
            self.weight_growth_potential
        )
        if not 0.99 <= total <= 1.01:  # Allow small floating point error
            raise ValueError(f"Scoring weights must sum to 1.0, got {total}")
        return True
    
    def get_scoring_weights(self) -> dict[str, float]:
        """Return scoring weights as a dictionary"""
        return {
            "technical_skills": self.weight_technical_skills,
            "experience": self.weight_experience,
            "education": self.weight_education,
            "cultural_fit": self.weight_cultural_fit,
            "growth_potential": self.weight_growth_potential,
        }


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures singleton pattern for settings.
    """
    settings = Settings()
    settings.validate_weights_sum()
    return settings


# Convenience function for checking if running in production
def is_production() -> bool:
    """Check if application is running in production environment"""
    return get_settings().environment == "production"
