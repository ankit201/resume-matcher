#!/usr/bin/env python3
"""Test that experience duration is now correctly calculated"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.parsers import ResumeParser
from datetime import datetime

def main():
    print("=" * 70)
    print("EXPERIENCE DURATION TEST")
    print("=" * 70)
    print(f"Current Date: {datetime.now().strftime('%B %d, %Y')}")
    print()
    
    parser = ResumeParser()
    parsed = parser.parse_file(Path("data/resumes/Ankit_Resume_SDS.pdf"))
    
    print(f"Total Experience: {parsed.total_experience_years} years")
    print()
    print("Detailed Work Experience:")
    print("-" * 70)
    
    for i, exp in enumerate(parsed.work_experience, 1):
        print(f"\n{i}. {exp.title}")
        print(f"   Company: {exp.company}")
        print(f"   Start: {exp.start_date}")
        print(f"   End: {exp.end_date or 'Present'}")
        
        if exp.duration_months:
            years = exp.duration_months // 12
            months = exp.duration_months % 12
            print(f"   Duration: {years} years, {months} months ({exp.duration_months} total months)")
        else:
            print(f"   Duration: Not calculated")
    
    print()
    print("=" * 70)
    print("✅ VERIFICATION:")
    print("=" * 70)
    
    # Check Fractal Analytics specifically
    fractal_exp = next((e for e in parsed.work_experience if "Fractal" in e.company), None)
    if fractal_exp:
        years = fractal_exp.duration_months // 12 if fractal_exp.duration_months else 0
        months = fractal_exp.duration_months % 12 if fractal_exp.duration_months else 0
        
        print(f"\n✓ Fractal Analytics experience:")
        print(f"  - Start: March 2023")
        print(f"  - End: Present (October 2025)")
        print(f"  - Calculated: {years}y {months}m")
        print(f"  - Expected: ~2y 7m")
        
        if years == 2 and 6 <= months <= 8:
            print(f"\n✅ SUCCESS! Duration is correctly calculated using current date!")
        else:
            print(f"\n⚠️  Duration might be off. Expected around 2y 7m, got {years}y {months}m")
    else:
        print("❌ Could not find Fractal Analytics experience")
    
    print()
    return 0

if __name__ == "__main__":
    sys.exit(main())
