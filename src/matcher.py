"""
Resume Matcher - Main Orchestrator
Unified interface for the complete matching pipeline.
"""

from typing import List, Optional, Union
from pathlib import Path

from .models import ParsedResume, ParsedJobDescription, MatchResult, BatchMatchResult
from .parsers import ResumeParser, JobDescriptionParser
from .scoring_engine import ScoringEngine
from config.settings import get_settings


class ResumeMatcher:
    """
    Main interface for resume matching system.
    Orchestrates parsing and matching.
    """
    
    def __init__(self):
        """Initialize matcher with all components"""
        self.resume_parser = ResumeParser()
        self.jd_parser = JobDescriptionParser()
        self.scoring_engine = ScoringEngine()
        self.settings = get_settings()
    
    def match_resume_to_job(
        self,
        resume: Union[str, Path, ParsedResume],
        job_description: Union[str, ParsedJobDescription],
        resume_id: str = "unknown",
        job_id: str = "unknown"
    ) -> MatchResult:
        """
        Complete matching pipeline for a single resume.
        
        Args:
            resume: Resume file path, text, or ParsedResume
            job_description: JD text or ParsedJobDescription
            resume_id: Identifier for resume
            job_id: Identifier for job
        
        Returns:
            MatchResult with complete analysis
        """
        # Step 1: Parse resume if needed
        if isinstance(resume, (str, Path)):
            if isinstance(resume, str) and not Path(resume).exists():
                # It's resume text, not a file
                parsed_resume = self.resume_parser.parse_text(resume)
            else:
                # It's a file path
                parsed_resume = self.resume_parser.parse_file(resume)
        else:
            parsed_resume = resume
        
        # Step 2: Parse job description if needed
        if isinstance(job_description, str):
            parsed_jd = self.jd_parser.parse_text(job_description)
        else:
            parsed_jd = job_description
        
        # Step 3: Run matching
        match_result = self.scoring_engine.score_candidate(
            resume=parsed_resume,
            job_description=parsed_jd,
            resume_id=resume_id,
            job_id=job_id
        )
        
        # Check if candidate was filtered out by semantic threshold
        if match_result is None:
            # Create a minimal result for rejected candidates
            from .models import MatchResult, MatchRecommendation
            match_result = MatchResult(
                resume_id=resume_id,
                job_id=job_id,
                overall_score=0,
                semantic_similarity=0.0,
                recommendation=MatchRecommendation.NOT_RECOMMENDED,
                confidence=0.1,
                strengths=[],
                weaknesses=["Semantic similarity below threshold - candidate does not meet basic requirements"],
                overall_reasoning="Candidate profile does not align with job requirements. Semantic match score too low.",
                metadata={
                    "rejected_by_semantic_filter": True,
                    "reason": "Below semantic similarity threshold"
                }
            )
        
        return match_result
    
    def match_multiple_resumes(
        self,
        resumes: List[Union[str, Path, ParsedResume]],
        job_description: Union[str, ParsedJobDescription],
        job_id: str = "unknown"
    ) -> BatchMatchResult:
        """
        Match multiple resumes against a single job description.
        
        Args:
            resumes: List of resume paths, texts, or ParsedResume objects
            job_description: JD text or ParsedJobDescription
            job_id: Job identifier
        
        Returns:
            BatchMatchResult with all match results
        """
        # Parse job description once
        if isinstance(job_description, str):
            parsed_jd = self.jd_parser.parse_text(job_description)
        else:
            parsed_jd = job_description
        
        # Process each resume
        results = []
        for i, resume in enumerate(resumes):
            resume_id = f"resume_{i}"
            
            try:
                match_result = self.match_resume_to_job(
                    resume=resume,
                    job_description=parsed_jd,
                    resume_id=resume_id,
                    job_id=job_id
                )
                results.append(match_result)
            except Exception as e:
                print(f"Error processing {resume_id}: {str(e)}")
                continue
        
        # Calculate aggregate stats
        total_time = sum(r.processing_time_ms for r in results)
        total_cost = sum(r.llm_cost for r in results)
        
        aggregate_stats = self.scoring_engine.get_aggregate_statistics(results)
        
        return BatchMatchResult(
            job_id=job_id,
            total_resumes=len(resumes),
            results=results,
            aggregate_stats=aggregate_stats,
            total_processing_time_ms=total_time,
            total_cost=total_cost
        )
    
    def get_skills_analysis(
        self,
        resume: Union[str, Path, ParsedResume],
        job_description: Union[str, ParsedJobDescription]
    ) -> dict:
        """Get detailed skills matching analysis"""
        # Parse if needed
        if not isinstance(resume, ParsedResume):
            if isinstance(resume, str) and not Path(resume).exists():
                parsed_resume = self.resume_parser.parse_text(resume)
            else:
                parsed_resume = self.resume_parser.parse_file(resume)
        else:
            parsed_resume = resume
        
        if isinstance(job_description, str):
            parsed_jd = self.jd_parser.parse_text(job_description)
        else:
            parsed_jd = job_description
        
        return self.scoring_engine.get_detailed_skills_analysis(
            parsed_resume, parsed_jd
        )
    

