"""
Live Demo Page - Single Resume Matching
========================================

Interactive demo showcasing:
- Resume upload and parsing
- Job description input
- Real-time matching analysis
- Detailed score breakdowns
- Explainable recommendations
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import tempfile

# Import our matcher
try:
    from src.matcher import ResumeMatcher
    from src.parsers import ResumeParser, JobDescriptionParser
    from config.settings import get_settings
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.stop()

st.set_page_config(page_title="Live Demo", page_icon="🎯", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .score-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    
    .score-value {
        font-size: 4rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    
    .score-label {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .dimension-score {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .dimension-name {
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .evidence-item {
        background: #f8f9fa;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
    }
    
    .gap-item {
        background: #fff3cd;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🎯 Live Demo: Resume Matching")
st.markdown("Upload a resume and job description to see AI-powered matching in action.")

# Initialize session state
if 'match_result' not in st.session_state:
    st.session_state.match_result = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Main layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📄 Resume Upload")
    
    # File uploader
    uploaded_resume = st.file_uploader(
        "Upload Resume (PDF only)",
        type=['pdf'],
        help="Upload a candidate's resume in PDF format. Our Gemini-powered parser will extract all information."
    )
    
    if uploaded_resume:
        st.success(f"✅ Uploaded: {uploaded_resume.name}")
        st.info(f"📦 Size: {uploaded_resume.size / 1024:.1f} KB")
        
        # Option to parse immediately
        if st.button("🔍 Parse Resume Only", help="Preview extracted information"):
            with st.spinner("Parsing resume with Gemini..."):
                try:
                    # Save temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_resume.getbuffer())
                        tmp_path = tmp_file.name
                    
                    # Parse
                    parser = ResumeParser()
                    parsed_resume = parser.parse_file(tmp_path)
                    
                    # Clean up
                    Path(tmp_path).unlink()
                    
                    # Display results
                    st.success("✅ Resume parsed successfully!")
                    
                    with st.expander("📋 Parsed Information", expanded=True):
                        # Contact info
                        if parsed_resume.contact_info:
                            st.markdown("**Contact:**")
                            st.write(f"- Email: {parsed_resume.contact_info.email or 'N/A'}")
                            st.write(f"- Phone: {parsed_resume.contact_info.phone or 'N/A'}")
                            st.write(f"- Location: {parsed_resume.contact_info.location or 'N/A'}")
                        
                        # Experience
                        st.markdown(f"**Total Experience:** {parsed_resume.total_experience_years or 'N/A'} years")
                        
                        # Skills
                        if parsed_resume.skills:
                            st.markdown(f"**Skills ({len(parsed_resume.skills)}):**")
                            st.write(", ".join(parsed_resume.skills[:15]))
                            if len(parsed_resume.skills) > 15:
                                st.write(f"... and {len(parsed_resume.skills) - 15} more")
                        
                        # Education
                        if parsed_resume.education:
                            st.markdown(f"**Education ({len(parsed_resume.education)}):**")
                            for edu in parsed_resume.education:
                                st.write(f"- {edu.degree} in {edu.field_of_study or 'N/A'} from {edu.institution}")
                        
                        # Work Experience
                        if parsed_resume.work_experience:
                            st.markdown(f"**Work Experience ({len(parsed_resume.work_experience)} roles):**")
                            for exp in parsed_resume.work_experience[:3]:
                                st.write(f"- {exp.title} at {exp.company}")
                
                except Exception as e:
                    st.error(f"❌ Parsing Error: {str(e)}")
                    st.exception(e)

with col2:
    st.markdown("### 💼 Job Description")
    
    # Job description input
    input_method = st.radio(
        "Input Method",
        ["Paste Text", "Upload File"],
        horizontal=True
    )
    
    job_description = None
    
    if input_method == "Paste Text":
        job_description = st.text_area(
            "Job Description",
            height=300,
            placeholder="""Example:
Senior Software Engineer - AI/ML

Requirements:
- 5+ years Python development
- Experience with LLMs and NLP
- Strong ML/AI background
- Bachelor's in CS or related field

Responsibilities:
- Build AI-powered applications
- Design scalable ML systems
- Collaborate with cross-functional teams
"""
        )
    else:
        uploaded_jd = st.file_uploader(
            "Upload Job Description",
            type=['txt', 'pdf'],
            help="Upload job description as text or PDF"
        )
        
        if uploaded_jd:
            if uploaded_jd.type == "application/pdf":
                st.warning("⚠️ PDF parsing for JDs coming soon. Please use text file or paste text.")
            else:
                job_description = uploaded_jd.read().decode('utf-8')
                st.success(f"✅ Loaded: {uploaded_jd.name}")

# Matching section
st.markdown("---")
st.markdown("### 🚀 Run Matching Analysis")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    match_button = st.button(
        "🎯 Match Resume to Job",
        disabled=not (uploaded_resume and job_description),
        help="Run comprehensive matching analysis",
        type="primary"
    )

with col2:
    anonymize = st.checkbox("Anonymize Resume", value=False, help="Remove PII before matching")

# Process matching
if match_button and uploaded_resume is not None and job_description is not None:
    st.session_state.processing = True
    
    with st.spinner("🤖 Running AI analysis... This may take 30-60 seconds"):
        try:
            # Save resume temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_resume.getbuffer())
                tmp_resume_path = tmp_file.name
            
            # Initialize matcher
            matcher = ResumeMatcher()
            
            # Run matching
            start_time = datetime.now()
            result = matcher.match_resume_to_job(
                resume=tmp_resume_path,
                job_description=job_description,
                resume_id=f"resume_{datetime.now().timestamp()}",
                job_id="demo_job"
            )
            end_time = datetime.now()
            
            # Clean up
            Path(tmp_resume_path).unlink()
            
            # Store result
            st.session_state.match_result = {
                'result': result,
                'processing_time': (end_time - start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
            st.session_state.processing = False
            st.success("✅ Analysis complete!")
            st.balloons()
            
        except Exception as e:
            st.session_state.processing = False
            st.error(f"❌ Matching Error: {str(e)}")
            st.exception(e)

# Display results
if st.session_state.match_result:
    result_data = st.session_state.match_result
    result = result_data['result']
    
    st.markdown("---")
    st.markdown("## 📊 Matching Results")
    
    # Overall score (already in 0-100 range from LLM)
    overall_score = result.overall_score
    recommendation = result.recommendation.value if hasattr(result.recommendation, 'value') else str(result.recommendation)
    
    # Determine color based on score
    if overall_score >= 80:
        score_color = "#28a745"  # Green
        emoji = "🎉"
    elif overall_score >= 60:
        score_color = "#ffc107"  # Yellow
        emoji = "👍"
    else:
        score_color = "#dc3545"  # Red
        emoji = "🤔"
    
    st.markdown(f"""
    <div class="score-container" style="background: linear-gradient(135deg, {score_color} 0%, {score_color}dd 100%);">
        <div class="score-label">Overall Match Score</div>
        <div class="score-value">{emoji} {overall_score:.1f}%</div>
        <div class="score-label">Recommendation: <strong>{recommendation}</strong></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Processing Time", f"{result_data['processing_time']:.1f}s")
    with col2:
        # Semantic similarity is 0-1, convert to percentage
        semantic_pct = result.semantic_similarity * 100 if result.semantic_similarity <= 1.0 else result.semantic_similarity
        st.metric("Semantic Score", f"{semantic_pct:.1f}%")
    with col3:
        if result.llm_cost:
            st.metric("API Cost", f"${result.llm_cost:.4f}")
        else:
            st.metric("API Cost", "N/A")
    with col4:
        st.metric("Confidence", f"{result.confidence * 100:.0f}%")
    
    # Dimensional scores
    st.markdown("### 📈 Detailed Score Breakdown")
    
    for dimension in result.dimension_scores:
        # Scores are already 0-100, weights are 0-1
        score_pct = dimension.score if dimension.score <= 100 else dimension.score
        weight_pct = dimension.weight * 100
        
        # Progress bar color
        if score_pct >= 75:
            bar_color = "🟢"
        elif score_pct >= 50:
            bar_color = "🟡"
        else:
            bar_color = "🔴"
        
        with st.expander(f"{bar_color} **{dimension.dimension}** - {score_pct:.1f}% (Weight: {weight_pct:.0f}%)", expanded=False):
            # Score bar (needs 0-1 range for st.progress)
            st.progress(dimension.score / 100.0 if dimension.score > 1 else dimension.score)
            
            # Reasoning
            if dimension.explanation:
                st.markdown("**Analysis:**")
                st.info(dimension.explanation)
            
            # Evidence
            if dimension.evidence:
                st.markdown("**✅ Strengths:**")
                for evidence in dimension.evidence:
                    st.markdown(f"""
                    <div class="evidence-item">
                        ✓ {evidence}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Gaps
            if dimension.gaps:
                st.markdown("**⚠️ Areas for Improvement:**")
                for gap in dimension.gaps:
                    st.markdown(f"""
                    <div class="gap-item">
                        ! {gap}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Skills analysis
    if result.matched_skills or result.missing_critical_skills:
        st.markdown("### 🎯 Skills Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Matched Skills**")
            if result.matched_skills:
                matched_df = []
                for skill in result.matched_skills[:10]:
                    matched_df.append({
                        "Skill": skill.skill,
                        "Match": f"{skill.relevance_score * 100:.0f}%",
                        "Type": skill.match_type
                    })
                st.dataframe(matched_df, hide_index=True)
            else:
                st.info("No matched skills found")
        
        with col2:
            st.markdown("**❌ Missing Critical Skills**")
            if result.missing_critical_skills:
                for skill in result.missing_critical_skills[:10]:
                    st.markdown(f"- {skill}")
                if len(result.missing_critical_skills) > 10:
                    st.caption(f"... and {len(result.missing_critical_skills) - 10} more")
            else:
                st.success("All required skills present!")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    
    # Get the recommendation value (handle both Enum and string)
    rec_value = result.recommendation.value if hasattr(result.recommendation, 'value') else str(result.recommendation)
    
    if rec_value == "Strong Match" or result.recommendation.name == "STRONG_MATCH":
        st.success("""
        **🎉 Strong Match - Highly Recommended**
        - Schedule interview immediately
        - Prioritize in the candidate pipeline
        - Consider expedited process
        """)
    elif rec_value == "Maybe" or result.recommendation.name == "MAYBE":
        st.info("""
        **👍 Good Match - Recommended**
        - Proceed with interview
        - Review specific gaps during interview
        - Consider for further rounds
        """)
    elif rec_value == "Weak Match" or result.recommendation.name == "WEAK_MATCH":
        st.warning("""
        **🤔 Weak Match - Review Required**
        - Manual review recommended
        - Assess missing skills
        - Consider for junior roles or with training
        """)
    else:  # NOT_RECOMMENDED
        st.error("""
        **❌ Not Recommended**
        - Does not meet key requirements
        - Significant skill gaps
        - Consider other candidates first
        """)
    
    # Export options
    st.markdown("---")
    st.markdown("### 📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON export
        json_data = {
            'overall_score': result.overall_score,
            'recommendation': result.recommendation,
            'dimension_scores': [
                {
                    'dimension': d.dimension,
                    'score': d.score,
                    'weight': d.weight,
                    'explanation': d.explanation
                } for d in result.dimension_scores
            ],
            'processing_time': result_data['processing_time'],
            'timestamp': result_data['timestamp']
        }
        
        st.download_button(
            "📄 Download JSON",
            data=json.dumps(json_data, indent=2),
            file_name=f"match_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Text report
        report_text = f"""RESUME MATCHING REPORT
=====================

Overall Score: {overall_score:.1f}%
Recommendation: {recommendation}
Processing Time: {result_data['processing_time']:.1f}s

DIMENSIONAL SCORES:
"""
        for dim in result.dimension_scores:
            # Scores already in 0-100 range
            report_text += f"\n{dim.dimension}: {dim.score:.1f}%"
        
        st.download_button(
            "📝 Download Report",
            data=report_text,
            file_name=f"match_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    with col3:
        if st.button("🔄 New Analysis"):
            st.session_state.match_result = None
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>Powered by:</strong> OpenAI GPT-4 (Matching) • Google Gemini 2.0 Flash (Parsing)</p>
    <p>All results are AI-generated and should be reviewed by human recruiters.</p>
</div>
""", unsafe_allow_html=True)
