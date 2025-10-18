"""
LLM-Based Deep Matching Engine
Uses Gemini for sophisticated resume evaluation with explainability.
Provides multi-dimensional scoring with detailed reasoning.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import (
    ParsedResume, ParsedJobDescription, MatchResult, ScoreDimension,
    SkillMatch, MatchRecommendation
)
from .llm_adapters.factory import LLMFactory
from .llm_adapters.base import LLMResponse
from config.settings import get_settings


class LLMMatcher:
    """
    Deep matching engine using LLM for nuanced evaluation.
    Provides explainable, multi-dimensional candidate assessment.
    """
    
    def __init__(self):
        """Initialize matcher with Gemini"""
        self.llm = LLMFactory.get_default_adapter()  # Gemini 2.5 Flash
        self.settings = get_settings()
        self.scoring_weights = self.settings.get_scoring_weights()
    
    def evaluate_match(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription,
        semantic_similarity: float,
        resume_id: str = "unknown",
        job_id: str = "unknown"
    ) -> MatchResult:
        """
        Perform comprehensive resume evaluation.
        
        Args:
            resume: Parsed resume
            job_description: Parsed job description
            semantic_similarity: Pre-computed semantic similarity score
            resume_id: Identifier for the resume
            job_id: Identifier for the job
        
        Returns:
            Complete MatchResult with scores and explanations
        """
        start_time = datetime.utcnow()
        
        # Run dimensional evaluation and skills analysis in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks
            dimensions_future = executor.submit(
                self._evaluate_dimensions, resume, job_description
            )
            skills_future = executor.submit(
                self._analyze_skills, resume, job_description
            )
            
            # Get results
            dimension_scores = dimensions_future.result()
            skills_analysis = skills_future.result()
        
        # Calculate overall score (weighted average)
        overall_score = self._calculate_weighted_score(dimension_scores)
        
        # Generate overall reasoning (depends on dimensions and skills, so must run after)
        overall_reasoning = self._generate_overall_reasoning(
            resume, job_description, dimension_scores, skills_analysis
        )
        
        # Determine recommendation
        recommendation = self._determine_recommendation(overall_score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(dimension_scores, semantic_similarity)
        
        # Extract strengths and weaknesses
        strengths, weaknesses = self._extract_strengths_weaknesses(dimension_scores)
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return MatchResult(
            resume_id=resume_id,
            job_id=job_id,
            overall_score=overall_score,
            semantic_similarity=semantic_similarity,
            recommendation=recommendation,
            confidence=confidence,
            dimension_scores=dimension_scores,
            matched_skills=skills_analysis["matches"],
            missing_critical_skills=skills_analysis["missing_critical"],
            strengths=strengths,
            weaknesses=weaknesses,
            overall_reasoning=overall_reasoning,
            processing_time_ms=processing_time,
            llm_cost=self._accumulated_cost
        )
    
    def _evaluate_dimensions(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> List[ScoreDimension]:
        """
        Evaluate all scoring dimensions using LLM in parallel.
        
        Returns:
            List of ScoreDimension objects with scores and explanations
        """
        self._accumulated_cost = 0.0
        
        # Define evaluation tasks
        evaluation_tasks = [
            ("technical", self._evaluate_technical_skills),
            ("experience", self._evaluate_experience),
            ("education", self._evaluate_education),
            ("cultural", self._evaluate_cultural_fit),
            ("growth", self._evaluate_growth_potential)
        ]
        
        # Execute all evaluations in parallel
        dimensions_dict = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            future_to_dimension = {
                executor.submit(func, resume, job_description): name
                for name, func in evaluation_tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_dimension):
                dimension_name = future_to_dimension[future]
                try:
                    dimension_score = future.result()
                    dimensions_dict[dimension_name] = dimension_score
                except Exception as e:
                    print(f"❌ Error evaluating {dimension_name}: {e}")
                    # Create fallback dimension
                    dimensions_dict[dimension_name] = ScoreDimension(
                        dimension=dimension_name.title(),
                        score=0,
                        weight=0.2,
                        explanation=f"Evaluation failed: {str(e)}",
                        evidence=[],
                        gaps=["Evaluation error"]
                    )
        
        # Return dimensions in original order
        dimensions = [
            dimensions_dict["technical"],
            dimensions_dict["experience"],
            dimensions_dict["education"],
            dimensions_dict["cultural"],
            dimensions_dict["growth"]
        ]
        
        return dimensions
    
    def _evaluate_technical_skills(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> ScoreDimension:
        """Evaluate technical skills match"""
        
        system_prompt = """You are an expert technical recruiter evaluating candidate skills.
Provide objective, evidence-based assessment. Score from 0-100."""
        
        user_prompt = f"""Evaluate the technical skills match between candidate and job requirements.

**Job Title:** {job_description.job_title}

**Required Technical Skills:**
{', '.join(job_description.required_skills)}

**Preferred Technical Skills:**
{', '.join(job_description.preferred_skills) if job_description.preferred_skills else 'None specified'}

**Candidate's Skills:**
{', '.join(resume.skills) if resume.skills else 'None listed'}

**Candidate's Technical Experience:**
{self._format_experience_for_prompt(resume)}

Provide a JSON response with:
{{
    "score": <0-100>,
    "explanation": "<2-3 sentences explaining the score>",
    "evidence": ["<specific matching skills>", "<relevant experience>"],
    "gaps": ["<missing critical skills>"]
}}"""
        
        response: LLMResponse = self.llm.generate_structured(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        self._accumulated_cost += response.cost
        
        # Debug: print response content
        if not response.content or not response.content.strip():
            print(f"⚠️ Empty response from LLM for technical skills")
            print(f"Response metadata: {response.metadata}")
            # Return default score
            return ScoreDimension(
                dimension="Technical Skills",
                score=0,
                weight=self.scoring_weights["technical_skills"],
                explanation="Failed to evaluate technical skills due to empty LLM response",
                evidence=[],
                gaps=["Evaluation failed"]
            )
        
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error for technical skills: {e}")
            print(f"Response content (first 500 chars): {response.content[:500]}")
            # Return default score
            return ScoreDimension(
                dimension="Technical Skills",
                score=0,
                weight=self.scoring_weights["technical_skills"],
                explanation="Failed to parse LLM response as JSON",
                evidence=[],
                gaps=["Evaluation failed - invalid JSON response"]
            )
        
        return ScoreDimension(
            dimension="Technical Skills",
            score=result.get("score", 0),
            weight=self.scoring_weights["technical_skills"],
            explanation=result.get("explanation", "No explanation provided"),
            evidence=result.get("evidence", []),
            gaps=result.get("gaps", [])
        )
    
    def _evaluate_experience(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> ScoreDimension:
        """Evaluate experience relevance"""
        
        system_prompt = """You are an expert at evaluating work experience relevance.
Consider: role similarity, industry relevance, responsibilities alignment, career progression."""
        
        user_prompt = f"""Evaluate experience relevance for this job.

**Job Requirements:**
- Title: {job_description.job_title}
- Experience Required: {job_description.min_experience_years}-{job_description.max_experience_years} years
- Key Responsibilities: {' '.join(job_description.responsibilities[:3])}

**Candidate's Experience:**
- Total Years: {resume.total_experience_years or 'Not specified'}
- Recent Roles:
{self._format_experience_for_prompt(resume, limit=3)}

Provide JSON response:
{{
    "score": <0-100>,
    "explanation": "<assessment of experience relevance>",
    "evidence": ["<relevant roles and achievements>"],
    "gaps": ["<experience gaps or concerns>"]
}}"""
        
        response: LLMResponse = self.llm.generate_structured(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        self._accumulated_cost += response.cost
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Response (first 1000): {response.content[:1000]}")
            result = {"score": 0, "explanation": "JSON parsing failed", "evidence": [], "gaps": ["Evaluation failed"]}
        
        return ScoreDimension(
            dimension="Experience Relevance",
            score=result["score"],
            weight=self.scoring_weights["experience"],
            explanation=result["explanation"],
            evidence=result.get("evidence", []),
            gaps=result.get("gaps", [])
        )
    
    def _evaluate_education(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> ScoreDimension:
        """Evaluate education and certifications"""
        
        system_prompt = """Evaluate educational qualifications and certifications.
Consider: degree relevance, institution quality, certifications, continuous learning."""
        
        education_text = "\n".join([
            f"- {e.degree} in {e.field_of_study or 'N/A'} from {e.institution} ({e.graduation_year or 'N/A'})"
            for e in resume.education
        ]) if resume.education else "None specified"
        
        certs_text = "\n".join([
            f"- {c.name} from {c.issuer}"
            for c in resume.certifications
        ]) if resume.certifications else "None specified"
        
        user_prompt = f"""Evaluate educational qualifications.

**Job Requirements:**
{', '.join(job_description.education_requirements) if job_description.education_requirements else 'Not specified'}

**Candidate's Education:**
{education_text}

**Certifications:**
{certs_text}

Provide JSON response:
{{
    "score": <0-100>,
    "explanation": "<education assessment>",
    "evidence": ["<relevant degrees/certifications>"],
    "gaps": ["<missing requirements>"]
}}"""
        
        response: LLMResponse = self.llm.generate_structured(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        self._accumulated_cost += response.cost
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Response (first 1000): {response.content[:1000]}")
            result = {"score": 0, "explanation": "JSON parsing failed", "evidence": [], "gaps": ["Evaluation failed"]}
        
        return ScoreDimension(
            dimension="Education & Certifications",
            score=result["score"],
            weight=self.scoring_weights["education"],
            explanation=result["explanation"],
            evidence=result.get("evidence", []),
            gaps=result.get("gaps", [])
        )
    
    def _evaluate_cultural_fit(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> ScoreDimension:
        """Evaluate cultural fit and soft skills"""
        
        system_prompt = """Assess cultural fit based on work style, collaboration indicators, and soft skills.
Look for: leadership, teamwork, communication, adaptability, problem-solving."""
        
        user_prompt = f"""Evaluate cultural fit and soft skills.

**Job Context:**
{job_description.summary}

**Candidate's Profile:**
Summary: {resume.summary or 'Not provided'}
Achievements: {self._extract_achievements(resume)}

Provide JSON response:
{{
    "score": <0-100>,
    "explanation": "<cultural fit assessment>",
    "evidence": ["<positive indicators>"],
    "gaps": ["<potential concerns>"]
}}"""
        
        response: LLMResponse = self.llm.generate_structured(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        self._accumulated_cost += response.cost
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Response (first 1000): {response.content[:1000]}")
            result = {"score": 0, "explanation": "JSON parsing failed", "evidence": [], "gaps": ["Evaluation failed"]}
        
        return ScoreDimension(
            dimension="Cultural Fit",
            score=result["score"],
            weight=self.scoring_weights["cultural_fit"],
            explanation=result["explanation"],
            evidence=result.get("evidence", []),
            gaps=result.get("gaps", [])
        )
    
    def _evaluate_growth_potential(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> ScoreDimension:
        """Evaluate growth potential and career trajectory"""
        
        system_prompt = """Assess candidate's growth potential and career trajectory.
Consider: career progression, learning agility, skill development, role transitions."""
        
        user_prompt = f"""Evaluate growth potential.

**Candidate's Career Progression:**
{self._format_experience_for_prompt(resume)}

**Certifications & Recent Learning:**
{', '.join([c.name for c in resume.certifications]) if resume.certifications else 'None'}

Provide JSON response:
{{
    "score": <0-100>,
    "explanation": "<growth potential assessment>",
    "evidence": ["<indicators of growth>"],
    "gaps": ["<concerns about stagnation>"]
}}"""
        
        response: LLMResponse = self.llm.generate_structured(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        self._accumulated_cost += response.cost
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Response (first 1000): {response.content[:1000]}")
            result = {"score": 0, "explanation": "JSON parsing failed", "evidence": [], "gaps": ["Evaluation failed"]}
        
        return ScoreDimension(
            dimension="Growth Potential",
            score=result["score"],
            weight=self.scoring_weights["growth_potential"],
            explanation=result["explanation"],
            evidence=result.get("evidence", []),
            gaps=result.get("gaps", [])
        )
    
    def _analyze_skills(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> Dict[str, Any]:
        """Detailed skills analysis using LLM for intelligent matching"""
        
        system_prompt = """You are an expert technical recruiter analyzing candidate skills.
Your task is to match candidate skills against job requirements intelligently.
Consider semantic similarity, related technologies, and skill equivalence.

Return a JSON object with this structure:
{
  "matched_skills": [
    {
      "skill": "Required skill from JD",
      "match_type": "exact|similar|related",
      "relevance_score": 0.0-1.0,
      "explanation": "Brief explanation of the match"
    }
  ],
  "missing_critical": ["List of critical required skills not found in resume"]
}

Match types:
- exact: Direct match (e.g., "Python" matches "Python")
- similar: Very close match (e.g., "PyTorch" matches "TensorFlow")
- related: Related but not equivalent (e.g., "Keras" matches "Deep Learning frameworks")

Only include matches with relevance_score >= 0.6. Be strict but fair."""

        user_prompt = f"""Analyze skill matching between candidate and job requirements.

**Candidate Skills:**
{', '.join(resume.skills) if resume.skills else 'None listed'}

**Job Required Skills:**
{chr(10).join(f"- {skill}" for skill in job_description.required_skills)}

**Job Preferred Skills:**
{chr(10).join(f"- {skill}" for skill in job_description.preferred_skills) if job_description.preferred_skills else 'None'}

Provide intelligent skill matching. Consider:
1. Direct technology matches
2. Framework equivalents (e.g., PyTorch vs TensorFlow)
3. Skill categories (e.g., "Python" covers "Python development")
4. Experience descriptions that imply skills

Return JSON only, no additional text."""

        try:
            response: LLMResponse = self.llm.generate_structured(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            self._accumulated_cost += response.cost
            
            # Parse JSON response
            result = json.loads(response.content)
            
            # Parse LLM response
            matches = []
            for skill_data in result.get("matched_skills", []):
                matches.append(SkillMatch(
                    skill=skill_data["skill"],
                    match_type=skill_data["match_type"],
                    relevance_score=float(skill_data["relevance_score"]),
                    explanation=skill_data["explanation"]
                ))
            
            missing_critical = result.get("missing_critical", [])
            
            return {
                "matches": matches,
                "missing_critical": missing_critical
            }
            
        except Exception as e:
            # Fallback to simple matching if LLM fails
            print(f"Warning: LLM skill matching failed ({e}), using fallback")
            matches = []
            missing_critical = []
            
            # Simple fallback: case-insensitive substring matching
            resume_skills_text = " ".join(resume.skills).lower()
            
            for req_skill in job_description.required_skills:
                req_skill_lower = req_skill.lower()
                found = False
                
                # Check if any part of the requirement is in resume skills
                for resume_skill in resume.skills:
                    if (req_skill_lower in resume_skill.lower() or 
                        resume_skill.lower() in req_skill_lower):
                        matches.append(SkillMatch(
                            skill=req_skill,
                            match_type="similar",
                            relevance_score=0.7,
                            explanation=f"Matches '{resume_skill}'"
                        ))
                        found = True
                        break
                
                if not found:
                    missing_critical.append(req_skill)
            
            return {
                "matches": matches,
                "missing_critical": missing_critical
            }
    
    def _generate_overall_reasoning(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription,
        dimension_scores: List[ScoreDimension],
        skills_analysis: Dict[str, Any]
    ) -> str:
        """Generate comprehensive reasoning for the match"""
        
        # Create summary of scores
        scores_summary = "\n".join([
            f"- {d.dimension}: {d.score}/100 - {d.explanation}"
            for d in dimension_scores
        ])
        
        system_prompt = """Synthesize an overall hiring recommendation.
Be specific, balanced, and actionable. Write 2-3 paragraphs."""
        
        user_prompt = f"""Generate overall matching analysis.

**Job:** {job_description.job_title}

**Dimensional Scores:**
{scores_summary}

**Skills Match:**
- Matched: {len(skills_analysis['matches'])} required skills
- Missing: {len(skills_analysis['missing_critical'])} required skills

Provide a concise overall assessment (2-3 paragraphs) explaining whether this candidate should be considered and why."""
        
        response: LLMResponse = self.llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        self._accumulated_cost += response.cost
        
        return response.content
    
    def _calculate_weighted_score(self, dimension_scores: List[ScoreDimension]) -> int:
        """Calculate weighted overall score"""
        total = sum(d.score * d.weight for d in dimension_scores)
        return int(round(total))
    
    def _determine_recommendation(self, overall_score: int) -> MatchRecommendation:
        """Determine recommendation based on score"""
        if overall_score >= 80:
            return MatchRecommendation.STRONG_MATCH
        elif overall_score >= 60:
            return MatchRecommendation.MAYBE
        elif overall_score >= 40:
            return MatchRecommendation.WEAK_MATCH
        else:
            return MatchRecommendation.NOT_RECOMMENDED
    
    def _calculate_confidence(
        self,
        dimension_scores: List[ScoreDimension],
        semantic_similarity: float
    ) -> float:
        """Calculate confidence in the recommendation"""
        # Higher confidence when scores are consistent and semantic similarity aligns
        scores = [d.score for d in dimension_scores]
        score_variance = float(np.var(scores))
        
        # Low variance = high confidence
        variance_factor = 1.0 - min(score_variance / 1000, 0.3)
        
        # Semantic similarity alignment
        avg_score = float(np.mean(scores)) / 100
        semantic_alignment = 1.0 - abs(avg_score - semantic_similarity)
        
        confidence = (variance_factor * 0.6 + semantic_alignment * 0.4)
        return float(min(max(confidence, 0.0), 1.0))
    
    def _extract_strengths_weaknesses(
        self,
        dimension_scores: List[ScoreDimension]
    ) -> tuple[List[str], List[str]]:
        """Extract strengths and weaknesses from dimensional analysis"""
        strengths = []
        weaknesses = []
        
        for dimension in dimension_scores:
            if dimension.score >= 75:
                strengths.extend(dimension.evidence[:2])  # Top 2 evidence items
            elif dimension.score < 60:
                weaknesses.extend(dimension.gaps[:2])  # Top 2 gaps
        
        return strengths[:5], weaknesses[:5]  # Limit to top 5 each
    
    def _format_experience_for_prompt(
        self,
        resume: ParsedResume,
        limit: Optional[int] = None
    ) -> str:
        """Format work experience for prompts"""
        experiences = resume.work_experience[:limit] if limit else resume.work_experience
        
        formatted = []
        for exp in experiences:
            exp_str = f"- {exp.title} at {exp.company}"
            if exp.duration_months:
                years = exp.duration_months // 12
                months = exp.duration_months % 12
                exp_str += f" ({years}y {months}m)"
            if exp.description:
                exp_str += f": {exp.description[:200]}"
            if exp.technologies:
                exp_str += f" | Tech: {', '.join(exp.technologies[:5])}"
            formatted.append(exp_str)
        
        return "\n".join(formatted) if formatted else "No experience listed"
    
    def _extract_achievements(self, resume: ParsedResume) -> str:
        """Extract key achievements from resume"""
        achievements = []
        for exp in resume.work_experience:
            achievements.extend(exp.achievements[:2])
        return "; ".join(achievements[:5]) if achievements else "None specified"


# Import numpy for calculations
import numpy as np
