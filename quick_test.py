#!/usr/bin/env python3
"""Quick test of matching"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.matcher import ResumeMatcher

def main():
    print("=" * 60)
    print("QUICK MATCHING TEST")
    print("=" * 60)
    
    resume_path = Path("data/resumes/Ankit_Resume_SDS.pdf")
    jd_path = Path("data/job_descriptions/senior_ai_engineer.txt")
    
    print(f"\nResume: {resume_path}")
    print(f"JD: {jd_path}\n")
    
    matcher = ResumeMatcher()
    
    print("Starting match (this will take 30-60 seconds)...\n")
    
    result = matcher.match_resume_to_job(
        resume=resume_path,
        job_description=jd_path.read_text(),
        resume_id="ankit",
        job_id="senior_ai_ml",
        detect_bias=False  # Skip bias for speed
    )
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Overall Score: {result.overall_score}%")
    print(f"Recommendation: {result.recommendation}")
    print(f"Semantic Similarity: {result.semantic_similarity:.1%}")
    print(f"Confidence: {result.confidence:.1%}")
    print(f"\nDimensions:")
    for dim in result.dimension_scores:
        print(f"  • {dim.dimension}: {dim.score}%")
    
    print(f"\nStrengths ({len(result.strengths)}):")
    for s in result.strengths[:3]:
        print(f"  + {s}")
    
    print(f"\nWeaknesses ({len(result.weaknesses)}):")
    for w in result.weaknesses[:3]:
        print(f"  - {w}")
    
    print("\n" + "=" * 60)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
