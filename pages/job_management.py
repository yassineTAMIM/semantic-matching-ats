"""
Job Management Page - Enhanced position management with analytics
UPDATED: Better job insights, application tracking, position analytics
"""

import streamlit as st
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from components.ui_components import *
from components.theme import BRAND_COLORS
from config import *

def render_job_management():
    """Render enhanced job management interface"""
    
    render_header(
        "Job Position Management",
        "Create, manage, and analyze job positions with application insights"
    )
    
    # Load existing jobs
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    # Load applications for analytics
    try:
        with open(PROCESSED_DATA_DIR / "applications.json", 'r', encoding='utf-8') as f:
            applications = json.load(f)
    except FileNotFoundError:
        applications = []
    
    # Tab interface
    tab1, tab2, tab3 = st.tabs(["➕ Create New Position", "📋 Manage Existing", "📊 Position Analytics"])
    
    with tab1:
        render_create_job_form(jobs)
    
    with tab2:
        render_job_list(jobs, applications)
    
    with tab3:
        render_position_analytics(jobs, applications)


def render_create_job_form(existing_jobs):
    """Render form to create new job position"""
    
    st.markdown("### New Job Position")
    st.markdown("Fill in the details below to create a new position in the system.")
    
    with st.form("new_job_form", clear_on_submit=True):
        
        # Basic information
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Job Title*", placeholder="e.g., Senior Data Scientist")
            service_line = st.selectbox("Service Line*", FORVIS_SERVICE_LINES)
            experience_level = st.selectbox(
                "Experience Level*",
                ["Intern", "Junior", "Mid-Level", "Senior", "Lead", "Principal", "Partner"]
            )
        
        with col2:
            location = st.selectbox("Location*", FORVIS_LOCATIONS)
            contract_type = st.selectbox("Contract Type*", ["Full-time", "Part-time", "Contract", "Temporary"])
            remote = st.selectbox("Remote Work", [False, True, "Hybrid"])
        
        # Experience requirements
        st.markdown("#### Experience Requirements")
        col1, col2 = st.columns(2)
        
        with col1:
            years_min = st.number_input("Minimum Years Experience", min_value=0, max_value=30, value=2)
        
        with col2:
            years_max = st.number_input("Maximum Years Experience", min_value=0, max_value=30, value=5)
        
        # Job description
        st.markdown("#### Job Description")
        description = st.text_area(
            "Description*",
            placeholder="Provide a detailed description of the role, responsibilities, and what makes it unique...",
            height=150
        )
        
        # Skills and requirements
        st.markdown("#### Skills & Requirements")
        
        # Pre-populate skills based on service line
        default_skills = get_default_skills(service_line)
        
        col1, col2 = st.columns(2)
        
        with col1:
            required_skills_input = st.text_area(
                "Required Skills* (comma-separated)",
                value=", ".join(default_skills[:8]),
                height=100
            )
            
            required_languages_input = st.text_input(
                "Required Languages (comma-separated)",
                value="English, French"
            )
        
        with col2:
            preferred_certs_input = st.text_area(
                "Preferred Certifications (comma-separated)",
                placeholder="e.g., CPA, CFA, PMP",
                height=100
            )
            
            education = st.text_input(
                "Preferred Education",
                placeholder="e.g., Master's in Finance"
            )
        
        # Additional details
        st.markdown("#### Additional Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            travel = st.selectbox(
                "Travel Required",
                ["None", "Occasional (10-25%)", "Frequent (25-50%)", "Extensive (50%+)"]
            )
        
        with col2:
            team_size = st.number_input("Team Size", min_value=1, max_value=100, value=10)
        
        with col3:
            positions = st.number_input("Number of Positions", min_value=1, max_value=10, value=1)
        
        # Salary range
        col1, col2 = st.columns(2)
        
        with col1:
            salary_min = st.number_input("Min Salary (€K)", min_value=20, max_value=300, value=50)
        
        with col2:
            salary_max = st.number_input("Max Salary (€K)", min_value=20, max_value=300, value=70)
        
        # Submit button
        submitted = st.form_submit_button("Create Position", use_container_width=True, type="primary")
        
        if submitted:
            # Validate required fields
            if not title or not description:
                st.error("Please fill in all required fields marked with *")
            elif years_min > years_max:
                st.error("Minimum experience cannot exceed maximum experience")
            elif salary_min > salary_max:
                st.error("Minimum salary cannot exceed maximum salary")
            else:
                # Create new job object
                new_job = create_job_object(
                    existing_jobs,
                    title, service_line, location, experience_level,
                    years_min, years_max, description,
                    required_skills_input, required_languages_input,
                    preferred_certs_input, education,
                    contract_type, remote, travel, team_size, positions,
                    salary_min, salary_max
                )
                
                # Add to jobs list
                existing_jobs.append(new_job)
                
                # Save to file
                with open(JOB_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(existing_jobs, f, indent=2, ensure_ascii=False)
                
                st.success(f"✅ Position '{title}' created successfully! (ID: {new_job['id']})")
                st.info("The new position is now available for candidate matching.")
                
                # Show created job
                with st.expander("View Created Position"):
                    render_job_card(new_job)


def render_job_list(jobs, applications):
    """Render list of existing jobs with management options and application stats"""
    
    st.markdown(f"### Active Positions ({len(jobs)} total)")
    
    # Calculate application stats per job
    app_counts = {}
    for app in applications:
        job_id = app['job_id']
        app_counts[job_id] = app_counts.get(job_id, 0) + 1
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_service = st.selectbox(
            "Filter by Service Line",
            ["All"] + FORVIS_SERVICE_LINES,
            key="job_filter_service"
        )
    
    with col2:
        filter_level = st.selectbox(
            "Filter by Level",
            ["All", "Intern", "Junior", "Mid-Level", "Senior", "Lead", "Principal", "Partner"],
            key="job_filter_level"
        )
    
    with col3:
        search_term = st.text_input("Search by title", key="job_search")
    
    # Apply filters
    filtered_jobs = jobs
    
    if filter_service != "All":
        filtered_jobs = [j for j in filtered_jobs if j['service_line'] == filter_service]
    
    if filter_level != "All":
        filtered_jobs = [j for j in filtered_jobs if j['experience_level'] == filter_level]
    
    if search_term:
        filtered_jobs = [j for j in filtered_jobs if search_term.lower() in j['title'].lower()]
    
    st.markdown(f"Showing {len(filtered_jobs)} positions")
    
    # Sort options
    col1, col2 = st.columns([3, 1])
    with col2:
        sort_by = st.selectbox("Sort by", ["Most Recent", "Most Applications", "Title (A-Z)"], key="job_sort")
    
    # Sort jobs
    if sort_by == "Most Recent":
        filtered_jobs.sort(key=lambda x: x.get('posted_date', '2000-01-01'), reverse=True)
    elif sort_by == "Most Applications":
        filtered_jobs.sort(key=lambda x: app_counts.get(x['id'], 0), reverse=True)
    else:  # Title A-Z
        filtered_jobs.sort(key=lambda x: x['title'])
    
    st.markdown("---")
    
    # Display jobs
    for job in filtered_jobs:
        job_apps = app_counts.get(job['id'], 0)
        
        # Job card with application badge
        col1, col2 = st.columns([4, 1])
        
        with col1:
            days_open = (datetime.now() - datetime.strptime(job['posted_date'], '%Y-%m-%d')).days
            
            st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; 
                            border-left: 4px solid {BRAND_COLORS['secondary']}; margin-bottom: 1rem;">
                    <h4 style="margin: 0 0 0.5rem 0; color: {BRAND_COLORS['primary']};">
                        {job['title']}
                    </h4>
                    <div style="display: flex; gap: 1rem; font-size: 0.9rem; color: {BRAND_COLORS['text_secondary']};">
                        <span>📍 {job['location']}</span>
                        <span>💼 {job['service_line']}</span>
                        <span>📊 {job['experience_level']}</span>
                        <span>📅 {days_open} days open</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Application count badge
            badge_color = BRAND_COLORS['success'] if job_apps > 20 else BRAND_COLORS['warning'] if job_apps > 5 else BRAND_COLORS['text_secondary']
            st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: {badge_color}22; 
                            border-radius: 0.5rem; border: 2px solid {badge_color};">
                    <div style="font-size: 1.5rem; font-weight: 700; color: {badge_color};">
                        {job_apps}
                    </div>
                    <div style="font-size: 0.8rem; color: {BRAND_COLORS['text_secondary']};">
                        Applications
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with st.expander(f"View Details - {job['id']}"):
            render_job_details(job, job_apps)
        
        st.markdown("---")


def render_job_details(job, app_count):
    """Render detailed job information"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Description")
        st.markdown(job['description'])
        
        st.markdown("#### Key Responsibilities")
        for resp in job.get('responsibilities', [])[:5]:
            st.markdown(f"• {resp}")
        
        st.markdown("#### Requirements")
        for req in job.get('requirements', [])[:5]:
            st.markdown(f"• {req}")
    
    with col2:
        st.markdown("#### Position Details")
        st.markdown(f"**Posted:** {job['posted_date']}")
        st.markdown(f"**Deadline:** {job.get('application_deadline', 'Open')}")
        st.markdown(f"**Positions:** {job.get('positions_available', 1)}")
        st.markdown(f"**Applications:** {app_count}")
        
        st.markdown("#### Compensation & Benefits")
        st.markdown(f"**Salary:** {job.get('salary_range', 'Competitive')}")
        st.markdown(f"**Contract:** {job['contract_type']}")
        st.markdown(f"**Remote:** {job.get('remote', 'No')}")
        st.markdown(f"**Travel:** {job.get('travel_required', 'None')}")
    
    st.markdown("---")
    
    st.markdown("#### Required Skills")
    skills_display = ", ".join(job['required_skills'][:20])
    if len(job['required_skills']) > 20:
        skills_display += f" (+{len(job['required_skills']) - 20} more)"
    st.markdown(skills_display)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"🔍 Find Candidates", key=f"find_{job['id']}", use_container_width=True):
            st.session_state.current_page = "Candidate Search"
            st.rerun()
    with col2:
        if st.button(f"📝 Edit Position", key=f"edit_{job['id']}", use_container_width=True):
            st.info("Edit functionality - coming soon")
    with col3:
        if st.button(f"📊 View Analytics", key=f"analytics_{job['id']}", use_container_width=True):
            st.info("Detailed analytics - coming soon")


def render_position_analytics(jobs, applications):
    """Render analytics dashboard for all positions"""
    
    st.markdown("### Position Performance Analytics")
    
    if not jobs:
        st.info("No positions to analyze. Create a job position to see analytics.")
        return
    
    # Calculate metrics
    app_counts = {}
    for app in applications:
        job_id = app['job_id']
        app_counts[job_id] = app_counts.get(job_id, 0) + 1
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("Total Positions", f"{len(jobs)}")
    with col2:
        render_metric_card("Total Applications", f"{len(applications)}")
    with col3:
        avg_apps = len(applications) / len(jobs) if jobs else 0
        render_metric_card("Avg Apps/Position", f"{avg_apps:.1f}")
    with col4:
        positions_with_apps = sum(1 for job_id in app_counts if app_counts[job_id] > 0)
        fill_rate = (positions_with_apps / len(jobs) * 100) if jobs else 0
        render_metric_card("Fill Rate", f"{fill_rate:.0f}%")
    
    st.markdown("---")
    
    # Applications by position
    st.markdown("#### Applications by Position")
    
    job_app_data = []
    for job in jobs:
        job_app_data.append({
            'Position': job['title'][:30] + ('...' if len(job['title']) > 30 else ''),
            'Applications': app_counts.get(job['id'], 0),
            'Service Line': job['service_line'],
            'Days Open': (datetime.now() - datetime.strptime(job['posted_date'], '%Y-%m-%d')).days
        })
    
    if job_app_data:
        import pandas as pd
        df = pd.DataFrame(job_app_data)
        df = df.sort_values('Applications', ascending=True).tail(15)
        
        fig = px.bar(
            df,
            y='Position',
            x='Applications',
            color='Service Line',
            orientation='h',
            text='Applications'
        )
        
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(
            height=500,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True, key="apps_by_position")
    
    st.markdown("---")
    
    # Service line breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Positions by Service Line")
        
        service_counts = {}
        for job in jobs:
            sl = job['service_line']
            service_counts[sl] = service_counts.get(sl, 0) + 1
        
        fig = go.Figure(data=[go.Pie(
            labels=list(service_counts.keys()),
            values=list(service_counts.values()),
            hole=.4,
            marker_colors=[BRAND_COLORS['primary'], BRAND_COLORS['secondary'], 
                          BRAND_COLORS['info'], BRAND_COLORS['accent']]
        )])
        
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True, key="service_pie")
    
    with col2:
        st.markdown("#### Applications by Service Line")
        
        service_apps = {}
        for app in applications:
            # Find job's service line
            job = next((j for j in jobs if j['id'] == app['job_id']), None)
            if job:
                sl = job['service_line']
                service_apps[sl] = service_apps.get(sl, 0) + 1
        
        if service_apps:
            fig = go.Figure(data=[go.Bar(
                x=list(service_apps.keys()),
                y=list(service_apps.values()),
                marker_color=BRAND_COLORS['primary'],
                text=list(service_apps.values()),
                textposition='outside'
            )])
            
            fig.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True, key="service_apps_bar")
        else:
            st.info("No applications yet")
    
    st.markdown("---")
    
    # Top performing positions
    st.markdown("#### Top Performing Positions")
    
    top_jobs = sorted(jobs, key=lambda x: app_counts.get(x['id'], 0), reverse=True)[:5]
    
    for i, job in enumerate(top_jobs, 1):
        apps = app_counts.get(job['id'], 0)
        days = (datetime.now() - datetime.strptime(job['posted_date'], '%Y-%m-%d')).days
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{i}. {job['title']}**")
        with col2:
            st.markdown(f"{apps} applications")
        with col3:
            st.markdown(f"{days} days open")


def create_job_object(existing_jobs, title, service_line, location, experience_level,
                     years_min, years_max, description, skills_input, languages_input,
                     certs_input, education, contract_type, remote, travel, team_size,
                     positions, salary_min, salary_max):
    """Create new job object with all fields"""
    
    # Generate new ID
    max_id = max([int(j['id'].split('_')[1]) for j in existing_jobs], default=0)
    new_id = f"JOB_{max_id + 1:04d}"
    
    # Parse comma-separated inputs
    required_skills = [s.strip() for s in skills_input.split(',') if s.strip()]
    required_languages = [l.strip() for l in languages_input.split(',') if l.strip()]
    preferred_certs = [c.strip() for c in certs_input.split(',') if c.strip()]
    
    # Generate responsibilities and requirements based on service line
    responsibilities = generate_responsibilities(service_line, experience_level)
    requirements = generate_requirements(experience_level, service_line)
    benefits = generate_benefits()
    
    return {
        "id": new_id,
        "title": title,
        "service_line": service_line,
        "location": location,
        "experience_level": experience_level,
        "years_experience_min": years_min,
        "years_experience_max": years_max,
        "description": description,
        "responsibilities": responsibilities,
        "requirements": requirements,
        "required_skills": required_skills,
        "required_languages": required_languages,
        "preferred_certifications": preferred_certs,
        "preferred_education": education,
        "salary_range": f"€{salary_min}K - €{salary_max}K + performance bonus",
        "benefits": benefits,
        "contract_type": contract_type,
        "remote": remote,
        "travel_required": travel,
        "team_size": team_size,
        "reports_to": "Manager",
        "posted_date": datetime.now().strftime("%Y-%m-%d"),
        "application_deadline": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
        "positions_available": positions,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }


def get_default_skills(service_line):
    """Get default skills based on service line"""
    skill_map = {
        "Audit & Assurance": ["Financial Reporting", "IFRS", "GAAP", "Internal Audit", "Risk Assessment", "Excel", "SAP", "Analytical Thinking"],
        "Tax & Legal": ["Corporate Tax", "VAT", "Tax Planning", "Transfer Pricing", "Legal Drafting", "Tax Compliance", "Research Skills"],
        "Financial Advisory": ["Financial Modeling", "Valuation", "M&A", "Due Diligence", "Excel", "PowerPoint", "Analytical Skills"],
        "Consulting": ["Strategy", "Business Transformation", "Project Management", "Change Management", "Stakeholder Management", "Presentation"],
        "Digital & Technology": ["Python", "SQL", "Data Analysis", "Cloud Computing", "Machine Learning", "Power BI", "Problem Solving"],
        "Outsourcing": ["Process Optimization", "Financial Reporting", "SAP", "Excel", "Attention to Detail", "Time Management"],
        "Risk Management": ["Risk Assessment", "Compliance", "Internal Controls", "Analytical Thinking", "Reporting", "Communication"],
        "Sustainability & ESG": ["ESG Reporting", "Sustainability", "Carbon Accounting", "Stakeholder Engagement", "Data Analysis", "Reporting"]
    }
    return skill_map.get(service_line, ["Analytical Thinking", "Communication", "Teamwork", "Problem Solving"])


def generate_responsibilities(service_line, level):
    """Generate typical responsibilities"""
    base = [
        f"Deliver high-quality {service_line.lower()} services to clients",
        "Maintain strong client relationships and communication",
        "Prepare professional deliverables and documentation",
        "Stay current with industry trends and regulations"
    ]
    
    if level in ["Senior", "Lead", "Principal", "Partner"]:
        base.extend([
            "Mentor and develop junior team members",
            "Lead complex engagements and projects",
            "Contribute to business development initiatives"
        ])
    
    return base


def generate_requirements(level, service_line):
    """Generate typical requirements"""
    reqs = [
        "Bachelor's or Master's degree in relevant field",
        "Strong analytical and problem-solving skills",
        "Excellent communication abilities",
        "Proficiency in Microsoft Office Suite"
    ]
    
    if level not in ["Intern", "Junior"]:
        reqs.append("Proven track record in professional services or similar environment")
    
    return reqs


def generate_benefits():
    """Generate standard benefits"""
    return [
        "Competitive salary and performance bonus",
        "Comprehensive health insurance",
        "Retirement savings plan",
        "25+ days annual leave",
        "Professional development budget",
        "Flexible working arrangements",
        "Employee wellness programs"
    ]