"""
Report Generator
Generate formatted reports for different stakeholders.
"""

import json
from typing import List, Dict, Optional
from datetime import datetime
from ..models import MatchResult, BatchMatchResult


class ReportGenerator:
    """Generate formatted reports for stakeholders"""
    
    @staticmethod
    def generate_executive_summary(
        match_results: List[MatchResult],
        job_title: str = "Position"
    ) -> str:
        """
        Generate executive summary report.
        
        Args:
            match_results: List of match results
            job_title: Job title
        
        Returns:
            Formatted text report
        """
        if not match_results:
            return "No candidates processed."
        
        # Calculate key metrics
        total = len(match_results)
        strong = sum(1 for r in match_results if r.recommendation.value == "Strong Match")
        maybe = sum(1 for r in match_results if r.recommendation.value == "Maybe")
        avg_score = sum(r.overall_score for r in match_results) / total
        
        report = f"""
# EXECUTIVE SUMMARY - {job_title}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## KEY METRICS
- **Total Candidates Screened:** {total}
- **Strong Matches:** {strong} ({strong/total*100:.1f}%)
- **Qualified Candidates:** {strong + maybe} ({(strong+maybe)/total*100:.1f}%)
- **Average Quality Score:** {avg_score:.1f}/100

## TOP CANDIDATES
"""
        
        # List top 5 candidates
        top_candidates = sorted(match_results, key=lambda x: x.overall_score, reverse=True)[:5]
        for i, candidate in enumerate(top_candidates, 1):
            report += f"\n{i}. **{candidate.resume_id}** - Score: {candidate.overall_score}/100"
            report += f"\n   - Recommendation: {candidate.recommendation.value}"
            report += f"\n   - Key Strength: {candidate.strengths[0] if candidate.strengths else 'N/A'}"
            report += "\n"
        
        report += f"""
## RECOMMENDATION
- **Proceed to interview:** {strong} strong candidates
- **Secondary review:** {maybe} qualified candidates
- **Average processing time:** {sum(r.processing_time_ms for r in match_results) / total / 1000:.2f} seconds per candidate

## NEXT STEPS
1. Schedule interviews with top {min(strong, 3)} candidates
2. Review "Maybe" candidates for specific skill development needs
3. Maintain pipeline with remaining qualified candidates
"""
        
        return report
    
    @staticmethod
    def generate_candidate_report(
        match_result: MatchResult,
        detailed: bool = True
    ) -> str:
        """
        Generate individual candidate evaluation report.
        
        Args:
            match_result: Match result for candidate
            detailed: Include detailed analysis
        
        Returns:
            Formatted text report
        """
        report = f"""
# CANDIDATE EVALUATION REPORT
Candidate ID: {match_result.resume_id}
Job ID: {match_result.job_id}
Evaluated: {match_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## OVERALL ASSESSMENT
**Recommendation:** {match_result.recommendation.value}
**Overall Score:** {match_result.overall_score}/100
**Confidence:** {match_result.confidence*100:.1f}%
**Semantic Match:** {match_result.semantic_similarity*100:.1f}%

## DIMENSIONAL SCORES
"""
        
        for dimension in match_result.dimension_scores:
            report += f"\n### {dimension.dimension} ({dimension.score}/100)\n"
            report += f"**Weight:** {dimension.weight*100:.0f}%\n"
            report += f"**Analysis:** {dimension.explanation}\n"
            
            if detailed and dimension.evidence:
                report += f"**Evidence:**\n"
                for evidence in dimension.evidence[:3]:
                    report += f"- {evidence}\n"
            
            if detailed and dimension.gaps:
                report += f"**Gaps:**\n"
                for gap in dimension.gaps[:3]:
                    report += f"- {gap}\n"
            
            report += "\n"
        
        report += f"""
## KEY STRENGTHS
"""
        for strength in match_result.strengths[:5]:
            report += f"- {strength}\n"
        
        if match_result.weaknesses:
            report += f"""
## AREAS FOR DEVELOPMENT
"""
            for weakness in match_result.weaknesses[:5]:
                report += f"- {weakness}\n"
        
        if match_result.missing_critical_skills:
            report += f"""
## MISSING CRITICAL SKILLS
"""
            for skill in match_result.missing_critical_skills:
                report += f"- {skill}\n"
        
        report += f"""
## DETAILED REASONING
{match_result.overall_reasoning}

## METADATA
- Processing Time: {match_result.processing_time_ms:.0f}ms
- Cost: ${match_result.llm_cost:.4f}
- Fairness Score: {match_result.fairness_score*100:.0f}%
"""
        
        if match_result.bias_flags:
            report += f"\n⚠️ **Bias Flags Detected:** {len(match_result.bias_flags)}\n"
        
        return report
    
    @staticmethod
    def export_to_json(
        match_results: List[MatchResult],
        filepath: Optional[str] = None
    ) -> str:
        """
        Export match results to JSON format.
        
        Args:
            match_results: List of match results
            filepath: Optional file path to save
        
        Returns:
            JSON string
        """
        data = {
            "generated_at": datetime.now().isoformat(),
            "total_candidates": len(match_results),
            "results": [r.to_dict() for r in match_results]
        }
        
        json_str = json.dumps(data, indent=2)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
        
        return json_str
    
    @staticmethod
    def export_to_csv_format(match_results: List[MatchResult]) -> List[Dict]:
        """
        Export match results to CSV-friendly format.
        
        Args:
            match_results: List of match results
        
        Returns:
            List of dictionaries suitable for CSV export
        """
        csv_data = []
        
        for result in match_results:
            row = {
                "resume_id": result.resume_id,
                "job_id": result.job_id,
                "overall_score": result.overall_score,
                "recommendation": result.recommendation.value,
                "confidence": result.confidence,
                "semantic_similarity": result.semantic_similarity,
                "processing_time_ms": result.processing_time_ms,
                "cost": result.llm_cost,
                "fairness_score": result.fairness_score,
                "bias_flags_count": len(result.bias_flags),
                "strengths": "; ".join(result.strengths[:3]),
                "weaknesses": "; ".join(result.weaknesses[:3]),
                "missing_skills": "; ".join(result.missing_critical_skills)
            }
            
            # Add dimensional scores
            for dimension in result.dimension_scores:
                row[f"{dimension.dimension.lower().replace(' ', '_')}_score"] = dimension.score
            
            csv_data.append(row)
        
        return csv_data
    
    @staticmethod
    def generate_batch_summary(
        batch_result: BatchMatchResult
    ) -> str:
        """
        Generate summary for batch processing results.
        
        Args:
            batch_result: Batch match result
        
        Returns:
            Formatted summary
        """
        total = batch_result.total_resumes
        processed = len(batch_result.results)
        
        # Calculate aggregates
        strong = sum(1 for r in batch_result.results if r.recommendation.value == "Strong Match")
        maybe = sum(1 for r in batch_result.results if r.recommendation.value == "Maybe")
        
        avg_score = sum(r.overall_score for r in batch_result.results) / processed if processed else 0
        total_cost = batch_result.total_cost
        avg_time = batch_result.total_processing_time_ms / processed if processed else 0
        
        report = f"""
# BATCH PROCESSING SUMMARY
Job ID: {batch_result.job_id}
Processed: {batch_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## PROCESSING METRICS
- **Total Resumes:** {total}
- **Successfully Processed:** {processed}
- **Success Rate:** {processed/total*100:.1f}%

## CANDIDATE QUALITY
- **Strong Matches:** {strong} ({strong/processed*100:.1f}%)
- **Qualified Candidates:** {strong + maybe} ({(strong+maybe)/processed*100:.1f}%)
- **Average Score:** {avg_score:.1f}/100

## PERFORMANCE
- **Total Processing Time:** {batch_result.total_processing_time_ms/1000:.2f} seconds
- **Average Time per Candidate:** {avg_time/1000:.2f} seconds
- **Total Cost:** ${total_cost:.2f}
- **Average Cost per Candidate:** ${total_cost/processed:.4f}

## SHORTLIST RECOMMENDATION
Top {min(strong, 10)} candidates recommended for immediate interview.
Additional {maybe} candidates available for secondary review.
"""
        
        return report
