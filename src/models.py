"""
Data Models
Pydantic models for type safety and validation across the application.
Following best practices: immutable data structures, clear validation rules.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class MatchRecommendation(str, Enum):
    """Recommendation levels for candidate matching"""
    STRONG_MATCH = "Strong Match"
    MAYBE = "Maybe"
    WEAK_MATCH = "Weak Match"
    NOT_RECOMMENDED = "Not Recommended"


class ExperienceLevel(str, Enum):
    """Experience level classification"""
    ENTRY = "Entry Level"
    MID = "Mid Level"
    SENIOR = "Senior"
    LEAD = "Lead"
    EXECUTIVE = "Executive"


# Resume Data Models

class ContactInfo(BaseModel):
    """Contact information from resume"""
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None
    portfolio: Optional[str] = None


class Education(BaseModel):
    """Education entry"""
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    honors: List[str] = Field(default_factory=list)


class WorkExperience(BaseModel):
    """Work experience entry"""
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None  # None means current
    duration_months: Optional[int] = None
    description: Optional[str] = None  # Make optional to handle missing descriptions
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    
    @field_validator('description')
    @classmethod
    def set_default_description(cls, v, info):
        """Provide default description if None"""
        if v is None or v == "":
            return f"No description provided"
        return v


class Certification(BaseModel):
    """Professional certification"""
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None


class ParsedResume(BaseModel):
    """Complete parsed resume structure"""
    raw_text: str
    contact_info: ContactInfo
    summary: Optional[str] = None
    education: List[Education] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    total_experience_years: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('skills')
    @classmethod
    def deduplicate_skills(cls, v):
        """Remove duplicate skills (case-insensitive)"""
        seen = set()
        result = []
        for skill in v:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                result.append(skill)
        return result


# Job Description Models

class JobRequirement(BaseModel):
    """Single job requirement"""
    category: str  # e.g., "technical_skill", "experience", "education"
    requirement: str
    is_required: bool = True
    priority: int = Field(default=1, ge=1, le=3)  # 1=critical, 2=important, 3=nice-to-have


class ParsedJobDescription(BaseModel):
    """Complete parsed job description"""
    raw_text: str
    job_title: str
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None  # Full-time, Contract, etc.
    experience_level: Optional[ExperienceLevel] = None
    summary: str
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    requirements: List[JobRequirement] = Field(default_factory=list)
    min_experience_years: Optional[int] = None
    max_experience_years: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Matching Results Models

class SkillMatch(BaseModel):
    """Skill matching details"""
    skill: str
    match_type: str  # "exact", "similar", "missing"
    relevance_score: float = Field(ge=0.0, le=1.0)
    explanation: Optional[str] = None


class ScoreDimension(BaseModel):
    """Single scoring dimension with explanation"""
    dimension: str
    score: int = Field(ge=0, le=100)
    weight: float = Field(ge=0.0, le=1.0)
    explanation: str
    evidence: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)


class MatchResult(BaseModel):
    """Complete matching result"""
    resume_id: str
    job_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Overall scores
    overall_score: int = Field(ge=0, le=100)
    semantic_similarity: float = Field(ge=0.0, le=1.0)
    recommendation: MatchRecommendation
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Dimensional scores
    dimension_scores: List[ScoreDimension] = Field(default_factory=list)
    
    # Skills analysis
    matched_skills: List[SkillMatch] = Field(default_factory=list)
    missing_critical_skills: List[str] = Field(default_factory=list)
    
    # Detailed analysis
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    overall_reasoning: str
    
    # Bias & fairness
    bias_flags: List[str] = Field(default_factory=list)
    fairness_score: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Metadata
    processing_time_ms: float = 0.0
    llm_cost: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for export"""
        return {
            "resume_id": self.resume_id,
            "job_id": self.job_id,
            "timestamp": self.timestamp.isoformat(),
            "overall_score": self.overall_score,
            "recommendation": self.recommendation.value,
            "confidence": self.confidence,
            "semantic_similarity": self.semantic_similarity,
            "dimension_scores": [
                {
                    "dimension": d.dimension,
                    "score": d.score,
                    "weight": d.weight,
                    "explanation": d.explanation
                }
                for d in self.dimension_scores
            ],
            "matched_skills": len(self.matched_skills),
            "missing_critical_skills": self.missing_critical_skills,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "reasoning": self.overall_reasoning,
            "bias_flags": self.bias_flags,
            "processing_time_ms": self.processing_time_ms,
            "cost": self.llm_cost
        }


class BatchMatchResult(BaseModel):
    """Batch matching results"""
    job_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_resumes: int
    results: List[MatchResult] = Field(default_factory=list)
    aggregate_stats: Dict[str, Any] = Field(default_factory=dict)
    total_processing_time_ms: float = 0.0
    total_cost: float = 0.0
