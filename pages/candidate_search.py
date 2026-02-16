"""
Candidate Search Page - Enhanced matching with professional UI
FIXED: Unique plotly chart keys, persistent dormant settings
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
    
    # Initialize dormant settings in session state
    if 'dormant_min_score' not in st.session_state:
        st.session_state.dormant_min_score = 0.60  # Default to 60%
    if 'dormant_top_k' not in st.session_state:
        st.session_state.dormant_top_k = 10
    
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
            
            # ⭐ Dormant Talent Section
            st.markdown("---")
            render_dormant_talent_section(selected_job)
        
        else:
            st.warning("No candidates found matching the criteria.")
            st.info("💡 Try relaxing filters or adjusting requirements")

def render_search_results(matches, job):
    """Render search results with professional cards - FIXED: unique keys"""
    
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
                # ⭐ FIX: Add unique key based on candidate ID and position
                st.plotly_chart(fig, use_container_width=True, key=f"score_breakdown_{candidate['id']}_{i}")
            
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


def render_dormant_talent_section(job):
    """Render dormant talent suggestions - ULTRA SIMPLE version with inline debug"""
    
    st.markdown("---")
    st.markdown("## 💡 Dormant Talent Discovery")
    
    # Initialize dormant detector
    if 'dormant_detector' not in st.session_state:
        from src.search.dormant_detector import DormantTalentDetector
        with st.spinner("Initializing dormant talent detector..."):
            st.session_state.dormant_detector = DormantTalentDetector(
                st.session_state.matching_engine
            )
    
    # INLINE DEBUG - Always visible
    detector = st.session_state.dormant_detector
    total_dormant = len(detector.dormant_candidates)
    
    if total_dormant == 0:
        st.error("❌ NO DORMANT CANDIDATES IN DATABASE!")
        st.markdown("**Fix:** Regenerate data with dormant candidates:")
        st.code("python scripts/synthetic_generator.py\npython pipeline.py", language="bash")
        return
    
    # Show stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Dormant", total_dormant)
    with col2:
        st.metric("Current Job", job['title'][:20])
    with col3:
        # Check eligibility
        from pathlib import Path
        import json
        app_path = Path("data/processed/applications.json")
        try:
            with open(app_path, 'r') as f:
                apps = json.load(f)
            applicants = {a['candidate_id'] for a in apps if a['job_id'] == job['id']}
            eligible = sum(1 for c in detector.dormant_candidates if c['id'] not in applicants)
            st.metric("Eligible for This Job", eligible)
        except:
            st.metric("Eligible", "Unknown")
    
    st.markdown("---")
    
    # Simple controls - NO FORM
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        min_score = st.slider(
            "Min Score", 
            0.5, 0.95, 0.60, 0.05,
            key=f"dorm_score_{job['id']}"
        )
    
    with col2:
        max_results = st.number_input(
            "Max Results", 
            5, 30, 10,
            key=f"dorm_max_{job['id']}"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button(
            "🔍 Search", 
            type="primary",
            key=f"dorm_btn_{job['id']}"
        )
    
    # IMMEDIATE execution on click
    if search_clicked:
        st.markdown("---")
        
        # Progress tracking
        progress = st.progress(0)
        status = st.empty()
        
        try:
            status.info("🔍 Step 1/3: Loading eligible candidates...")
            progress.progress(33)
            
            # Get eligible dormant candidates
            app_path = Path("data/processed/applications.json")
            with open(app_path, 'r') as f:
                apps = json.load(f)
            
            applied_to_this = {a['candidate_id'] for a in apps if a['job_id'] == job['id']}
            eligible = [c for c in detector.dormant_candidates if c['id'] not in applied_to_this]
            
            st.write(f"Found {len(eligible)} eligible dormant candidates")
            
            if len(eligible) == 0:
                status.warning("⚠️ All dormant candidates already applied to this job!")
                st.info("Try selecting a different job position.")
                progress.progress(100)
                return
            
            status.info("🔍 Step 2/3: Computing match scores...")
            progress.progress(66)
            
            # Direct search
            matches = detector.detect_dormant_matches_direct(job, min_score=min_score)
            matches = matches[:max_results]
            
            status.success(f"✅ Step 3/3: Found {len(matches)} matches!")
            progress.progress(100)
            
            # Store results
            result_key = f"dormant_res_{job['id']}"
            st.session_state[result_key] = matches
            
        except Exception as e:
            status.error(f"❌ Error: {str(e)}")
            st.code(f"Details: {e}")
            import traceback
            with st.expander("Full Error"):
                st.code(traceback.format_exc())
            progress.progress(100)
            return
    
    # Display stored results
    result_key = f"dormant_res_{job['id']}"
    if result_key in st.session_state:
        matches = st.session_state[result_key]
        
        if not matches:
            st.warning(f"No matches found above {min_score:.0%} threshold")
            st.info("Try lowering the minimum score slider above.")
            return
        
        st.markdown("---")
        st.markdown(f"### 🎯 Top {len(matches)} Dormant Matches")
        
        # Metrics row
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_months = sum(m['evolution']['months_dormant'] for m in matches) / len(matches)
            render_metric_card("Avg Months Dormant", f"{avg_months:.0f}")
        with col2:
            avg_score = sum(m['scores']['total_with_evolution'] for m in matches) / len(matches)
            render_metric_card("Avg Match Score", f"{avg_score:.0%}")
        with col3:
            render_metric_card("Dormant Matches", str(len(matches)))
        
        st.markdown("---")
        
        # Display each dormant candidate
        for i, match in enumerate(matches, 1):
            candidate = match['candidate']
            scores = match['scores']
            evolution = match['evolution']
            
            # Dormant alert badge
            st.markdown(f"""
                <div style="background: #FFF3CD; padding: 0.75rem; border-radius: 0.5rem; 
                            border-left: 4px solid #FFC107; margin-bottom: 1rem;">
                    <strong>⚡ DORMANT ALERT #{i}</strong> - Applied {evolution['months_dormant']} months ago
                </div>
            """, unsafe_allow_html=True)
            
            render_candidate_card(candidate, scores['total_with_evolution'], i)
            
            with st.expander("View Dormant Analysis"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**💡 Evolution Insight:**")
                    st.info(evolution['narrative'])
                    
                    st.markdown("**Key Skills:**")
                    st.markdown(", ".join(candidate['skills'][:10]))
                
                with col2:
                    st.markdown("####Scores")
                    st.metric("Base Match", f"{scores['total']:.0%}")
                    st.metric("Evolution Bonus", f"+{scores['evolution']:.0%}")
                    st.metric("Total Score", f"{scores['total_with_evolution']:.0%}")
                    st.markdown(f"**Growth:** {evolution['growth_potential'].split(' - ')[0]}")
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**📧 Email:** {candidate['email']}")
                with col2:
                    st.markdown(f"**📱 Phone:** {candidate['phone']}")
            
            st.markdown("---")