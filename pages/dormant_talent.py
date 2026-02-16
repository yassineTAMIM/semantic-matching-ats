"""
Dormant Talent Discovery Page - Identify and reactivate past candidates
"""

import streamlit as st
import json
import sys
from pathlib import Path
from components.ui_components import *
from components.theme import BRAND_COLORS
from config import *

sys.path.append(str(Path(__file__).parent.parent))
from src.search.dormant_detector import DormantTalentDetector
from src.search.matching_engine import MatchingEngine

def render_dormant_talent():
    """Render dormant talent discovery interface"""
    
    render_header(
        "Dormant Talent Rediscovery",
        "Unlock hidden value by identifying past applicants who've gained relevant experience"
    )
    
    # Initialize engines
    if 'matching_engine' not in st.session_state:
        with st.spinner("Initializing system..."):
            st.session_state.matching_engine = MatchingEngine()
            st.session_state.dormant_detector = DormantTalentDetector(st.session_state.matching_engine)
    
    # Load jobs
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    # Info section
    st.info("""
    💡 **What are Dormant Talents?**  
    Candidates who applied 6+ months ago may have since gained new skills, certifications, and experience. 
    This tool automatically identifies them for relevant new positions, reducing recruitment costs by up to 15%.
    """)
    
    # Selection interface
    st.markdown("### Scan for Dormant Matches")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        job_idx = st.selectbox(
            "Select Position to Scan",
            range(len(jobs)),
            format_func=lambda i: f"{jobs[i]['title']} - {jobs[i]['service_line']} ({jobs[i]['location']})"
        )
        selected_job = jobs[job_idx]
    
    with col2:
        min_score = st.slider(
            "Minimum Match Score",
            min_value=50,
            max_value=95,
            value=75,
            step=5,
            format="%d%%",
            help="Only show candidates above this match threshold"
        ) / 100.0  # Convert to decimal
    
    # Show job details
    with st.expander("📋 Position Details", expanded=False):
        render_job_card(selected_job)
    
    # Scan button
    if st.button("🔍 Scan Dormant Candidate Pool", width="stretch", type="primary"):
        
        with st.spinner("Scanning dormant candidates... This may take a moment."):
            # Detect dormant matches
            dormant_matches = st.session_state.dormant_detector.detect_dormant_matches(
                selected_job,
                min_score=min_score
            )
            
            # Generate summary
            summary = st.session_state.dormant_detector.generate_alert_summary(dormant_matches)
        
        if dormant_matches:
            st.success(f"🎯 {summary['message']}")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                render_metric_card(
                    "Total Alerts",
                    str(summary['total_alerts'])
                )
            
            with col2:
                render_metric_card(
                    "Avg Match Score",
                    f"{summary['avg_match_score']:.0%}"
                )
            
            with col3:
                render_metric_card(
                    "Avg Dormant Period",
                    f"{summary['avg_months_dormant']:.0f} months"
                )
            
            with col4:
                top_cand = summary['top_candidate']
                render_metric_card(
                    "Top Candidate",
                    top_cand['name'][:15] + "..."
                )
            
            st.markdown("---")
            
            # Results tabs
            tab1, tab2 = st.tabs(["🚨 Alerts", "📊 Analytics"])
            
            with tab1:
                render_dormant_alerts(dormant_matches, selected_job)
            
            with tab2:
                render_dormant_analytics(dormant_matches)
        
        else:
            st.warning("No dormant candidates found above the threshold.")
            st.info(f"""
            💡 **Suggestions:**
            - Try lowering the minimum match score
            - Review the job requirements
            - Check back later as the pool grows
            """)

def render_dormant_alerts(matches, job):
    """Render dormant candidate alerts"""
    
    st.markdown("### Dormant Talent Alerts")
    st.markdown(f"*Candidates who applied 6+ months ago and match the {job['title']} position*")
    
    for i, match in enumerate(matches, 1):
        candidate = match['candidate']
        scores = match['scores']
        evolution = match['evolution']
        
        # Alert card with dormant styling
        st.markdown(f"""
            <div class="candidate-card" style="border-left: 4px solid {BRAND_COLORS['warning']};">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0; color: {BRAND_COLORS['primary']};">
                            🚨 #{i} - {candidate['name']}
                        </h3>
                        <p style="margin: 0.25rem 0; color: {BRAND_COLORS['text_secondary']}; font-weight: 500;">
                            {candidate['current_title']}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <div style="background: {BRAND_COLORS['warning']}; color: white; 
                                    padding: 0.25rem 0.75rem; border-radius: 1rem; 
                                    font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem;">
                            DORMANT ALERT
                        </div>
                        <div style="background: {get_score_color(scores['total_with_evolution'])}; 
                                    color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; 
                                    font-size: 0.85rem; font-weight: 600;">
                            {scores['total_with_evolution']:.0%} Match
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Expandable details
        with st.expander("View Detailed Analysis & Contact Info"):
            
            # Evolution narrative
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, {BRAND_COLORS['warning']}22 0%, {BRAND_COLORS['warning']}11 100%); 
                            padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                    <div style="font-weight: 600; color: {BRAND_COLORS['warning']}; margin-bottom: 0.5rem;">
                        💡 Evolution Insight
                    </div>
                    <div style="color: {BRAND_COLORS['text_primary']};">
                        {evolution['narrative']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Base Match", f"{scores['total']:.0%}")
            
            with col2:
                st.metric("Evolution Bonus", f"+{scores['evolution']:.0%}")
            
            with col3:
                st.metric("Months Dormant", evolution['months_dormant'])
            
            with col4:
                growth = evolution['growth_potential'].split(' - ')[0]
                color = {
                    'HIGH': BRAND_COLORS['success'],
                    'MEDIUM': BRAND_COLORS['info'],
                    'MODERATE': BRAND_COLORS['warning'],
                    'LOW': BRAND_COLORS['danger']
                }.get(growth, BRAND_COLORS['text_secondary'])
                
                st.markdown(f"""
                    <div>
                        <div style="color: #666; font-size: 0.85rem; margin-bottom: 0.25rem;">Growth Potential</div>
                        <div style="color: {color}; font-weight: 600; font-size: 1.1rem;">{growth}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Score breakdown
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = render_score_breakdown(scores)
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                st.markdown("#### Timeline")
                st.markdown(f"**Last Applied:** {evolution['last_application']}")
                st.markdown(f"**Original Role:** {evolution['original_title']}")
                st.markdown(f"**New Opportunity:** {evolution['new_opportunity']}")
            
            st.markdown("---")
            
            # Contact information
            st.markdown("#### Contact Information")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**📧 Email:** {candidate['email']}")
            
            with col2:
                st.markdown(f"**📱 Phone:** {candidate['phone']}")
            
            with col3:
                st.markdown(f"**📍 Location:** {candidate['location']}")
            
            # Action button
            if st.button(f"📧 Contact {candidate['name']}", key=f"contact_{candidate['id']}"):
                st.success(f"Notification sent to recruit {candidate['name']} for {job['title']}")
        
        st.markdown("---")

def render_dormant_analytics(matches):
    """Render analytics for dormant talent discovery"""
    
    st.markdown("### Discovery Analytics")
    
    # Distribution by months dormant
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Distribution by Dormant Period")
        
        import plotly.express as px
        import pandas as pd
        
        dormant_periods = [m['evolution']['months_dormant'] for m in matches]
        
        fig = px.histogram(
            x=dormant_periods,
            nbins=10,
            labels={'x': 'Months Dormant', 'y': 'Number of Candidates'},
            color_discrete_sequence=[BRAND_COLORS['warning']]
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.markdown("#### Growth Potential Distribution")
        
        growth_counts = {}
        for m in matches:
            potential = m['evolution']['growth_potential'].split(' - ')[0]
            growth_counts[potential] = growth_counts.get(potential, 0) + 1
        
        df = pd.DataFrame(list(growth_counts.items()), columns=['Potential', 'Count'])
        
        fig = px.bar(
            df,
            x='Potential',
            y='Count',
            color='Potential',
            color_discrete_map={
                'HIGH': BRAND_COLORS['success'],
                'MEDIUM': BRAND_COLORS['info'],
                'MODERATE': BRAND_COLORS['warning'],
                'LOW': BRAND_COLORS['danger']
            }
        )
        
        fig.update_layout(
            showlegend=False,
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, width="stretch")
    
    # ROI estimate
    st.markdown("---")
    st.markdown("#### Estimated ROI from Dormant Talent Reactivation")
    
    num_alerts = len(matches)
    avg_recruitment_cost = 5000  # Average cost per external hire
    reactivation_rate = 0.15  # 15% success rate
    
    estimated_hires = int(num_alerts * reactivation_rate)
    cost_savings = estimated_hires * avg_recruitment_cost
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_metric_card("Dormant Alerts", str(num_alerts))
    
    with col2:
        render_metric_card("Estimated Hires", str(estimated_hires), "15% conversion")
    
    with col3:
        render_metric_card("Cost Savings", f"€{cost_savings:,}", "vs external hiring")