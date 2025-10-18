"""
Batch Processing Page - Multiple Resume Screening
=================================================

Features:
- Upload multiple resumes at once
- Process against single job description
- Bulk analysis and ranking
- Export results in multiple formats
- Progress tracking
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import tempfile
from datetime import datetime
import json
import time

try:
    from src.matcher import ResumeMatcher
    from src.parsers import JobDescriptionParser
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.stop()

st.set_page_config(page_title="Batch Processing", page_icon="📦", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .batch-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .result-row {
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 4px solid #0066CC;
        background: #f8f9fa;
    }
    
    .rank-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .rank-1 { background: #ffd700; color: #333; }
    .rank-2 { background: #c0c0c0; color: #333; }
    .rank-3 { background: #cd7f32; color: white; }
    .rank-default { background: #e9ecef; color: #495057; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📦 Batch Processing")
st.markdown("Screen multiple resumes efficiently against a single job description")

# Initialize session state
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Instructions
with st.expander("📖 How to Use Batch Processing", expanded=False):
    st.markdown("""
    ### Step-by-Step Guide
    
    1. **Upload Job Description**
       - Paste text or upload a file
       - Ensure all requirements are clearly stated
    
    2. **Upload Multiple Resumes**
       - Select multiple PDF files at once
       - Maximum 50 resumes per batch
    
    3. **Configure Settings**
       - Set minimum match threshold
       - Choose how many top candidates to display
    
    4. **Process Batch**
       - Click "Process Batch" to start
       - Processing time: ~10-15 seconds per resume
    
    5. **Review Results**
       - View ranked candidates
       - Export results (CSV, JSON, Excel)
       - Download individual reports
    """)

# === STEP 1: JOB DESCRIPTION ===
st.markdown("## 📋 Step 1: Job Description")

col1, col2 = st.columns([3, 1])

with col1:
    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="""Example:
Senior Software Engineer - AI/ML

Requirements:
- 5+ years Python development
- Experience with LLMs, NLP, and ML frameworks
- Strong system design skills
- Bachelor's degree in Computer Science

Responsibilities:
- Build AI-powered applications
- Design scalable ML systems
- Lead technical initiatives
"""
    )

with col2:
    st.markdown("**Quick Load**")
    sample_jd = st.selectbox(
        "Sample JD",
        ["Custom", "Senior Engineer", "Data Scientist", "Product Manager"]
    )
    
    if sample_jd == "Senior Engineer" and st.button("Load Sample"):
        job_description = """Senior Software Engineer - AI/ML
        
Requirements:
- 5+ years Python development
- Experience with LLMs and NLP
- Strong ML/AI background
- Bachelor's in CS or related field

Responsibilities:
- Build AI-powered applications
- Design scalable ML systems
- Lead technical teams"""
        st.rerun()

# === STEP 2: RESUME UPLOAD ===
st.markdown("---")
st.markdown("## 📁 Step 2: Upload Resumes")

uploaded_resumes = st.file_uploader(
    "Upload Resume PDFs (Max 50)",
    type=['pdf'],
    accept_multiple_files=True,
    help="Select multiple PDF files at once. Hold Ctrl/Cmd to select multiple files."
)

if uploaded_resumes:
    st.success(f"✅ Uploaded {len(uploaded_resumes)} resume(s)")
    
    # Show list
    with st.expander(f"📄 View Uploaded Files ({len(uploaded_resumes)})", expanded=False):
        for i, resume in enumerate(uploaded_resumes, 1):
            st.write(f"{i}. {resume.name} ({resume.size / 1024:.1f} KB)")
    
    if len(uploaded_resumes) > 50:
        st.error("❌ Maximum 50 resumes allowed per batch. Please reduce the number of files.")

# === STEP 3: SETTINGS ===
st.markdown("---")
st.markdown("## ⚙️ Step 3: Processing Settings")

col1, col2, col3, col4 = st.columns(4)

with col1:
    min_threshold = st.slider("Min Match Score", 0, 100, 50, step=5,
                              help="Filter results below this score")

with col2:
    top_n = st.number_input("Show Top N", min_value=5, max_value=50, value=10, step=5,
                           help="Number of top candidates to display")

# === STEP 4: PROCESS BATCH ===
st.markdown("---")
st.markdown("## 🚀 Step 4: Process Batch")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    process_button = st.button(
        "📦 Process Batch",
        disabled=not (job_description and uploaded_resumes and len(uploaded_resumes) <= 50),
        type="primary",
        help="Start batch processing"
    )

with col2:
    estimated_time = len(uploaded_resumes) * 12 if uploaded_resumes else 0
    st.metric("Estimated Time", f"{estimated_time}s")

with col3:
    estimated_cost = len(uploaded_resumes) * 0.15 if uploaded_resumes else 0
    st.metric("Estimated Cost", f"${estimated_cost:.2f}")

# Process batch
if process_button:
    st.session_state.processing = True
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    total_cost = 0
    start_time = datetime.now()
    
    try:
        # Initialize matcher
        matcher = ResumeMatcher()
        
        # Process each resume
        for i, resume_file in enumerate(uploaded_resumes):
            status_text.text(f"Processing {i+1}/{len(uploaded_resumes)}: {resume_file.name}")
            
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(resume_file.getbuffer())
                tmp_path = tmp_file.name
            
            try:
                # Match resume
                result = matcher.match_resume_to_job(
                    resume=tmp_path,
                    job_description=job_description
                )
                
                # Store result
                results.append({
                    'filename': resume_file.name,
                    'overall_score': result.overall_score,
                    'recommendation': result.recommendation,
                    'semantic_score': result.semantic_similarity * 100,
                    'matched_skills': len(result.matched_skills),
                    'missing_skills': len(result.missing_critical_skills),
                    'cost': result.llm_cost or 0,
                    'confidence': result.confidence * 100,
                    'result_object': result  # Store full object for details
                })
                
                total_cost += (result.llm_cost or 0)
                
            except Exception as e:
                st.warning(f"⚠️ Error processing {resume_file.name}: {str(e)}")
                results.append({
                    'filename': resume_file.name,
                    'overall_score': 0,
                    'recommendation': 'error',
                    'error': str(e)
                })
            
            # Clean up
            Path(tmp_path).unlink()
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_resumes))
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Store results
        st.session_state.batch_results = {
            'results': results,
            'total_processed': len(uploaded_resumes),
            'total_cost': total_cost,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.processing = False
        progress_bar.progress(1.0)
        status_text.text("✅ Batch processing complete!")
        
        st.success(f"✅ Processed {len(results)} resumes in {processing_time:.1f}s")
        st.balloons()
        
    except Exception as e:
        st.session_state.processing = False
        st.error(f"❌ Batch Processing Error: {str(e)}")
        st.exception(e)

# === STEP 5: RESULTS ===
if st.session_state.batch_results:
    batch_data = st.session_state.batch_results
    results_df = pd.DataFrame([r for r in batch_data['results'] if 'error' not in r])
    
    # Check if we have any successful results
    if len(results_df) == 0:
        st.error("❌ No resumes were successfully processed. Please check the errors above.")
        st.stop()
    
    # Sort by score
    results_df = results_df.sort_values('overall_score', ascending=False)
    
    # Filter by threshold
    filtered_df = results_df[results_df['overall_score'] >= min_threshold]
    
    st.markdown("---")
    st.markdown("## 📊 Batch Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Processed", batch_data['total_processed'])
    
    with col2:
        st.metric("Above Threshold", len(filtered_df))
    
    with col3:
        st.metric("Processing Time", f"{batch_data['processing_time']:.1f}s")
    
    with col4:
        st.metric("Total Cost", f"${batch_data['total_cost']:.2f}")
    
    # Score distribution
    st.markdown("### 📈 Score Distribution")
    
    fig = px.histogram(results_df, x='overall_score', nbins=20,
                      title="Overall Match Score Distribution",
                      labels={'overall_score': 'Match Score (%)', 'count': 'Number of Candidates'})
    fig.add_vline(x=min_threshold, line_dash="dash", line_color="red",
                 annotation_text=f"Threshold: {min_threshold}%")
    st.plotly_chart(fig, use_container_width=True)
    
    # Top candidates
    st.markdown(f"### 🏆 Top {min(top_n, len(filtered_df))} Candidates")
    
    for rank, (i, row) in enumerate(filtered_df.head(top_n).iterrows(), start=1):
        
        if rank == 1:
            rank_class = "rank-1"
            emoji = "🥇"
        elif rank == 2:
            rank_class = "rank-2"
            emoji = "🥈"
        elif rank == 3:
            rank_class = "rank-3"
            emoji = "🥉"
        else:
            rank_class = "rank-default"
            emoji = f"#{rank}"
        
        with st.expander(f"{emoji} **{row['filename']}** - {row['overall_score']:.1f}%", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Overall Score", f"{row['overall_score']:.1f}%")
            
            with col2:
                st.metric("Recommendation", row['recommendation'].replace('_', ' ').title())
            
            with col3:
                st.metric("Matched Skills", row['matched_skills'])
            
            with col4:
                st.metric("Confidence", f"{row['confidence']:.0f}%")
            
            # Show dimensional scores if available
            if 'result_object' in row:
                result_obj = row['result_object']
                
                st.markdown("**Dimensional Scores:**")
                for dim in result_obj.dimension_scores:
                    st.progress(dim.score / 100.0, text=f"{dim.dimension}: {dim.score:.1f}%")
    
    # Comparison table
    st.markdown("---")
    st.markdown("### 📊 Detailed Comparison")
    
    # Prepare display dataframe
    display_df = filtered_df[['filename', 'overall_score', 'recommendation', 
                              'matched_skills', 'missing_skills', 'confidence']].copy()
    
    display_df.columns = ['Filename', 'Score (%)', 'Recommendation', 
                         'Matched Skills', 'Missing Skills', 'Confidence (%)']
    
    display_df['Score (%)'] = display_df['Score (%)'].round(1)
    display_df['Confidence (%)'] = display_df['Confidence (%)'].round(0)
    display_df['Recommendation'] = display_df['Recommendation'].str.replace('_', ' ').str.title()
    
    st.dataframe(display_df, hide_index=True, use_container_width=True)
    
    # Export options
    st.markdown("---")
    st.markdown("### 📥 Export Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # CSV export
        csv_data = display_df.to_csv(index=False)
        st.download_button(
            "📊 Download CSV",
            data=csv_data,
            file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # JSON export
        json_data = results_df.drop('result_object', axis=1, errors='ignore').to_json(orient='records', indent=2)
        st.download_button(
            "📄 Download JSON",
            data=json_data,
            file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col3:
        # Summary report
        summary_text = f"""BATCH PROCESSING SUMMARY
========================

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Processed: {batch_data['total_processed']}
Above Threshold ({min_threshold}%): {len(filtered_df)}
Processing Time: {batch_data['processing_time']:.1f}s
Total Cost: ${batch_data['total_cost']:.2f}

TOP 10 CANDIDATES:
"""
        for rank, (i, row) in enumerate(filtered_df.head(10).iterrows(), start=1):
            summary_text += f"\n{rank}. {row['filename']} - {row['overall_score']:.1f}%"
        
        st.download_button(
            "📝 Download Summary",
            data=summary_text,
            file_name=f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    with col4:
        if st.button("🔄 New Batch"):
            st.session_state.batch_results = None
            st.rerun()
    
    # Insights
    st.markdown("---")
    st.markdown("### 💡 Key Insights")
    
    avg_score = results_df['overall_score'].mean()
    strong_matches = len(results_df[results_df['recommendation'] == 'strong_match'])
    good_matches = len(results_df[results_df['recommendation'] == 'good_match'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Candidate Quality:**
        - Average Match Score: **{avg_score:.1f}%**
        - Strong Matches: **{strong_matches}** ({strong_matches/len(results_df)*100:.1f}%)
        - Good Matches: **{good_matches}** ({good_matches/len(results_df)*100:.1f}%)
        """)
    
    with col2:
        st.markdown(f"""
        **Processing Details:**
        - Total Processed: **{len(results_df)}** resumes
        - Total Cost: **${batch_data['total_cost']:.2f}**
        - Avg Cost per Resume: **${batch_data['total_cost']/len(results_df):.3f}**
        - Processing Time: **{batch_data['processing_time']:.1f}s**
        """)
    
    # Recommendation distribution
    st.markdown("### 📊 Recommendation Distribution")
    
    rec_counts = results_df['recommendation'].value_counts()
    rec_df = pd.DataFrame({
        'Recommendation': rec_counts.index.str.replace('_', ' ').str.title(),
        'Count': rec_counts.values
    })
    
    fig = px.pie(rec_df, values='Count', names='Recommendation',
                title="Candidates by Recommendation Category",
                color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig, use_container_width=True)

else:
    # No results yet
    st.info("👆 Upload resumes and job description, then click 'Process Batch' to get started")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>📦 Batch Processing Engine</strong></p>
    <p>Powered by AI • Process up to 50 resumes simultaneously • Fast and efficient screening</p>
</div>
""", unsafe_allow_html=True)
