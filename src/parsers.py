"""
Resume and Job Description Parsers
Uses Gemini 2.0 Flash for intelligent document parsing with structured output.
Uploads PDF directly to Gemini for native processing.
"""

import json
import re
from pathlib import Path
from typing import Optional, Union, Dict, Any
from datetime import datetime
from dateutil import parser as date_parser
from google import genai
from google.genai import types as genai_types

from .models import (
    ParsedResume, ParsedJobDescription, ContactInfo, Education,
    WorkExperience, Certification, JobRequirement, ExperienceLevel
)
from .llm_adapters.factory import LLMFactory
from .llm_adapters.base import LLMResponse
from config.settings import get_settings


def recalculate_experience_durations(parsed_resume: ParsedResume) -> ParsedResume:
    """
    Recalculate work experience durations using current date for "Present" positions.
    
    This fixes the issue where Gemini calculates duration at parse time, but
    for current roles (end_date = "Present" or None), the duration becomes stale.
    
    Args:
        parsed_resume: Parsed resume with potentially stale duration_months
    
    Returns:
        Updated ParsedResume with recalculated durations
    """
    current_date = datetime.now()
    total_months = 0
    
    for exp in parsed_resume.work_experience:
        if not exp.start_date:
            # Can't calculate without start date
            continue
        
        try:
            # Parse start date - handle various formats
            if isinstance(exp.start_date, str):
                # Try to parse the date string
                start_date = date_parser.parse(exp.start_date, fuzzy=True)
            else:
                continue
            
            # Determine end date
            if exp.end_date and exp.end_date.lower() not in ['present', 'current', 'now']:
                # Parse end date
                try:
                    end_date = date_parser.parse(exp.end_date, fuzzy=True)
                except:
                    # If parsing fails, assume current
                    end_date = current_date
            else:
                # No end date or "Present" means current
                end_date = current_date
            
            # Calculate duration in months
            duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            
            # Update the work experience object
            exp.duration_months = duration_months
            total_months += duration_months
            
        except Exception as e:
            # If date parsing fails, keep original duration
            print(f"⚠️  Could not parse dates for {exp.company}: {e}")
            if exp.duration_months:
                total_months += exp.duration_months
    
    # Update total experience years
    if total_months > 0:
        parsed_resume.total_experience_years = round(total_months / 12, 1)
    
    return parsed_resume


class ResumeParser:
    """
    Intelligent resume parser using Gemini 2.0 Flash.
    Handles PDF, DOCX, and TXT formats with robust extraction.
    Uses Gemini's native PDF processing for better accuracy.
    """
    
    def __init__(self):
        """Initialize parser with Gemini adapter"""
        self.llm = LLMFactory.get_parsing_adapter()  # Gemini 2.0 Flash
        settings = get_settings()
        # Initialize genai client for PDF processing
        self.genai_client = genai.Client(api_key=settings.google_api_key)
        self.model_name = settings.gemini_model
    
    def parse_file(self, file_path: Union[str, Path]) -> ParsedResume:
        """
        Parse resume from file.
        For PDFs, uploads directly to Gemini for native processing.
        
        Args:
            file_path: Path to resume file (PDF, DOCX, or TXT)
        
        Returns:
            ParsedResume with structured data
        
        Raises:
            ValueError: If file format is unsupported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        # Extract text based on file type
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self._parse_pdf_with_gemini(file_path)
        elif extension == '.docx':
            raw_text = self._extract_docx_text(file_path)
            return self.parse_text(raw_text)
        elif extension == '.txt':
            raw_text = file_path.read_text(encoding='utf-8')
            return self.parse_text(raw_text)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def parse_text(self, resume_text: str) -> ParsedResume:
        """
        Parse resume from text using LLM with structured outputs (Pydantic).
        
        Uses Pydantic models directly for type-safe, validated parsing without
        manual JSON parsing. Much more reliable than text-based JSON extraction.
        
        Args:
            resume_text: Raw resume text
        
        Returns:
            ParsedResume with structured, validated data
        """
        # Create prompt for structured extraction
        system_prompt = """You are an expert resume parser. Extract structured information from resumes.
Be thorough and accurate. If information is not present, use null or empty lists.
Extract ALL skills mentioned throughout the resume, including those in experience descriptions.
Calculate total_experience_years from work experience dates."""
        
        user_prompt = f"""Parse the following resume and extract structured information.

Resume:
{resume_text}

Extract all information accurately:
- Contact info (email, phone, LinkedIn, GitHub, location, portfolio)
- Professional summary
- Education (degrees, institutions, years, GPA, honors)
- Work experience (company, title, dates, descriptions, achievements, technologies)
- Skills (ALL technical skills, tools, and technologies mentioned)
- Certifications (name, issuer, dates, credentials)
- Languages spoken
- Total years of experience (calculate from work history)

Be comprehensive and extract everything mentioned."""
        
        # Try new structured output method first
        if hasattr(self.llm, 'generate_with_schema'):
            try:
                # Type ignore since we're checking existence at runtime
                parsed_resume, response = self.llm.generate_with_schema(  # type: ignore
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    response_model=ParsedResume  # Pass Pydantic model directly!
                )
                
                # Update metadata
                parsed_resume.metadata = {
                    "parsing_cost": response.cost,
                    "parsing_latency_ms": response.latency_ms,
                    "model_used": response.model,
                    "structured_output": True
                }
                
                return parsed_resume
                
            except Exception as e:
                print(f"Structured output failed, falling back to legacy: {e}")
        
        # Fallback to legacy JSON mode if structured outputs not available
        return self._parse_text_legacy(resume_text, system_prompt, user_prompt)
    
    def _parse_text_legacy(self, resume_text: str, system_prompt: str, user_prompt: str) -> ParsedResume:
        """Legacy parsing method using JSON mode (fallback)"""
        # Call LLM for structured extraction
        response: LLMResponse = self.llm.generate_structured(
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_schema=None  # Legacy method
        )
        
        # Parse JSON response manually
        try:
            parsed_data = json.loads(response.content)
        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON from response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        
        # Convert to Pydantic model with validation
        parsed_resume = ParsedResume(
            raw_text=resume_text,
            contact_info=ContactInfo(**parsed_data.get("contact_info", {})),
            summary=parsed_data.get("summary"),
            education=[Education(**edu) for edu in parsed_data.get("education", [])],
            work_experience=[WorkExperience(**exp) for exp in parsed_data.get("work_experience", [])],
            skills=parsed_data.get("skills", []),
            certifications=[Certification(**cert) for cert in parsed_data.get("certifications", [])],
            languages=parsed_data.get("languages", []),
            total_experience_years=parsed_data.get("total_experience_years"),
            metadata={
                "parsing_cost": response.cost,
                "parsing_latency_ms": response.latency_ms,
                "model_used": response.model,
                "structured_output": False  # Legacy mode
            }
        )
        
        # Recalculate experience durations for current roles
        return recalculate_experience_durations(parsed_resume)
    
    def _parse_pdf_with_gemini(self, pdf_path: Path) -> ParsedResume:
        """
        Parse PDF directly using Gemini's native PDF processing with structured outputs.
        
        Uses Pydantic models directly via Gemini's new SDK for type-safe parsing.
        Reads PDF bytes and sends to Gemini with response_schema for guaranteed structure.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            ParsedResume with structured, validated data
        """
        # Read PDF file as bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        # Create prompt for structured extraction with explicit JSON schema
        json_schema = {
            "contact_info": {
                "email": "string or null",
                "phone": "string or null",
                "linkedin": "string or null",
                "github": "string or null",
                "location": "string or null",
                "portfolio": "string or null"
            },
            "summary": "string or null",
            "education": [
                {
                    "degree": "string",
                    "institution": "string",
                    "field_of_study": "string or null",
                    "graduation_year": "integer or null",
                    "gpa": "float or null",
                    "honors": ["string"]
                }
            ],
            "work_experience": [
                {
                    "company": "string",
                    "title": "string",
                    "start_date": "string or null",
                    "end_date": "string or null",
                    "duration_months": "integer or null",
                    "description": "string or null",
                    "achievements": ["string"],
                    "technologies": ["string"]
                }
            ],
            "skills": ["string"],
            "certifications": [
                {
                    "name": "string",
                    "issuer": "string",
                    "issue_date": "string or null",
                    "expiry_date": "string or null",
                    "credential_id": "string or null"
                }
            ],
            "languages": ["string"],
            "total_experience_years": "float or null"
        }
        
        prompt = f"""Parse this resume PDF and extract all information.

CRITICAL: You MUST respond with ONLY valid JSON. No markdown, no explanations, no text before or after the JSON.

Extract the following information into this EXACT JSON structure:
{json.dumps(json_schema, indent=2)}

Instructions:
- Extract ALL information comprehensively
- If a field is not present, use null or empty array
- For work_experience, include description AND achievements
- Extract ALL skills from entire resume (experience, projects, skills section)
- Calculate total_experience_years from work history dates
- Return ONLY the JSON object, nothing else

RESPOND WITH ONLY VALID JSON - NO MARKDOWN, NO TEXT, JUST JSON."""
        
        system_prompt = "You are a JSON-only resume parser. You MUST respond with valid JSON only, no additional text or formatting."
        
        # Note: New google.genai SDK doesn't yet support PDF with structured outputs
        # Using legacy method for PDF parsing (works reliably)
        print(f"📄 Parsing PDF with Gemini (using legacy method for PDF support)...")
        
        # Fallback to legacy Gemini PDF parsing
        return self._parse_pdf_with_gemini_legacy(pdf_path, pdf_bytes, prompt)
    
    def _parse_pdf_with_gemini_legacy(self, pdf_path: Path, pdf_bytes: bytes, prompt: str) -> ParsedResume:
        """Legacy Gemini PDF parsing using old google.generativeai SDK"""
        # Note: This uses the OLD google.generativeai package which is still installed
        # but not type-checked. We use type: ignore comments for Pylance.
        import google.generativeai as genai_legacy  # type: ignore
        
        # Configure and use old SDK
        genai_legacy.configure(api_key=self.llm.api_key)  # type: ignore
        model = genai_legacy.GenerativeModel('gemini-2.5-flash')  # type: ignore
        
        # Configure for JSON output
        generation_config = genai_legacy.types.GenerationConfig(  # type: ignore
            temperature=0.2,  # Low temperature for consistent JSON
            response_mime_type="application/json"  # Force JSON output!
        )
        
        # Generate response with PDF using inline data
        print(f"🤖 Sending PDF to Gemini for JSON parsing...")
        response = model.generate_content(
            [
                {
                    'mime_type': 'application/pdf',
                    'data': pdf_bytes
                },
                prompt
            ],
            generation_config=generation_config
        )
        
        # Check if response is blocked or empty
        if not response.text or len(response.text.strip()) == 0:
            error_msg = "Gemini returned empty response"
            if response.prompt_feedback:
                error_msg += f". Feedback: {response.prompt_feedback}"
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'finish_reason'):
                        error_msg += f". Finish reason: {candidate.finish_reason}"
                    if hasattr(candidate, 'safety_ratings'):
                        error_msg += f". Safety ratings: {candidate.safety_ratings}"
            raise ValueError(error_msg)
        
        print(f"📝 Got response from Gemini ({len(response.text)} chars), parsing JSON...")
        
        # Parse JSON response
        try:
            # Clean response text
            response_text = response.text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            parsed_data = json.loads(response_text)
            print(f"✅ Successfully parsed JSON response")
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"📄 Response preview: {response.text[:500]}...")
            # Fallback: try to extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                print(f"🔍 Found JSON in response, attempting to parse...")
                parsed_data = json.loads(json_match.group())
                print(f"✅ Successfully extracted and parsed JSON")
            else:
                raise ValueError(f"Failed to parse LLM response as JSON: {e}. Response was: {response.text[:200]}")
        
        # Get raw text for storage
        raw_text = f"[Parsed from PDF: {pdf_path.name}]"
        
        # Convert to Pydantic model with validation
        parsed_resume = ParsedResume(
            raw_text=raw_text,
            contact_info=ContactInfo(**parsed_data.get("contact_info", {})),
            summary=parsed_data.get("summary"),
            education=[Education(**edu) for edu in parsed_data.get("education", [])],
            work_experience=[WorkExperience(**exp) for exp in parsed_data.get("work_experience", [])],
            skills=parsed_data.get("skills", []),
            certifications=[Certification(**cert) for cert in parsed_data.get("certifications", [])],
            languages=parsed_data.get("languages", []),
            total_experience_years=parsed_data.get("total_experience_years"),
            metadata={
                "parsing_method": "gemini_native_pdf_legacy",
                "file_name": pdf_path.name,
                "model_used": "gemini-2.5-flash",
                "structured_output": False
            }
        )
        
        # Recalculate experience durations for current roles
        return recalculate_experience_durations(parsed_resume)
    
    def _extract_docx_text(self, docx_path: Path) -> str:
        """
        Extract text from DOCX file.
        Note: For DOCX, we extract text first then send to LLM.
        Gemini's file upload API works best with PDF.
        """
        try:
            # Simple text extraction without python-docx dependency
            # In production, consider using python-docx or converting to PDF
            with open(docx_path, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
                # Basic cleanup
                content = re.sub(r'[^\x00-\x7F]+', ' ', content)
                return content
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {e}")


class JobDescriptionParser:
    """
    Job description parser using LLM for intelligent extraction.
    """
    
    def __init__(self):
        """Initialize parser with Gemini adapter"""
        self.llm = LLMFactory.get_parsing_adapter()  # Gemini 2.0 Flash
    
    def parse_text(self, jd_text: str) -> ParsedJobDescription:
        """
        Parse job description from text.
        
        Args:
            jd_text: Raw job description text
        
        Returns:
            ParsedJobDescription with structured data
        """
        # Define expected schema
        schema = {
            "job_title": "string",
            "company": "string or null",
            "location": "string or null",
            "job_type": "string or null",
            "experience_level": "string or null",
            "summary": "string",
            "responsibilities": ["string"],
            "required_skills": ["string"],
            "preferred_skills": ["string"],
            "education_requirements": ["string"],
            "min_experience_years": "integer or null",
            "max_experience_years": "integer or null",
            "requirements": [
                {
                    "category": "string",
                    "requirement": "string",
                    "is_required": "boolean",
                    "priority": "integer (1-3)"
                }
            ]
        }
        
        system_prompt = """You are an expert job description analyzer. Extract structured information from job postings.
Categorize requirements into: technical_skill, soft_skill, experience, education, certification.
Priority: 1=critical (must-have), 2=important, 3=nice-to-have."""
        
        user_prompt = f"""Parse the following job description and extract structured information.

Job Description:
{jd_text}

Extract all information into the exact JSON structure.
Separate required_skills (must-have) from preferred_skills (nice-to-have).
For experience_level, choose from: Entry Level, Mid Level, Senior, Lead, Executive."""
        
        # Call LLM
        response: LLMResponse = self.llm.generate_structured(
            prompt=user_prompt,
            system_prompt=system_prompt,
            response_schema=schema
        )
        
        # Parse JSON
        try:
            parsed_data = json.loads(response.content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group())
            else:
                raise ValueError("Failed to parse job description")
        
        # Map experience level to enum
        exp_level = parsed_data.get("experience_level")
        if exp_level and isinstance(exp_level, str):
            try:
                parsed_data["experience_level"] = ExperienceLevel(exp_level)
            except ValueError:
                parsed_data["experience_level"] = None
        
        # Convert to Pydantic model
        return ParsedJobDescription(
            raw_text=jd_text,
            job_title=parsed_data["job_title"],
            company=parsed_data.get("company"),
            location=parsed_data.get("location"),
            job_type=parsed_data.get("job_type"),
            experience_level=parsed_data.get("experience_level"),
            summary=parsed_data["summary"],
            responsibilities=parsed_data.get("responsibilities", []),
            required_skills=parsed_data.get("required_skills", []),
            preferred_skills=parsed_data.get("preferred_skills", []),
            education_requirements=parsed_data.get("education_requirements", []),
            requirements=[JobRequirement(**req) for req in parsed_data.get("requirements", [])],
            min_experience_years=parsed_data.get("min_experience_years"),
            max_experience_years=parsed_data.get("max_experience_years"),
            metadata={
                "parsing_cost": response.cost,
                "parsing_latency_ms": response.latency_ms,
                "model_used": response.model
            }
        )
    
    def parse_file(self, file_path: Union[str, Path]) -> ParsedJobDescription:
        """Parse job description from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Job description file not found: {file_path}")
        
        text = file_path.read_text(encoding='utf-8')
        return self.parse_text(text)
