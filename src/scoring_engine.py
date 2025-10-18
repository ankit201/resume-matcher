"""
Scoring & Recommendation Engine
Combines semantic and LLM-based scores for final candidate ranking.
Provides unified interface for complete matching pipeline.
"""

import time
from typing import List, Optional
from datetime import datetime

from .models import ParsedResume, ParsedJobDescription, MatchResult
from .semantic_matcher import SemanticMatcher
from .llm_matcher import LLMMatcher
from config.settings import get_settings


class ScoringEngine:
    """
    Unified scoring engine that orchestrates the complete matching pipeline.
    Combines fast semantic matching with deep LLM analysis.
    """
    
    def __init__(self):
        """Initialize scoring engine with matchers"""
        self.semantic_matcher = SemanticMatcher()
        self.llm_matcher = LLMMatcher()
        self.settings = get_settings()
    
    def score_candidate(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription,
        resume_id: str = "unknown",
        job_id: str = "unknown",
        use_semantic_filter: bool = True
    ) -> Optional[MatchResult]:
        """
        Complete candidate scoring pipeline.
        
        Args:
            resume: Parsed resume
            job_description: Parsed job description
            resume_id: Resume identifier
            job_id: Job identifier
            use_semantic_filter: Whether to pre-filter with semantic threshold
        
        Returns:
            MatchResult if candidate passes filters, None otherwise
        """
        start_time = time.time()
        
        # Step 1: Semantic similarity (fast filtering)
        semantic_score = self.semantic_matcher.compute_overall_similarity(
            resume, job_description
        )
        
        # Early rejection if below threshold
        if use_semantic_filter and semantic_score < self.settings.semantic_threshold:
            return None
        
        # Step 2: Deep LLM analysis
        match_result = self.llm_matcher.evaluate_match(
            resume=resume,
            job_description=job_description,
            semantic_similarity=semantic_score,
            resume_id=resume_id,
            job_id=job_id
        )
        
        # Update processing time
        total_time = (time.time() - start_time) * 1000
        match_result.processing_time_ms = total_time
        
        # Add semantic analysis to metadata
        match_result.metadata.update({
            "semantic_similarity": semantic_score,
            "passed_semantic_filter": semantic_score >= self.settings.semantic_threshold
        })
        
        return match_result
    
    def score_batch(
        self,
        resumes: List[ParsedResume],
        job_description: ParsedJobDescription,
        job_id: str = "unknown",
        use_semantic_filter: bool = True,
        top_k: Optional[int] = None
    ) -> List[MatchResult]:
        """
        Score multiple candidates efficiently.
        
        Args:
            resumes: List of parsed resumes
            job_description: Job description
            job_id: Job identifier
            use_semantic_filter: Whether to use semantic pre-filtering
            top_k: Return only top K candidates (None = all)
        
        Returns:
            List of MatchResults, sorted by score descending
        """
        results = []
        
        # Step 1: Batch semantic scoring for efficiency
        if use_semantic_filter:
            semantic_results = self.semantic_matcher.batch_compute_similarities(
                resumes, job_description
            )
            
            # Filter by threshold
            candidates_to_process = [
                (idx, score) for idx, score in semantic_results
                if score >= self.settings.semantic_threshold
            ]
            
            # Limit to top_k if specified
            if top_k:
                candidates_to_process = candidates_to_process[:top_k]
        else:
            # Process all candidates
            candidates_to_process = [(i, 0.0) for i in range(len(resumes))]
        
        # Step 2: Deep LLM analysis for filtered candidates
        for idx, semantic_score in candidates_to_process:
            resume = resumes[idx]
            resume_id = f"resume_{idx}"
            
            match_result = self.llm_matcher.evaluate_match(
                resume=resume,
                job_description=job_description,
                semantic_similarity=semantic_score,
                resume_id=resume_id,
                job_id=job_id
            )
            
            results.append(match_result)
        
        # Sort by overall score
        results.sort(key=lambda x: x.overall_score, reverse=True)
        
        return results
    
    def get_detailed_skills_analysis(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> dict:
        """
        Get detailed skills matching analysis.
        
        Args:
            resume: Parsed resume
            job_description: Parsed job description
        
        Returns:
            Dictionary with detailed skills analysis
        """
        skill_matches = self.semantic_matcher.compute_skills_match(
            resume, job_description
        )
        
        # Categorize matches
        exact_matches = [sm for sm in skill_matches if sm.match_type == "exact"]
        similar_matches = [sm for sm in skill_matches if sm.match_type == "similar"]
        missing_skills = [sm for sm in skill_matches if sm.match_type == "missing"]
        
        # Calculate match percentage
        total_required = len(job_description.required_skills)
        matched_required = len([
            sm for sm in exact_matches + similar_matches
            if sm.skill in job_description.required_skills
        ])
        
        match_percentage = (matched_required / total_required * 100) if total_required > 0 else 0
        
        return {
            "exact_matches": exact_matches,
            "similar_matches": similar_matches,
            "missing_skills": missing_skills,
            "match_percentage": match_percentage,
            "total_required_skills": total_required,
            "matched_required_skills": matched_required,
            "summary": {
                "exact": len(exact_matches),
                "similar": len(similar_matches),
                "missing": len(missing_skills)
            }
        }
    
    def get_experience_analysis(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> dict:
        """
        Get detailed experience relevance analysis.
        
        Args:
            resume: Parsed resume
            job_description: Parsed job description
        
        Returns:
            Dictionary with experience analysis
        """
        relevance_metrics = self.semantic_matcher.compute_experience_relevance(
            resume, job_description
        )
        
        # Add experience level matching
        experience_level_match = self._check_experience_level_match(
            resume, job_description
        )
        
        return {
            **relevance_metrics,
            "experience_level_match": experience_level_match,
            "total_years": resume.total_experience_years,
            "required_years": {
                "min": job_description.min_experience_years,
                "max": job_description.max_experience_years
            }
        }
    
    def get_section_analysis(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> dict:
        """
        Get section-by-section similarity analysis.
        
        Args:
            resume: Parsed resume
            job_description: Parsed job description
        
        Returns:
            Dictionary with section similarities
        """
        return self.semantic_matcher.compute_section_similarities(
            resume, job_description
        )
    
    def _check_experience_level_match(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> dict:
        """Check if candidate's experience level matches requirements"""
        total_years = resume.total_experience_years or 0
        min_required = job_description.min_experience_years or 0
        max_required = job_description.max_experience_years or 999
        
        is_match = min_required <= total_years <= max_required
        
        if total_years < min_required:
            status = "underqualified"
            gap = min_required - total_years
        elif total_years > max_required:
            status = "overqualified"
            gap = total_years - max_required
        else:
            status = "match"
            gap = 0
        
        return {
            "is_match": is_match,
            "status": status,
            "gap_years": gap,
            "candidate_years": total_years,
            "required_range": f"{min_required}-{max_required}"
        }
    
    def rank_candidates(
        self,
        match_results: List[MatchResult],
        sort_by: str = "overall_score"
    ) -> List[MatchResult]:
        """
        Rank and sort candidates by specified criterion.
        
        Args:
            match_results: List of match results
            sort_by: Sorting criterion (overall_score, semantic_similarity, confidence)
        
        Returns:
            Sorted list of match results
        """
        if sort_by == "overall_score":
            return sorted(match_results, key=lambda x: x.overall_score, reverse=True)
        elif sort_by == "semantic_similarity":
            return sorted(match_results, key=lambda x: x.semantic_similarity, reverse=True)
        elif sort_by == "confidence":
            return sorted(match_results, key=lambda x: x.confidence, reverse=True)
        else:
            raise ValueError(f"Invalid sort criterion: {sort_by}")
    
    def filter_by_recommendation(
        self,
        match_results: List[MatchResult],
        min_recommendation: str = "Maybe"
    ) -> List[MatchResult]:
        """
        Filter candidates by minimum recommendation level.
        
        Args:
            match_results: List of match results
            min_recommendation: Minimum recommendation (Strong Match, Maybe, Weak Match)
        
        Returns:
            Filtered list of match results
        """
        recommendation_order = {
            "Strong Match": 3,
            "Maybe": 2,
            "Weak Match": 1,
            "Not Recommended": 0
        }
        
        min_level = recommendation_order.get(min_recommendation, 0)
        
        return [
            result for result in match_results
            if recommendation_order.get(result.recommendation.value, 0) >= min_level
        ]
    
    def get_aggregate_statistics(
        self,
        match_results: List[MatchResult]
    ) -> dict:
        """
        Calculate aggregate statistics for a batch of results.
        
        Args:
            match_results: List of match results
        
        Returns:
            Dictionary with aggregate statistics
        """
        if not match_results:
            return {}
        
        scores = [r.overall_score for r in match_results]
        confidences = [r.confidence for r in match_results]
        semantic_scores = [r.semantic_similarity for r in match_results]
        
        # Count by recommendation
        recommendations = {}
        for result in match_results:
            rec = result.recommendation.value
            recommendations[rec] = recommendations.get(rec, 0) + 1
        
        # Total cost and time
        total_cost = sum(r.llm_cost for r in match_results)
        total_time = sum(r.processing_time_ms for r in match_results)
        
        return {
            "total_candidates": len(match_results),
            "score_statistics": {
                "mean": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
                "median": sorted(scores)[len(scores) // 2]
            },
            "confidence_statistics": {
                "mean": sum(confidences) / len(confidences),
                "min": min(confidences),
                "max": max(confidences)
            },
            "semantic_statistics": {
                "mean": sum(semantic_scores) / len(semantic_scores),
                "min": min(semantic_scores),
                "max": max(semantic_scores)
            },
            "recommendations_breakdown": recommendations,
            "total_processing_time_ms": total_time,
            "avg_processing_time_ms": total_time / len(match_results),
            "total_cost_usd": total_cost,
            "avg_cost_per_candidate": total_cost / len(match_results)
        }
