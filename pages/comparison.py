"""
Candidate Comparison Page - Side-by-side candidate analysis
"""

import streamlit as st
import json
import plotly.graph_objects as go
from components.ui_components import *
from components.theme import BRAND_COLORS
from config import *

def render_candidate_comparison():
    """Render candidate comparison interface"""
    
    render_header(
        "Candidate Comparison Tool",
        "Compare candidates side-by-side with detailed analytics"
    )
    
    # Load candidates
    with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    # Load jobs for job-specific comparison
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    # Check if we have recent search results
    has_recent_search = 'last_search_job' in st.session_state and 'last_search_results' in st.session_state
    
    if has_recent_search:
        st.info(f"""
        💡 **Smart Defaults Loaded**  
        Comparing top 2 candidates from your last search for: **{st.session_state.last_search_job['title']}**
        """)
        
        # Get top 2 from last search
        top_candidates = st.session_state.last_search_results[:2]
        default_idx1 = next((i for i, c in enumerate(candidates) if c['id'] == top_candidates[0]['candidate']['id']), 0)
        default_idx2 = next((i for i, c in enumerate(candidates) if c['id'] == top_candidates[1]['candidate']['id']), 1) if len(top_candidates) > 1 else 1
        default_job_idx = next((i for i, j in enumerate(jobs) if j['id'] == st.session_state.last_search_job['id']), 0)
        compare_for_job_default = True
    else:
        default_idx1 = 0
        default_idx2 = 1
        default_job_idx = 0
        compare_for_job_default = False
    
    # Candidate selection
    st.markdown("### Select Candidates to Compare")
    
    col1, col2 = st.columns(2)
    
    with col1:
        candidate1_idx = st.selectbox(
            "First Candidate",
            range(len(candidates)),
            index=default_idx1,
            format_func=lambda i: f"{candidates[i]['name']} - {candidates[i]['current_title']}",
            key="cand1_select"
        )
        candidate1 = candidates[candidate1_idx]
    
    with col2:
        candidate2_idx = st.selectbox(
            "Second Candidate",
            range(len(candidates)),
            index=default_idx2,
            format_func=lambda i: f"{candidates[i]['name']} - {candidates[i]['current_title']}",
            key="cand2_select"
        )
        candidate2 = candidates[candidate2_idx]
    
    if candidate1['id'] == candidate2['id']:
        st.warning("⚠️ Please select two different candidates to compare")
        return
    
    # Optional: Job-specific comparison
    compare_for_job = st.checkbox("Compare for specific job position", value=compare_for_job_default)
    
    selected_job = None
    if compare_for_job:
        job_idx = st.selectbox(
            "Select Position",
            range(len(jobs)),
            index=default_job_idx,
            format_func=lambda i: f"{jobs[i]['title']} - {jobs[i]['service_line']}"
        )
        selected_job = jobs[job_idx]
    
    if st.button("📊 Generate Comparison", width="stretch", type="primary"):
        render_comparison_results(candidate1, candidate2, selected_job)

def render_comparison_results(cand1, cand2, job=None):
    """Render detailed comparison results"""
    
    st.markdown("---")
    st.markdown("### Comparison Results")
    
    # Basic info comparison
    col1, col2 = st.columns(2)
    
    with col1:
        render_candidate_card(cand1)
    
    with col2:
        render_candidate_card(cand2)
    
    st.markdown("---")
    
    # Comparison tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", "🎯 Skills Analysis", "💼 Experience", "📈 Visualizations"
    ])
    
    with tab1:
        render_overview_comparison(cand1, cand2, job)
    
    with tab2:
        render_skills_comparison(cand1, cand2, job)
    
    with tab3:
        render_experience_comparison(cand1, cand2)
    
    with tab4:
        render_comparison_visualizations(cand1, cand2, job)

def render_overview_comparison(cand1, cand2, job):
    """Render high-level comparison"""
    
    st.markdown("#### Quick Comparison")
    
    # Create comparison table
    comparison_data = {
        "Attribute": [
            "Service Line",
            "Experience Level",
            "Years of Experience",
            "Location",
            "Education",
            "Certifications",
            "Languages",
            "Availability"
        ],
        cand1['name']: [
            cand1.get('service_line', 'N/A'),
            cand1.get('experience_level', 'N/A'),
            f"{cand1.get('years_experience', 0)} years",
            cand1.get('location', 'N/A'),
            cand1.get('education', ['N/A'])[0] if isinstance(cand1.get('education'), list) else 'N/A',
            len(cand1.get('certifications', [])),
            len(cand1.get('languages', [])),
            cand1.get('availability', 'N/A')
        ],
        cand2['name']: [
            cand2.get('service_line', 'N/A'),
            cand2.get('experience_level', 'N/A'),
            f"{cand2.get('years_experience', 0)} years",
            cand2.get('location', 'N/A'),
            cand2.get('education', ['N/A'])[0] if isinstance(cand2.get('education'), list) else 'N/A',
            len(cand2.get('certifications', [])),
            len(cand2.get('languages', [])),
            cand2.get('availability', 'N/A')
        ]
    }
    
    import pandas as pd
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, width="stretch", hide_index=True)
    
    # If job is selected, show matching scores
    if job:
        st.markdown("---")
        st.markdown("#### Match Scores for Selected Position")
        
        # Calculate simplified match scores
        score1 = calculate_simple_match_score(cand1, job)
        score2 = calculate_simple_match_score(cand2, job)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
                <div class="{'comparison-winner' if score1 > score2 else ''}" style="padding: 1rem; border-radius: 0.5rem;">
                    <h4>{cand1['name']}</h4>
                    <div style="font-size: 2rem; font-weight: 700; color: {BRAND_COLORS['primary']};">
                        {score1:.0%}
                    </div>
                    <div style="color: {BRAND_COLORS['text_secondary']};">
                        Overall Match
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="{'comparison-winner' if score2 > score1 else ''}" style="padding: 1rem; border-radius: 0.5rem;">
                    <h4>{cand2['name']}</h4>
                    <div style="font-size: 2rem; font-weight: 700; color: {BRAND_COLORS['primary']};">
                        {score2:.0%}
                    </div>
                    <div style="color: {BRAND_COLORS['text_secondary']};">
                        Overall Match
                    </div>
                </div>
            """, unsafe_allow_html=True)

def render_skills_comparison(cand1, cand2, job):
    """Render detailed skills comparison"""
    
    st.markdown("#### Skills Analysis")
    
    skills1 = set([s.lower() for s in cand1.get('skills', [])])
    skills2 = set([s.lower() for s in cand2.get('skills', [])])
    
    # Calculate overlaps
    common_skills = skills1 & skills2
    unique1 = skills1 - skills2
    unique2 = skills2 - skills1
    
    # Show overlap chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = render_skill_comparison_chart(list(skills1), list(skills2))
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.markdown("##### Statistics")
        render_metric_card("Common Skills", str(len(common_skills)))
        render_metric_card(f"{cand1['name']} Unique", str(len(unique1)))
        render_metric_card(f"{cand2['name']} Unique", str(len(unique2)))
    
    st.markdown("---")
    
    # If job is selected, show relevance to job requirements
    if job:
        st.markdown("#### Relevance to Job Requirements")
        
        required_skills = set([s.lower() for s in job.get('required_skills', [])])
        
        match1 = skills1 & required_skills
        match2 = skills2 & required_skills
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"##### {cand1['name']}")
            st.markdown(f"**Match:** {len(match1)}/{len(required_skills)} skills ({len(match1)/len(required_skills):.0%})")
            if match1:
                st.markdown("**Matched Skills:**")
                for skill in sorted(match1)[:10]:
                    st.markdown(f"• {skill.title()}")
        
        with col2:
            st.markdown(f"##### {cand2['name']}")
            st.markdown(f"**Match:** {len(match2)}/{len(required_skills)} skills ({len(match2)/len(required_skills):.0%})")
            if match2:
                st.markdown("**Matched Skills:**")
                for skill in sorted(match2)[:10]:
                    st.markdown(f"• {skill.title()}")
    
    # Detailed skill lists
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.expander(f"Common Skills ({len(common_skills)})"):
            for skill in sorted(common_skills):
                st.markdown(f"• {skill.title()}")
    
    with col2:
        with st.expander(f"{cand1['name']} Unique ({len(unique1)})"):
            for skill in sorted(unique1):
                st.markdown(f"• {skill.title()}")
    
    with col3:
        with st.expander(f"{cand2['name']} Unique ({len(unique2)})"):
            for skill in sorted(unique2):
                st.markdown(f"• {skill.title()}")

def render_experience_comparison(cand1, cand2):
    """Render experience comparison"""
    
    st.markdown("#### Experience Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"##### {cand1['name']}")
        st.markdown(f"**Total Experience:** {cand1.get('years_experience', 0)} years")
        st.markdown(f"**Level:** {cand1.get('experience_level', 'N/A')}")
        
        if cand1.get('work_history'):
            st.markdown("**Work History:**")
            for i, work in enumerate(cand1['work_history'][:3], 1):
                st.markdown(f"{i}. **{work.get('title', 'N/A')}** at {work.get('company', 'N/A')}")
                st.markdown(f"   *{work.get('start_date', '')} - {work.get('end_date', '')}*")
    
    with col2:
        st.markdown(f"##### {cand2['name']}")
        st.markdown(f"**Total Experience:** {cand2.get('years_experience', 0)} years")
        st.markdown(f"**Level:** {cand2.get('experience_level', 'N/A')}")
        
        if cand2.get('work_history'):
            st.markdown("**Work History:**")
            for i, work in enumerate(cand2['work_history'][:3], 1):
                st.markdown(f"{i}. **{work.get('title', 'N/A')}** at {work.get('company', 'N/A')}")
                st.markdown(f"   *{work.get('start_date', '')} - {work.get('end_date', '')}*")

def render_comparison_visualizations(cand1, cand2, job):
    """Render advanced comparison visualizations"""
    
    st.markdown("#### Visual Comparison")
    
    # Radar chart comparison
    if job:
        st.markdown("##### Multi-Criteria Comparison for Position")
        
        categories = ['Skills', 'Experience', 'Education', 'Certifications', 'Languages']
        
        # Calculate normalized scores
        scores1 = calculate_category_scores(cand1, job)
        scores2 = calculate_category_scores(cand2, job)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=scores1,
            theta=categories,
            fill='toself',
            name=cand1['name'],
            line_color=BRAND_COLORS['primary']
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=scores2,
            theta=categories,
            fill='toself',
            name=cand2['name'],
            line_color=BRAND_COLORS['secondary']
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig, width="stretch")
    
    # Experience comparison bar chart
    st.markdown("##### Experience Timeline")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=cand1['name'],
        x=['Total Experience'],
        y=[cand1.get('years_experience', 0)],
        marker_color=BRAND_COLORS['primary']
    ))
    
    fig.add_trace(go.Bar(
        name=cand2['name'],
        x=['Total Experience'],
        y=[cand2.get('years_experience', 0)],
        marker_color=BRAND_COLORS['secondary']
    ))
    
    fig.update_layout(
        barmode='group',
        height=300,
        yaxis_title="Years"
    )
    
    st.plotly_chart(fig, width="stretch")

def calculate_simple_match_score(candidate, job):
    """Calculate simplified match score"""
    # Simplified scoring logic
    cand_skills = set([s.lower() for s in candidate.get('skills', [])])
    req_skills = set([s.lower() for s in job.get('required_skills', [])])
    
    skill_score = len(cand_skills & req_skills) / len(req_skills) if req_skills else 0
    
    # Experience score
    exp = candidate.get('years_experience', 0)
    min_exp = job.get('years_experience_min', 0)
    max_exp = job.get('years_experience_max', 100)
    
    if min_exp <= exp <= max_exp:
        exp_score = 1.0
    else:
        exp_score = 0.5
    
    # Service line match
    service_match = 1.0 if candidate.get('service_line') == job.get('service_line') else 0.5
    
    return (skill_score * 0.5 + exp_score * 0.3 + service_match * 0.2)

def calculate_category_scores(candidate, job):
    """Calculate scores for radar chart categories"""
    
    # Skills
    cand_skills = set([s.lower() for s in candidate.get('skills', [])])
    req_skills = set([s.lower() for s in job.get('required_skills', [])])
    skill_score = len(cand_skills & req_skills) / len(req_skills) if req_skills else 0
    
    # Experience
    exp = candidate.get('years_experience', 0)
    min_exp = job.get('years_experience_min', 0)
    max_exp = job.get('years_experience_max', 100)
    exp_score = 1.0 if min_exp <= exp <= max_exp else 0.6
    
    # Education (normalized)
    edu_score = 0.8 if candidate.get('education') else 0.5
    
    # Certifications (normalized)
    cert_count = len(candidate.get('certifications', []))
    cert_score = min(cert_count / 3, 1.0)
    
    # Languages
    lang_count = len(candidate.get('languages', []))
    lang_score = min(lang_count / 3, 1.0)
    
    return [skill_score, exp_score, edu_score, cert_score, lang_score]