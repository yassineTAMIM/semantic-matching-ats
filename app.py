# COPY THIS TO REPLACE app.py
# Includes: Export CSV, Performance Cache, Better Progress

"""
Streamlit UI - Enhanced with Quick Wins
"""

import streamlit as st
import json
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

sys.path.append(str(Path(__file__).parent))

from config import *
from src.search.matching_engine import MatchingEngine
from src.search.dormant_detector import DormantTalentDetector
from src.explainability.explainer import ExplainabilityEngine

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .candidate-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'matching_engine' not in st.session_state:
    with st.spinner("🚀 Initializing matching engine..."):
        st.session_state.matching_engine = MatchingEngine()
        st.session_state.dormant_detector = DormantTalentDetector(st.session_state.matching_engine)

if 'jobs_data' not in st.session_state:
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        st.session_state.jobs_data = json.load(f)

if 'candidates_data' not in st.session_state:
    with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
        st.session_state.candidates_data = json.load(f)

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# ============= QUICK WIN 1: PERFORMANCE CACHE =============
@st.cache_data(ttl=3600, show_spinner=False)
def cached_match_candidates(job_id, top_k, filters_str):
    """Cached matching for performance"""
    engine = st.session_state.matching_engine
    job = next(j for j in st.session_state.jobs_data if j['id'] == job_id)
    filters = eval(filters_str) if filters_str != 'None' else None
    return engine.match_candidates(job, top_k=top_k, filters=filters)

def get_score_class(score):
    if score >= 0.85:
        return "score-excellent"
    elif score >= 0.75:
        return "score-good"
    else:
        return "score-moderate"

def display_candidate_card(match, rank):
    candidate = match['candidate']
    scores = match['scores']
    
    with st.container():
        st.markdown(f"""
        <div class="candidate-card">
            <h3>#{rank} - {candidate['name']}</h3>
            <p><strong>{candidate['current_title']}</strong> | {candidate['service_line']}</p>
            <p>📍 {candidate['location']} | 💼 {candidate['years_experience']} years</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Score", f"{scores['total']:.1%}")
        with col2:
            st.metric("Semantic", f"{scores['semantic']:.1%}")
        with col3:
            st.metric("Skills", f"{scores['skills']:.1%}")
        with col4:
            st.metric("Experience", f"{scores['experience']:.1%}")
        with col5:
            st.metric("Location", f"{scores['location']:.1%}")
        
        with st.expander("📊 View Detailed Analysis"):
            explanation = ExplainabilityEngine.generate_explanation(match)
            
            st.markdown(f"**Summary:** {explanation['summary']}")
            
            st.markdown("**Strengths:**")
            for strength in explanation['strengths']:
                st.markdown(f"✅ {strength}")
            
            if explanation['weaknesses']:
                st.markdown("**Considerations:**")
                for weakness in explanation['weaknesses']:
                    st.markdown(f"⚠️ {weakness}")
            
            st.markdown("**Recommendation:**")
            rec = explanation['recommendation']
            st.info(f"**{rec['decision']}** - {rec['rationale']}")
        
        if st.button(f"📧 Contact {candidate['name']}", key=f"contact_{candidate['id']}"):
            st.success(f"Email: {candidate['email']} | Phone: {candidate['phone']}")

def main():
    st.markdown(f'<div class="main-header">{APP_ICON} {APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #666;'>{APP_DESCRIPTION}</p>", unsafe_allow_html=True)
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["🔍 Candidate Search", "🔔 Dormant Talent Alerts", "📊 Analytics Dashboard", "ℹ️ About"]
    )
    
    # Statistics in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Statistics")
    
    total_candidates = len(st.session_state.candidates_data)
    dormant_count = sum(1 for c in st.session_state.candidates_data if c.get('is_dormant', False))
    total_jobs = len(st.session_state.jobs_data)
    
    st.sidebar.metric("Total Candidates", f"{total_candidates:,}")
    st.sidebar.metric("Dormant Candidates", f"{dormant_count:,}")
    st.sidebar.metric("Active Jobs", f"{total_jobs:,}")
    
    # Search history in sidebar
    if st.session_state.search_history:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🕐 Recent Searches")
        for search in st.session_state.search_history[:5]:
            st.sidebar.caption(f"🔍 {search['job']}")
            st.sidebar.caption(f"   {search['timestamp']} - {search['results']} matches")
    
    if page == "🔍 Candidate Search":
        candidate_search_page()
    elif page == "🔔 Dormant Talent Alerts":
        dormant_alerts_page()
    elif page == "📊 Analytics Dashboard":
        analytics_page()
    else:
        about_page()

def candidate_search_page():
    st.header("🔍 Candidate Search & Matching")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        job_options = [f"{job['id']} - {job['title']} ({job['service_line']})" 
                      for job in st.session_state.jobs_data]
        selected_job_str = st.selectbox("Select Job Position", job_options)
        selected_job_id = selected_job_str.split(" - ")[0]
        selected_job = next(j for j in st.session_state.jobs_data if j['id'] == selected_job_id)
    
    with col2:
        top_k = st.slider("Number of Candidates", 5, 20, TOP_K_CANDIDATES)
    
    with st.expander("📋 Job Details", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Service Line:** {selected_job['service_line']}")
            st.write(f"**Location:** {selected_job['location']}")
        with col2:
            st.write(f"**Experience:** {selected_job['experience_level']}")
            st.write(f"**Years:** {selected_job['years_experience_min']}-{selected_job['years_experience_max']}")
        with col3:
            st.write(f"**Contract:** {selected_job['contract_type']}")
            st.write(f"**Remote:** {selected_job['remote']}")
        
        st.write(f"**Required Skills:** {', '.join(selected_job['required_skills'][:10])}")
    
    with st.expander("🔧 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_location = st.selectbox("Location Filter", ["All"] + FORVIS_LOCATIONS)
        with col2:
            filter_min_exp = st.number_input("Min Experience (years)", 0, 30, 0)
        with col3:
            filter_max_exp = st.number_input("Max Experience (years)", 0, 30, 30)
    
    filters = {}
    if filter_location != "All":
        filters['location'] = filter_location
    if filter_min_exp > 0:
        filters['min_experience'] = filter_min_exp
    if filter_max_exp < 30:
        filters['max_experience'] = filter_max_exp
    
    # ============= QUICK WIN 2: BETTER PROGRESS =============
    if st.button("🚀 Find Candidates", type="primary"):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Generating job embedding...")
            progress_bar.progress(20)
            time.sleep(0.3)
            
            status_text.text("🔎 Searching candidate pool...")
            progress_bar.progress(40)
            
            # Use cached matching
            matches = cached_match_candidates(
                selected_job['id'],
                top_k,
                str(filters) if filters else 'None'
            )
            
            progress_bar.progress(70)
            status_text.text("📊 Calculating multi-criteria scores...")
            time.sleep(0.3)
            
            progress_bar.progress(90)
            status_text.text("✅ Complete!")
            progress_bar.progress(100)
            time.sleep(0.5)
            
            status_text.empty()
            progress_bar.empty()
            
            if matches:
                st.balloons()
                st.success(f"✨ Found {len(matches)} matching candidates!")
                
                # Save to history
                st.session_state.search_history.insert(0, {
                    'job': selected_job['title'],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'results': len(matches),
                    'top_score': matches[0]['scores']['total']
                })
                st.session_state.search_history = st.session_state.search_history[:10]
                
                # ============= QUICK WIN 3: EXPORT CSV =============
                col1, col2 = st.columns(2)
                with col1:
                    export_data = []
                    for match in matches:
                        c = match['candidate']
                        s = match['scores']
                        export_data.append({
                            'Name': c['name'],
                            'Title': c['current_title'],
                            'Experience': f"{c['years_experience']} years",
                            'Location': c['location'],
                            'Total Score': f"{s['total']:.1%}",
                            'Semantic': f"{s['semantic']:.1%}",
                            'Skills': f"{s['skills']:.1%}",
                            'Email': c['email'],
                            'Phone': c['phone']
                        })
                    
                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download Shortlist (CSV)",
                        csv,
                        f"shortlist_{selected_job['id']}_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        key='download-csv'
                    )
                
                with col2:
                    share_text = f"Top Candidates for {selected_job['title']}:\n\n"
                    for i, match in enumerate(matches[:5], 1):
                        c = match['candidate']
                        share_text += f"{i}. {c['name']} ({c['current_title']}) - {match['scores']['total']:.0%} match\n"
                        share_text += f"   {c['email']} | {c['phone']}\n\n"
                    
                    st.download_button(
                        "📋 Copy Shortlist",
                        share_text,
                        f"shortlist_{selected_job['id']}.txt",
                        "text/plain"
                    )
                
                st.markdown("---")
                
                for i, match in enumerate(matches, 1):
                    display_candidate_card(match, i)
            else:
                st.warning("No candidates found matching the criteria.")
                st.info("💡 Try:\n- Relaxing filters\n- Broadening skill requirements\n- Adjusting experience range")
        
        except Exception as e:
            st.error(f"❌ Search failed: {str(e)}")
            st.info("Try refreshing the page or check the logs")

def dormant_alerts_page():
    st.header("🔔 Dormant Talent Rediscovery")
    
    st.info("""
    **What are Dormant Talents?**  
    Candidates who applied 6+ months ago may have gained new experience. 
    This feature automatically identifies them for new positions.
    """)
    
    job_options = [f"{job['id']} - {job['title']} ({job['service_line']})" 
                  for job in st.session_state.jobs_data]
    selected_job_str = st.selectbox("Scan for dormant matches for:", job_options)
    selected_job_id = selected_job_str.split(" - ")[0]
    selected_job = next(j for j in st.session_state.jobs_data if j['id'] == selected_job_id)
    
    min_score = st.slider("Minimum Match Score", 0.5, 0.9, DORMANT_MIN_SCORE, 0.05)
    
    if st.button("🔍 Scan Dormant Candidates", type="primary"):
        with st.spinner("Scanning dormant candidate pool..."):
            dormant_matches = st.session_state.dormant_detector.detect_dormant_matches(
                selected_job,
                min_score=min_score
            )
            summary = st.session_state.dormant_detector.generate_alert_summary(dormant_matches)
        
        if dormant_matches:
            st.success(f"🎯 {summary['message']}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Alerts", summary['total_alerts'])
            with col2:
                st.metric("Avg Match Score", f"{summary['avg_match_score']:.1%}")
            with col3:
                st.metric("Avg Months Dormant", f"{summary['avg_months_dormant']:.0f}")
            with col4:
                st.metric("Top Candidate", summary['top_candidate']['name'])
            
            st.markdown("---")
            
            for i, match in enumerate(dormant_matches, 1):
                candidate = match['candidate']
                scores = match['scores']
                evolution = match['evolution']
                
                with st.container():
                    st.markdown(f"""
                    <div class="candidate-card" style="border-left: 4px solid #ff6b6b;">
                        <h3>🚨 #{i} - {candidate['name']} (DORMANT TALENT)</h3>
                        <p><strong>{candidate['current_title']}</strong></p>
                        <p>📅 Last Applied: {evolution['last_application']} ({evolution['months_dormant']} months ago)</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Match Score", f"{scores['total']:.1%}")
                    with col2:
                        st.metric("Evolution Bonus", f"+{scores['evolution']:.1%}")
                    with col3:
                        st.metric("Total with Evolution", f"{scores['total_with_evolution']:.1%}")
                    with col4:
                        st.metric("Growth Potential", evolution['growth_potential'].split(' - ')[0])
                    
                    st.info(f"**Evolution Narrative:** {evolution['narrative']}")
        else:
            st.warning("No dormant candidates found above threshold.")

def analytics_page():
    st.header("📊 Analytics Dashboard")
    
    st.subheader("System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_candidates = len(st.session_state.candidates_data)
    dormant_count = sum(1 for c in st.session_state.candidates_data if c.get('is_dormant', False))
    
    with col1:
        st.metric("Total Candidates", f"{total_candidates:,}")
    with col2:
        st.metric("Active Candidates", f"{total_candidates - dormant_count:,}")
    with col3:
        st.metric("Dormant Candidates", f"{dormant_count:,}", 
                 f"{dormant_count/total_candidates:.1%}")
    with col4:
        st.metric("Open Positions", f"{len(st.session_state.jobs_data):,}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Candidates by Service Line")
        service_line_dist = {}
        for c in st.session_state.candidates_data:
            sl = c['service_line']
            service_line_dist[sl] = service_line_dist.get(sl, 0) + 1
        
        df = pd.DataFrame(list(service_line_dist.items()), columns=['Service Line', 'Count'])
        df = df.sort_values('Count', ascending=False)
        st.bar_chart(df.set_index('Service Line'))
    
    with col2:
        st.subheader("Jobs by Service Line")
        job_dist = {}
        for j in st.session_state.jobs_data:
            sl = j['service_line']
            job_dist[sl] = job_dist.get(sl, 0) + 1
        
        df_jobs = pd.DataFrame(list(job_dist.items()), columns=['Service Line', 'Count'])
        df_jobs = df_jobs.sort_values('Count', ascending=False)
        st.bar_chart(df_jobs.set_index('Service Line'))

def about_page():
    st.header("ℹ️ About This System")
    
    st.markdown("""
    ## Semantic Candidate Matching System
    
    AI-powered recruitment using Sentence-BERT and FAISS for intelligent matching.
    
    ### Key Features
    1. **Semantic Matching** - Understands meaning beyond keywords
    2. **Dormant Talent Rediscovery** - Reactivates past applicants ⭐
    3. **Multi-Criteria Scoring** - Weighted algorithm (semantic 70%, skills 20%, experience 7%, location 3%)
    4. **Transparent AI** - Full explainability
    
    ### Performance
    - Search time: <2 seconds (1000+ CVs)
    - Precision: 85%+
    - Memory: <1GB
    
    ### Team
    École Centrale Casablanca - Class of 2026
    - ABSRI Imad
    - EL BAHA Ali
    - EL MAIMOUNI Kenza
    - RAMDANI Nabil
    - TAMIM Yassine
    
    **Partner:** Forvis Mazars
    
    Version 1.1 - January 2025
    """)

if __name__ == "__main__":
    main()