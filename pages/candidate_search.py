"""
Candidate Search Page - Enhanced matching with professional UI
ULTRA SIMPLIFIED: Automatic dormant talent discovery - no buttons, just results
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
    if st.button("🔍 Find Matching Candidates", use_container_width=True, type="primary"):
        
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
            
            # ⭐ AUTOMATIC Dormant Talent Discovery - No buttons!
            st.markdown("---")
            render_automatic_dormant_section(selected_job)
        
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
                st.plotly_chart(fig, use_container_width=True, key=f"score_breakdown_{candidate['id']}_{i}")
            
            with col2:
                st.markdown("#### Component Scores")
                st.markdown(f"**Semantic:** {scores['semantic']:.1%}")
                st.markdown(f"**Skills:** {scores['skills']:.1%}")
                st.markdown(f"**Experience:** {scores['experience']:.1%}")
                st.markdown(f"**Location:** {scores['location']:.1%}")
                st.markdown(f"**Profile Score:** 60%")
            
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
        
        st.plotly_chart(fig, use_container_width=True, key="analytics_score_dist")
    
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
        
        st.plotly_chart(fig, use_container_width=True, key="analytics_quality_pie")
    
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


def render_automatic_dormant_section(job):
    """
    ⭐ ULTRA SIMPLIFIED: Automatic dormant talent discovery
    NO BUTTONS - Just shows top 5 dormant candidates automatically
    """
    
    st.markdown("## 💎 Hidden Gems - Dormant Talent")
    st.markdown("Past candidates who didn't apply to this position but may now be perfect fits")
    
    # Initialize dormant detector
    if 'dormant_detector' not in st.session_state:
        from src.search.dormant_detector import DormantTalentDetector
        try:
            st.session_state.dormant_detector = DormantTalentDetector(
                st.session_state.matching_engine
            )
        except Exception as e:
            st.error(f"Could not initialize dormant talent detector: {e}")
            return
    
    detector = st.session_state.dormant_detector
    
    # Check if we have any dormant candidates
    if not detector.dormant_candidates or len(detector.dormant_candidates) == 0:
        st.info("💡 No dormant candidates in the system yet. They will appear here after candidates become inactive for 6+ months.")
        return
    
    # AUTOMATICALLY search for top 5 dormant candidates
    # Use a lower threshold (0.60) to ensure we get results
    with st.spinner("🔍 Discovering dormant talent..."):
        try:
            # Search with moderate threshold
            dormant_matches = detector.detect_dormant_matches(job, min_score=0.60)
            
            # Take top 5
            dormant_matches = dormant_matches[:5]
            
        except Exception as e:
            st.error(f"Error finding dormant candidates: {e}")
            with st.expander("🔍 Technical Details"):
                import traceback
                st.code(traceback.format_exc())
            return
    
    # Display results
    if dormant_matches and len(dormant_matches) > 0:
        # Success metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_months = sum(m['evolution']['months_dormant'] for m in dormant_matches) / len(dormant_matches)
            st.metric("Avg Time Since Last Application", f"{avg_months:.0f} months")
        with col2:
            avg_score = sum(m['scores']['total_with_evolution'] for m in dormant_matches) / len(dormant_matches)
            st.metric("Avg Match Score", f"{avg_score:.0%}")
        with col3:
            st.metric("Top Dormant Candidates", len(dormant_matches))
        
        st.markdown("---")
        
        # Display each dormant candidate
        for i, match in enumerate(dormant_matches, 1):
            candidate = match['candidate']
            scores = match['scores']
            evolution = match['evolution']
            
            # Special dormant badge
            st.markdown(f"""
                <div style="background: linear-gradient(90deg, #FFE5B4 0%, #FFD700 100%); 
                            padding: 1rem; border-radius: 0.75rem; 
                            border-left: 5px solid #FFA500; margin-bottom: 1rem;
                            box-shadow: 0 2px 4px rgba(255,165,0,0.2);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.3rem;">💎</span>
                            <strong style="color: #8B4513; font-size: 1.1rem; margin-left: 0.5rem;">
                                DORMANT GEM #{i}
                            </strong>
                        </div>
                        <div style="text-align: right; color: #8B4513;">
                            <div style="font-size: 0.9rem;">Last applied <strong>{evolution['months_dormant']} months ago</strong></div>
                            <div style="font-size: 1.2rem; font-weight: bold;">{scores['total_with_evolution']:.0%} Match</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Candidate card
            render_candidate_card(candidate, scores['total_with_evolution'], None)
            
            # Compact info row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**📊 Base Score:** {scores['total']:.0%}")
                st.markdown(f"**🎯 Evolution Bonus:** +{scores['evolution']:.0%}")
            with col2:
                growth = evolution['growth_potential'].split(' - ')[0]
                if growth == "HIGH":
                    st.markdown(f"**📈 Growth:** 🔥 {growth}")
                elif growth == "MEDIUM":
                    st.markdown(f"**📈 Growth:** ⭐ {growth}")
                else:
                    st.markdown(f"**📈 Growth:** 📊 {growth}")
            with col3:
                st.markdown(f"**📧 {candidate['email']}**")
                st.markdown(f"**📱 {candidate['phone']}**")
            
            # Why they're a good match (evolution insight)
            with st.expander("💡 Why This Candidate Now?"):
                st.info(evolution['narrative'])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🎯 Key Skills:**")
                    st.markdown(", ".join(candidate['skills'][:8]))
                with col2:
                    st.markdown("**💼 Experience:**")
                    st.markdown(f"{candidate['years_experience']} years as {candidate['experience_level']}")
                    if candidate.get('company_history'):
                        st.markdown(f"**Companies:** {', '.join(candidate['company_history'][:2])}")
            
            st.markdown("---")
    
    else:
        # No dormant matches found
        st.info("""
            💡 **No dormant candidates match this position right now**
            
            This means:
            - All dormant candidates already applied to this job, OR
            - No dormant candidates have the required skills/experience
            
            *Dormant candidates appear here when past applicants become qualified for new positions.*
        """)