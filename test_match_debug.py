#!/usr/bin/env python3
"""
Debug script to test matching with actual files
"""

import sys
from pathlib import Path
from src.matcher import ResumeMatcher
from src.parsers import ResumeParser, JobDescriptionParser

def main():
    print("=" * 80)
    print("RESUME MATCHER DEBUG TEST")
    print("=" * 80)
    
    # File paths
    resume_path = Path("data/resumes/Ankit_Resume_SDS.pdf")
    jd_path = Path("data/job_descriptions/senior_ai_engineer.txt")
    
    if not resume_path.exists():
        print(f"❌ Resume file not found: {resume_path}")
        return 1
    
    if not jd_path.exists():
        print(f"❌ Job description file not found: {jd_path}")
        return 1
    
    print(f"✓ Resume file: {resume_path}")
    print(f"✓ JD file: {jd_path}")
    print()
    
    # Step 1: Test Resume Parsing
    print("Step 1: Parsing Resume...")
    print("-" * 80)
    try:
        resume_parser = ResumeParser()
        parsed_resume = resume_parser.parse_file(resume_path)
        print(f"✓ Resume parsed successfully")
        print(f"  Name: {parsed_resume.contact_info.get('name', 'N/A') if parsed_resume.contact_info else 'N/A'}")
        print(f"  Skills: {len(parsed_resume.skills) if parsed_resume.skills else 0} found")
        print(f"  Experience: {len(parsed_resume.work_experience) if parsed_resume.work_experience else 0} entries")
        print(f"  Education: {len(parsed_resume.education) if parsed_resume.education else 0} entries")
        if parsed_resume.skills:
            print(f"  Sample skills: {', '.join(parsed_resume.skills[:5])}")
        print()
    except Exception as e:
        print(f"❌ Resume parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 2: Test JD Parsing
    print("Step 2: Parsing Job Description...")
    print("-" * 80)
    try:
        jd_parser = JobDescriptionParser()
        jd_text = jd_path.read_text()
        parsed_jd = jd_parser.parse_text(jd_text)
        print(f"✓ Job description parsed successfully")
        print(f"  Title: {parsed_jd.job_title}")
        print(f"  Required Skills: {len(parsed_jd.required_skills)} found")
        print(f"  Preferred Skills: {len(parsed_jd.preferred_skills)} found")
        print(f"  Responsibilities: {len(parsed_jd.responsibilities)} found")
        if parsed_jd.required_skills:
            print(f"  Sample required: {', '.join(parsed_jd.required_skills[:5])}")
        print()
    except Exception as e:
        print(f"❌ JD parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 3: Test Matching
    print("Step 3: Running Matcher...")
    print("-" * 80)
    try:
        matcher = ResumeMatcher()
        result = matcher.match_resume_to_job(
            resume=parsed_resume,
            job_description=parsed_jd,
            resume_id="ankit_resume",
            job_id="senior_ai_engineer"
        )
        
        print(f"✓ Matching completed")
        print()
        print("RESULTS:")
        print(f"  Overall Score: {result.overall_score}%")
        print(f"  Semantic Similarity: {result.semantic_similarity:.2%}")
        print(f"  Recommendation: {result.recommendation}")
        print(f"  Confidence: {result.confidence:.2%}")
        print()
        
        if hasattr(result, 'dimension_scores') and result.dimension_scores:
            print("  Dimension Scores:")
            for dim, score in result.dimension_scores.items():
                print(f"    - {dim}: {score}%")
        else:
            print("  ⚠️  No dimension scores found")
        print()
        
        if result.strengths:
            print(f"  Strengths ({len(result.strengths)}):")
            for s in result.strengths[:3]:
                print(f"    + {s}")
        else:
            print("  ⚠️  No strengths found")
        print()
        
        if result.weaknesses:
            print(f"  Weaknesses ({len(result.weaknesses)}):")
            for w in result.weaknesses[:3]:
                print(f"    - {w}")
        else:
            print("  ⚠️  No weaknesses found")
        print()
        
        if result.metadata:
            print(f"  Metadata:")
            for key, val in result.metadata.items():
                print(f"    {key}: {val}")
        
        print()
        print("=" * 80)
        print("✅ DEBUG TEST COMPLETE")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"❌ Matching failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
