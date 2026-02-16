"""
Candidate Search Page - Enhanced matching with professional UI
"""

import streamlit as st
import json
import sys
from pathlib import Path
from components.ui_components import *
from components.theme import BRAND_COLORS
from config import *

sys.path.append(str(Path(__file__).parent.parent))
from src.search.matching_engine import MatchingEngine
from src.explainability.explainer import ExplainabilityEngine

def render_candidate_search():
    """Render enhanced candidate search interface"""
    
    render_header(
        "Intelligent Candidate Matching",
        "AI-powered semantic search with explainable recommendations"
    )
    
    # Initialize matching engine
    if 'matching_engine' not in st.session_state:
        with st.spinner("Initializing matching engine..."):
            st.session_state.matching_engine = MatchingEngine()
    
    # Load jobs
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    # Search interface
    st.markdown("### Select Position")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Job selection with better formatting
        job_options = [f"{j['title']} - {j['service_line']} ({j['location']})" for j in jobs]
        selected_idx = st.selectbox(
            "Choose the position to find candidates for:",
            range(len(jobs)),
            format_func=lambda i: job_options[i]
        )
        selected_job = jobs[selected_idx]
    
    with col2:
        top_k = st.number_input("Number of Results", min_value=5, max_value=50, value=10)
    
    # Show selected job details
    with st.expander("📋 Position Details", expanded=False):
        render_job_card(selected_job)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Experience Required:** {selected_job['years_experience_min']}-{selected_job['years_experience_max']} years")
            st.markdown(f"**Contract:** {selected_job['contract_type']}")
        with col2:
            st.markdown(f"**Remote:** {selected_job.get('remote', 'No')}")
            st.markdown(f"**Travel:** {selected_job.get('travel_required', 'None')}")
        
        st.markdown(f"**Required Skills:** {', '.join(selected_job['required_skills'][:15])}")
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_location = st.selectbox("Location", ["All"] + FORVIS_LOCATIONS)
        
        with col2:
            filter_min_exp = st.number_input("Min Experience (years)", 0, 30, 0)
        
        with col3:
            filter_max_exp = st.number_input("Max Experience (years)", 0, 30, 30)
    
    # Build filters dict
    filters = {}
    if filter_location != "All":
        filters['location'] = filter_location
    if filter_min_exp > 0:
        filters['min_experience'] = filter_min_exp
    if filter_max_exp < 30:
        filters['max_experience'] = filter_max_exp
    
    # Search button
    if st.button("🔍 Find Matching Candidates", width="stretch", type="primary"):
        
        with st.spinner("Searching candidate pool..."):
            # Perform matching
            matches = st.session_state.matching_engine.match_candidates(
                selected_job,
                top_k=top_k,
                filters=filters if filters else None
            )
        
        if matches:
            st.success(f"✨ Found {len(matches)} matching candidates!")
            
            # Save to session state for smart comparison
            st.session_state.last_search_job = selected_job
            st.session_state.last_search_results = matches
            
            # Summary metrics
            avg_score = sum(m['scores']['total'] for m in matches) / len(matches)
            top_score = matches[0]['scores']['total']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                render_metric_card("Top Match", f"{top_score:.0%}")
            with col2:
                render_metric_card("Average Score", f"{avg_score:.0%}")
            with col3:
                render_metric_card("Candidates", str(len(matches)))
            
            st.markdown("---")
            
            # Results tabs
            tab1, tab2 = st.tabs(["👥 Ranked Results", "📊 Analytics"])
            
            with tab1:
                render_search_results(matches, selected_job)
            
            with tab2:
                render_search_analytics(matches)
        
        else:
            st.warning("No candidates found matching the criteria.")
            st.info("💡 Try relaxing filters or adjusting requirements")

def render_search_results(matches, job):
    """Render search results with professional cards"""
    
    for i, match in enumerate(matches, 1):
        candidate = match['candidate']
        scores = match['scores']
        breakdown = match['breakdown']
        
        # Candidate card
        render_candidate_card(candidate, scores['total'], i)
        
        # Expandable details
        with st.expander("View Detailed Analysis"):
            
            # Score breakdown visualization
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = render_score_breakdown(scores)
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                st.markdown("#### Component Scores")
                st.markdown(f"**Semantic:** {scores['semantic']:.1%}")
                st.markdown(f"**Skills:** {scores['skills']:.1%}")
                st.markdown(f"**Experience:** {scores['experience']:.1%}")
                st.markdown(f"**Location:** {scores['location']:.1%}")
            
            st.markdown("---")
            
            # Detailed explanation
            explanation = ExplainabilityEngine.generate_explanation(match)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ✅ Strengths")
                for strength in explanation['strengths']:
                    st.markdown(f"• {strength}")
            
            with col2:
                st.markdown("#### ⚠️ Considerations")
                if explanation['weaknesses']:
                    for weakness in explanation['weaknesses']:
                        st.markdown(f"• {weakness}")
                else:
                    st.markdown("• No significant weaknesses identified")
            
            st.markdown("---")
            
            # Recommendation
            rec = explanation['recommendation']
            color = get_score_color(rec['confidence'])
            
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color}22 0%, {color}11 100%); 
                            padding: 1rem; border-radius: 0.5rem; border-left: 4px solid {color};">
                    <div style="font-weight: 600; font-size: 1.1rem; color: {color}; margin-bottom: 0.5rem;">
                        {rec['decision']}
                    </div>
                    <div style="color: {BRAND_COLORS['text_primary']};">
                        {rec['rationale']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Contact info
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**📧 Email:** {candidate['email']}")
            with col2:
                st.markdown(f"**📱 Phone:** {candidate['phone']}")
        
        st.markdown("---")

def render_search_analytics(matches):
    """Render analytics for search results"""
    
    st.markdown("### Search Results Analytics")
    
    # Score distribution
    scores = [m['scores']['total'] for m in matches]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Score Distribution")
        
        # Histogram
        import plotly.graph_objects as go
        fig = go.Figure(data=[go.Histogram(
            x=scores,
            nbinsx=10,
            marker_color=BRAND_COLORS['primary']
        )])
        
        fig.update_layout(
            xaxis_title="Match Score",
            yaxis_title="Number of Candidates",
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.markdown("#### Quality Tiers")
        
        excellent = sum(1 for s in scores if s >= 0.85)
        good = sum(1 for s in scores if 0.75 <= s < 0.85)
        moderate = sum(1 for s in scores if 0.65 <= s < 0.75)
        low = sum(1 for s in scores if s < 0.65)
        
        fig = go.Figure(data=[go.Pie(
            labels=['Excellent (85%+)', 'Good (75-85%)', 'Moderate (65-75%)', 'Below 65%'],
            values=[excellent, good, moderate, low],
            marker_colors=[BRAND_COLORS['success'], BRAND_COLORS['info'], 
                          BRAND_COLORS['warning'], BRAND_COLORS['danger']],
            hole=.4
        )])
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, width="stretch")
    
    # Component analysis
    st.markdown("#### Component Score Analysis")
    
    avg_semantic = sum(m['scores']['semantic'] for m in matches) / len(matches)
    avg_skills = sum(m['scores']['skills'] for m in matches) / len(matches)
    avg_exp = sum(m['scores']['experience'] for m in matches) / len(matches)
    avg_loc = sum(m['scores']['location'] for m in matches) / len(matches)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Avg Semantic", f"{avg_semantic:.0%}")
    with col2:
        render_metric_card("Avg Skills", f"{avg_skills:.0%}")
    with col3:
        render_metric_card("Avg Experience", f"{avg_exp:.0%}")
    with col4:
        render_metric_card("Avg Location", f"{avg_loc:.0%}")