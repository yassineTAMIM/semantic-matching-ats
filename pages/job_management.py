"""
Job Management Page - Create and manage job positions
"""

import streamlit as st
import json
from datetime import datetime, timedelta
from components.ui_components import *
from components.theme import BRAND_COLORS
from config import *

def render_job_management():
    """Render job management interface"""
    
    render_header(
        "Job Position Management",
        "Create new positions and manage existing opportunities"
    )
    
    # Load existing jobs
    with open(JOB_DATA_FILE, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    # Tab interface
    tab1, tab2 = st.tabs(["➕ Create New Position", "📋 Manage Existing"])
    
    with tab1:
        render_create_job_form(jobs)
    
    with tab2:
        render_job_list(jobs)

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
        submitted = st.form_submit_button("Create Position", width='stretch', type="primary")
        
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

def render_job_list(jobs):
    """Render list of existing jobs with management options"""
    
    st.markdown(f"### Active Positions ({len(jobs)} total)")
    
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
    st.markdown("---")
    
    # Display jobs
    for job in filtered_jobs:
        with st.expander(f"**{job['title']}** - {job['service_line']} ({job['id']})"):
            render_job_card(job)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {job['description'][:200]}...")
                st.markdown(f"**Required Skills:** {', '.join(job['required_skills'][:10])}")
            
            with col2:
                st.markdown(f"**Posted:** {job['posted_date']}")
                st.markdown(f"**Positions:** {job.get('positions_available', 1)}")
                st.markdown(f"**Salary:** {job.get('salary_range', 'N/A')}")