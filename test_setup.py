#!/usr/bin/env python3
"""
Setup Verification Script
Tests that all components are working correctly before demo
"""

import sys
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def test_python_version():
    """Check Python version"""
    print_header("1. Checking Python Version")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 9:
        print_success(f"Python {version_str} (Required: 3.9+)")
        return True
    else:
        print_error(f"Python {version_str} (Required: 3.9+)")
        return False

def test_imports():
    """Test critical imports"""
    print_header("2. Testing Critical Imports")
    
    imports = {
        "streamlit": "Streamlit UI framework",
        "openai": "OpenAI API",
        "google.generativeai": "Google Gemini API",
        "anthropic": "Anthropic Claude API (optional)",
        "sentence_transformers": "Embeddings",
        "pandas": "Data processing",
        "plotly": "Visualizations",
        "pydantic": "Data validation",
        "tenacity": "Retry logic",
        "tiktoken": "Token counting"
    }
    
    success_count = 0
    total_count = len(imports)
    
    for module, description in imports.items():
        try:
            __import__(module)
            print_success(f"{module:30s} - {description}")
            success_count += 1
        except ImportError as e:
            if module == "anthropic":
                print_warning(f"{module:30s} - {description} (Optional)")
            else:
                print_error(f"{module:30s} - {description} - {str(e)}")
    
    print(f"\nImported {success_count}/{total_count} modules")
    return success_count >= (total_count - 1)  # -1 for optional anthropic

def test_project_structure():
    """Check project structure"""
    print_header("3. Verifying Project Structure")
    
    required_paths = {
        "src": "Source code directory",
        "src/llm_adapters": "LLM adapters",
        "src/bias_detection": "Bias detection suite",
        "src/analytics": "Analytics engine",
        "config": "Configuration files",
        "pages": "Streamlit pages",
        "data": "Data directory",
        "data/resumes": "Resume storage",
        "data/job_descriptions": "Job description storage",
        ".env.example": "Environment template",
        "app.py": "Main application",
        "pyproject.toml": "UV configuration",
        "README.md": "Documentation"
    }
    
    success_count = 0
    
    for path_str, description in required_paths.items():
        path = Path(path_str)
        if path.exists():
            print_success(f"{path_str:30s} - {description}")
            success_count += 1
        else:
            print_error(f"{path_str:30s} - {description} - Missing!")
    
    print(f"\nFound {success_count}/{len(required_paths)} required paths")
    return success_count == len(required_paths)

def test_config():
    """Test configuration loading"""
    print_header("4. Testing Configuration")
    
    try:
        from config.settings import get_settings
        settings = get_settings()
        
        # Check OpenAI
        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            print_success("OpenAI API key configured")
            openai_ok = True
        else:
            print_error("OpenAI API key not configured (Required)")
            openai_ok = False
        
        # Check Google AI
        if settings.google_api_key and settings.google_api_key != "your_google_api_key_here":
            print_success("Google AI API key configured")
            google_ok = True
        else:
            print_error("Google AI API key not configured (Required)")
            google_ok = False
        
        # Check Anthropic
        if settings.anthropic_api_key and settings.anthropic_api_key != "your_anthropic_api_key_here":
            print_success("Anthropic API key configured (Optional)")
        else:
            print_warning("Anthropic API key not configured (Optional)")
        
        # Check scoring weights
        weights = settings.get_scoring_weights()
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) < 0.001:
            print_success(f"Scoring weights sum to {total_weight:.3f}")
        else:
            print_error(f"Scoring weights sum to {total_weight:.3f} (should be 1.0)")
        
        return openai_ok and google_ok
        
    except Exception as e:
        print_error(f"Configuration error: {str(e)}")
        return False

def test_core_modules():
    """Test core module imports"""
    print_header("5. Testing Core Modules")
    
    modules = [
        ("src.models", "Data models"),
        ("src.parsers", "Resume/JD parsers"),
        ("src.llm_adapters.factory", "LLM factory"),
        ("src.semantic_matcher", "Semantic matcher"),
        ("src.llm_matcher", "LLM matcher"),
        ("src.scoring_engine", "Scoring engine"),
        ("src.matcher", "Main matcher"),
        ("src.bias_detection.detector", "Bias detector"),
        ("src.analytics.roi_calculator", "ROI calculator"),
    ]
    
    success_count = 0
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            print_success(f"{module_name:35s} - {description}")
            success_count += 1
        except Exception as e:
            print_error(f"{module_name:35s} - {description} - {str(e)}")
    
    print(f"\nLoaded {success_count}/{len(modules)} core modules")
    return success_count == len(modules)

def test_streamlit_pages():
    """Check Streamlit pages"""
    print_header("6. Checking Streamlit Pages")
    
    pages = [
        "pages/1_🎯_Live_Demo.py",
        "pages/2_📊_Executive_Dashboard.py",
        "pages/3_⚖️_Bias_Analysis.py",
        "pages/4_📦_Batch_Processing.py"
    ]
    
    success_count = 0
    
    for page in pages:
        if Path(page).exists():
            print_success(page)
            success_count += 1
        else:
            print_error(f"{page} - Missing!")
    
    print(f"\nFound {success_count}/{len(pages)} Streamlit pages")
    return success_count == len(pages)

def test_sample_data():
    """Check sample data"""
    print_header("7. Checking Sample Data")
    
    jd_path = Path("data/job_descriptions/senior_ai_engineer.txt")
    
    if jd_path.exists():
        print_success("Sample job description found")
        print(f"   Location: {jd_path}")
        jd_ok = True
    else:
        print_warning("Sample job description not found")
        print(f"   Expected: {jd_path}")
        jd_ok = False
    
    resume_count = len(list(Path("data/resumes").glob("*.pdf")))
    if resume_count > 0:
        print_success(f"Found {resume_count} sample resume(s)")
    else:
        print_warning("No sample resumes found in data/resumes/")
        print("   Add sample PDFs to test the system")
    
    return jd_ok

def main():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("  TechCorp AI Resume Matcher - Setup Verification")
    print("🚀"*30)
    
    results = []
    
    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Package Imports", test_imports()))
    results.append(("Project Structure", test_project_structure()))
    results.append(("Configuration", test_config()))
    results.append(("Core Modules", test_core_modules()))
    results.append(("Streamlit Pages", test_streamlit_pages()))
    results.append(("Sample Data", test_sample_data()))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s} : {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉"*30)
        print("  ALL TESTS PASSED! System is ready for demo!")
        print("🎉"*30)
        print("\nNext steps:")
        print("1. Ensure .env file has your API keys")
        print("2. Run: streamlit run app.py")
        print("3. Navigate to http://localhost:8501")
        print("\n✨ Happy matching! ✨\n")
        return 0
    else:
        print("\n" + "⚠️ "*30)
        print("  SOME TESTS FAILED - Please fix issues before demo")
        print("⚠️ "*30)
        print("\nCommon fixes:")
        print("1. Run: ./setup.sh")
        print("2. Create .env from .env.example")
        print("3. Add your API keys to .env")
        print("4. Ensure Python 3.9+ is installed")
        print("\nSee QUICKSTART.md for detailed setup guide\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
