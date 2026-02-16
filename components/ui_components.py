"""
Forvis Mazars UI Components - BULLETPROOF VERSION
Guaranteed to render HTML correctly
"""

import streamlit as st
import plotly.graph_objects as go

# Brand colors
COLORS = {
    "primary": "#171C8F",
    "secondary": "#0066CC",
    "success": "#28A745",
    "info": "#17A2B8",
    "warning": "#FFC107",
    "danger": "#DC3545",
    "text_secondary": "#666666"
}

def render_header(title, subtitle=""):
    """Render page header"""
    html = '<div class="app-header">'
    html += f'<h1>{title}</h1>'
    if subtitle:
        html += f'<p>{subtitle}</p>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_metric_card(label, value, delta=None, icon=""):
    """Render metric card using native Streamlit - no HTML issues"""
    if delta:
        st.metric(label=label, value=value, delta=delta)
    else:
        st.metric(label=label, value=value)

def render_candidate_card(candidate, score=None, rank=None):
    """Render candidate card with clean HTML"""
    
    # Extract data safely
    name = str(candidate.get('name', 'N/A'))
    title_text = str(candidate.get('current_title', 'N/A'))
    service_line = str(candidate.get('service_line', 'N/A'))
    years = int(candidate.get('years_experience', 0))
    location = str(candidate.get('location', 'N/A'))
    
    # Build badges
    badges = ""
    if rank:
        badges += f'<span style="background: {COLORS["primary"]}; color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.85rem; font-weight: 600; margin-right: 0.5rem;">#{rank}</span>'
    if score is not None:
        score_color = get_score_color(score)
        score_pct = int(score * 100)
        badges += f'<span style="background: {score_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.85rem; font-weight: 600;">{score_pct}% Match</span>'
    
    # Complete HTML in one string
    card_html = f"""
    <div class="candidate-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <div style="flex: 1;">
                <h3 style="margin: 0; color: {COLORS["primary"]};">{name}</h3>
                <p style="margin: 0.25rem 0; color: {COLORS["text_secondary"]}; font-weight: 500;">{title_text}</p>
            </div>
            <div>{badges}</div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
            <div>
                <div style="color: {COLORS["text_secondary"]}; font-size: 0.85rem;">Service Line</div>
                <div style="font-weight: 500;">{service_line}</div>
            </div>
            <div>
                <div style="color: {COLORS["text_secondary"]}; font-size: 0.85rem;">Experience</div>
                <div style="font-weight: 500;">{years} years</div>
            </div>
            <div>
                <div style="color: {COLORS["text_secondary"]}; font-size: 0.85rem;">Location</div>
                <div style="font-weight: 500;">{location}</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def render_job_card(job):
    """Render job card with clean HTML"""
    
    title = str(job.get('title', 'N/A'))
    service_line = str(job.get('service_line', 'N/A'))
    experience = str(job.get('experience_level', 'N/A'))
    location = str(job.get('location', 'N/A'))
    
    card_html = f"""
    <div class="job-card">
        <h3 style="margin: 0 0 0.5rem 0; color: {COLORS["secondary"]};">{title}</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div>
                <div style="color: {COLORS["text_secondary"]}; font-size: 0.85rem;">Service Line</div>
                <div style="font-weight: 500;">{service_line}</div>
            </div>
            <div>
                <div style="color: {COLORS["text_secondary"]}; font-size: 0.85rem;">Experience</div>
                <div style="font-weight: 500;">{experience}</div>
            </div>
            <div>
                <div style="color: {COLORS["text_secondary"]}; font-size: 0.85rem;">Location</div>
                <div style="font-weight: 500;">{location}</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def get_score_color(score):
    """Get color based on score"""
    if score >= 0.85:
        return COLORS['success']
    elif score >= 0.75:
        return COLORS['info']
    elif score >= 0.65:
        return COLORS['warning']
    else:
        return COLORS['danger']

def render_score_breakdown(scores):
    """Render score breakdown chart - returns figure"""
    categories = list(scores.keys())
    values = list(scores.values())
    
    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker=dict(color=COLORS['primary']),
        text=[f"{v:.0%}" for v in values],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Score Breakdown",
        xaxis=dict(tickformat='.0%', range=[0, 1]),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig  # Return the figure instead of rendering it

def render_radar_chart(candidate, job, scores):
    """Render radar chart - returns figure"""
    categories = ['Semantic', 'Skills', 'Experience', 'Location']
    values = [
        scores.get('semantic', 0),
        scores.get('skills', 0),
        scores.get('experience', 0),
        scores.get('location', 0)
    ]
    
    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=candidate.get('name', 'Candidate'),
        line=dict(color=COLORS['primary'], width=2)
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1], tickformat='.0%')),
        height=400
    )
    
    return fig  # Return the figure instead of rendering it

def render_skill_comparison_chart(skills1, skills2):
    """Render skills comparison - returns figure for caller to display"""
    common = len(set(skills1) & set(skills2))
    unique1 = len(set(skills1) - set(skills2))
    unique2 = len(set(skills2) - set(skills1))
    
    fig = go.Figure(go.Bar(
        x=[common, unique1, unique2],
        y=['Common', 'Candidate 1 Only', 'Candidate 2 Only'],
        orientation='h',
        marker=dict(color=[COLORS['success'], COLORS['primary'], COLORS['secondary']])
    ))
    
    fig.update_layout(
        title="Skills Overlap",
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig  # Return figure instead of rendering

def render_section_header(title):
    """Render section header"""
    html = f'<div class="section-header">{title}</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_stats_grid(stats):
    """Render stats grid"""
    cols = st.columns(len(stats))
    for col, stat in zip(cols, stats):
        with col:
            render_metric_card(stat['label'], stat['value'], stat.get('delta'))