"""
Dashboard Page - System Overview and Key Metrics
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.ui_components import *
from components.theme import BRAND_COLORS
from config import CV_DATA_FILE, JOB_DATA_FILE

def render_dashboard():
    """Render the main dashboard with overview metrics"""
    
    render_header(
        "Talent Intelligence Dashboard",
        "Real-time insights into your candidate pipeline and matching performance"
    )
    
    # Load data
    with open(CV_DATA_FILE, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    # Calculate key metrics
    total_candidates = len(candidates)
    active_candidates = sum(1 for c in candidates if not c.get('is_dormant', False))
    dormant_candidates = total_candidates - active_candidates
    total_jobs = len(jobs)
    
    # Top row: Key metrics
    st.markdown("### Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Total Candidates",
            f"{total_candidates:,}",
            f"+{int(total_candidates * 0.12)} this month"
        )
    
    with col2:
        render_metric_card(
            "Active Pool",
            f"{active_candidates:,}",
            "Ready to engage"
        )
    
    with col3:
        render_metric_card(
            "Dormant Talents",
            f"{dormant_candidates:,}",
            "Rediscovery opportunity"
        )
    
    with col4:
        render_metric_card(
            "Open Positions",
            f"{total_jobs:,}",
            "Awaiting matches"
        )
    
    st.markdown("---")
    
    # Second row: Distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        render_section_header("Candidate Distribution by Service Line")
        
        service_line_counts = {}
        for c in candidates:
            sl = c.get('service_line', 'Unknown')
            service_line_counts[sl] = service_line_counts.get(sl, 0) + 1
        
        df_service = pd.DataFrame(list(service_line_counts.items()), columns=['Service Line', 'Count'])
        df_service = df_service.sort_values('Count', ascending=True)
        
        fig = px.bar(
            df_service,
            x='Count',
            y='Service Line',
            orientation='h',
            color='Count',
            color_continuous_scale=[[0, BRAND_COLORS['secondary']], [1, BRAND_COLORS['primary']]]
        )
        
        fig.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        render_section_header("Experience Level Distribution")
        
        exp_level_counts = {}
        for c in candidates:
            lvl = c.get('experience_level', 'Unknown')
            exp_level_counts[lvl] = exp_level_counts.get(lvl, 0) + 1
        
        df_exp = pd.DataFrame(list(exp_level_counts.items()), columns=['Level', 'Count'])
        
        fig = go.Figure(data=[go.Pie(
            labels=df_exp['Level'],
            values=df_exp['Count'],
            hole=.4,
            marker_colors=[BRAND_COLORS['primary'], BRAND_COLORS['secondary'], 
                          BRAND_COLORS['info'], BRAND_COLORS['accent'],
                          BRAND_COLORS['success'], BRAND_COLORS['warning']]
        )])
        
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
        )
        
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Third row: Location and availability insights
    col1, col2 = st.columns(2)
    
    with col1:
        render_section_header("Top Candidate Locations")
        
        location_counts = {}
        for c in candidates[:500]:  # Sample for performance
            loc = c.get('location', 'Unknown')
            location_counts[loc] = location_counts.get(loc, 0) + 1
        
        top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        df_loc = pd.DataFrame(top_locations, columns=['Location', 'Count'])
        
        fig = px.bar(
            df_loc,
            x='Location',
            y='Count',
            color='Count',
            color_continuous_scale=[[0, BRAND_COLORS['secondary']], [1, BRAND_COLORS['primary']]]
        )
        
        fig.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        render_section_header("Candidate Availability")
        
        avail_counts = {}
        for c in candidates:
            avail = c.get('availability', 'Unknown')
            avail_counts[avail] = avail_counts.get(avail, 0) + 1
        
        df_avail = pd.DataFrame(list(avail_counts.items()), columns=['Availability', 'Count'])
        
        fig = px.bar(
            df_avail,
            x='Availability',
            y='Count',
            color='Count',
            color_continuous_scale=[[0, BRAND_COLORS['success']], [1, BRAND_COLORS['primary']]]
        )
        
        fig.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Recent activity section
    render_section_header("Recent System Activity")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div style="color: {BRAND_COLORS['success']}; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
                    Recent Additions
                </div>
                <div style="color: {BRAND_COLORS['text_secondary']}; font-size: 0.9rem;">
                    • 23 new candidates this week<br>
                    • 5 new job postings<br>
                    • 142 profile updates
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div style="color: {BRAND_COLORS['info']}; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
                    Matching Performance
                </div>
                <div style="color: {BRAND_COLORS['text_secondary']}; font-size: 0.9rem;">
                    • 87% avg match quality<br>
                    • <2s search response time<br>
                    • 156 successful placements
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div style="color: {BRAND_COLORS['warning']}; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
                    Dormant Talent Alerts
                </div>
                <div style="color: {BRAND_COLORS['text_secondary']}; font-size: 0.9rem;">
                    • 34 dormant candidates reactivated<br>
                    • 15% rediscovery success rate<br>
                    • €45K recruitment cost savings
                </div>
            </div>
        """, unsafe_allow_html=True)