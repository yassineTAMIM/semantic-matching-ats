"""
Forvis Mazars Talent Intelligence System
Professional HR Matching Platform with AI-Powered Insights

Version 2.1 - Enhanced UX Edition
"""

import streamlit as st
import sys
from pathlib import Path
import base64

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from components.theme import apply_theme, BRAND_COLORS
from pages.dashboard import render_dashboard
from pages.candidate_search import render_candidate_search
from pages.comparison import render_candidate_comparison
from pages.dormant_talent import render_dormant_talent
from pages.job_management import render_job_management

# Page configuration
st.set_page_config(
    page_title="Forvis Mazars - Talent Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default Streamlit pages navigation
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        [data-testid="stSidebarNavItems"] {
            display: none;
        }
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0;
        }
        
        /* Footer styling */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(90deg, #171C8F 0%, #0066CC 100%);
            color: white;
            padding: 0.75rem 2rem;
            text-align: center;
            font-size: 0.85rem;
            z-index: 999;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }
        .footer a {
            color: white;
            text-decoration: none;
            margin: 0 1rem;
            opacity: 0.9;
        }
        .footer a:hover {
            opacity: 1;
            text-decoration: underline;
        }
        
        /* Add padding to main content to avoid footer overlap */
        .main .block-container {
            padding-bottom: 4rem;
        }
    </style>
""", unsafe_allow_html=True)

# Apply custom theme
apply_theme()

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Candidate Search"  # Default to Candidate Search

# Initialize matching engines (needed for dormant talent page)
if 'matching_engine' not in st.session_state:
    from src.search.matching_engine import MatchingEngine
    from src.search.dormant_detector import DormantTalentDetector
    
    st.session_state.matching_engine = MatchingEngine()
    st.session_state.dormant_detector = DormantTalentDetector(st.session_state.matching_engine)


def get_logo_base64(image_path):
    """Convert logo image to base64 for embedding"""
    try:
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{data}"
    except:
        return None


def render_navbar():
    """Render horizontal navigation bar"""
    st.markdown(f"""
        <div style="background: linear-gradient(90deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['secondary']} 100%);
                    padding: 0.75rem 2rem; margin: -1rem -1rem 2rem -1rem; 
                    border-radius: 0 0 1rem 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: white;">
                        Forvis Mazars
                    </div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem; border-left: 2px solid rgba(255,255,255,0.3); padding-left: 1rem;">
                        Talent Intelligence System
                    </div>
                </div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem;">
                    {st.session_state.current_page}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render professional minimalist sidebar"""
    
    with st.sidebar:
        # Logo section - try to load from file, fallback to text
        logo_path = "forvis_mazars_logo.png"  # User should place their logo here
        logo_base64 = get_logo_base64(logo_path)
        
        if logo_base64:
            st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem 0; border-bottom: 2px solid #E0E0E0; margin-bottom: 2rem;">
                    <img src="{logo_base64}" style="max-width: 180px; width: 100%;">
                </div>
            """, unsafe_allow_html=True)
        else:
            # Fallback to text logo
            st.markdown("""
                <div style="text-align: center; padding: 1.5rem 0; border-bottom: 2px solid #E0E0E0; margin-bottom: 2rem;">
                    <div style="font-size: 1.6rem; font-weight: 700;">
                        <span style="color: #171C8F;">forvis</span>
                        <span style="color: #0066CC;"> mazars</span>
                    </div>
                    <div style="color: #666; font-size: 0.8rem; margin-top: 0.5rem;">
                        Talent Intelligence
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Clean navigation - no icons, professional
        pages = [
            "Candidate Search",
            "Candidate Comparison", 
            "Dormant Talent",
            "Job Management",
            "Dashboard",
            "About"
        ]
        
        for page_name in pages:
            is_active = st.session_state.current_page == page_name
            
            # Minimal button styling
            button_html = f"""
                <button style="
                    width: 100%;
                    padding: 0.75rem 1rem;
                    margin-bottom: 0.25rem;
                    background: {'linear-gradient(135deg, #171C8F 0%, #0066CC 100%)' if is_active else 'transparent'};
                    color: {'white' if is_active else '#1A1A1A'};
                    border: {'none' if is_active else '1px solid #E0E0E0'};
                    border-radius: 0.5rem;
                    text-align: left;
                    font-size: 0.95rem;
                    font-weight: {'600' if is_active else '500'};
                    cursor: pointer;
                    transition: all 0.2s;
                " onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                    {page_name}
                </button>
            """
            
            if st.button(
                page_name,
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = page_name
                st.rerun()
        
        # Spacer
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        
        # System info card
        st.markdown("""
            <div style="
                padding: 1rem;
                background: linear-gradient(135deg, #F8F9FA 0%, #E8E9EB 100%);
                border-radius: 0.75rem;
                border: 1px solid #E0E0E0;
                margin-top: auto;
            ">
                <div style="font-size: 0.75rem; color: #666; line-height: 1.8;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <strong>System Status</strong>
                        <span style="color: #28A745;">● Active</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>Version</span>
                        <span>2.1</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Model</span>
                        <span>SBERT</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_footer():
    """Render professional footer"""
    st.markdown("""
        <div class="footer">
            <div>
                © 2025 Forvis Mazars | Talent Intelligence System v2.1
                <span style="margin: 0 1rem;">|</span>
                Built with ❤️
                <span style="margin: 0 1rem;">|</span>
                <a href="?page=About">About</a>
                <a href="https://www.forvismazars.com" target="_blank">Forvis Mazars</a>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_about():
    """Render About page with useful information"""
    from components.ui_components import render_header
    
    render_header(
        "About Talent Intelligence System",
        "AI-powered semantic matching for smarter recruitment"
    )
    
    # Introduction
    st.markdown("""
        ### 🎯 What is This System?
        
        The Forvis Mazars Talent Intelligence System uses cutting-edge **Natural Language Processing (NLP)** 
        and **Semantic Matching** to revolutionize how we find and match candidates to job positions.
        
        Unlike traditional keyword-based systems, our AI understands the **meaning** behind job descriptions 
        and candidate profiles, finding the best matches even when different terminology is used.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Candidates", "1,000+", help="Candidates in the database")
    with col2:
        st.metric("Matching Accuracy", "85%+", help="Average precision score")
    with col3:
        st.metric("Time Saved", "80%", help="Reduction in screening time")
    
    st.markdown("---")
    
    # Key Features
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            ### ✨ Key Features
            
            **🔍 Semantic Matching**  
            Understands meaning beyond keywords. Finds "Data Scientist" when you search for "ML Engineer".
            
            **💡 Dormant Talent Rediscovery**  
            Automatically identifies past candidates who now match new positions.
            
            **⚖️ Side-by-Side Comparison**  
            Compare candidates with detailed analytics and visualizations.
            
            **📊 Explainable AI**  
            Every match score is broken down and justified - no black boxes!
            
            **⚡ Lightning Fast**  
            Results in under 2 seconds, even with 10,000+ candidates.
        """)
    
    with col2:
        st.markdown("""
            ### 🛠️ Technology Stack
            
            **Sentence-BERT (SBERT)**  
            State-of-the-art transformer model for semantic understanding.
            
            **FAISS**  
            Facebook AI's similarity search - optimized for large-scale retrieval.
            
            **Multi-Criteria Scoring**  
            - Semantic similarity (70%)
            - Skills match (15%)
            - Experience level (10%)
            - Location preference (5%)
            
            **Python & Streamlit**  
            Modern, responsive web interface built with Python.
        """)
    
    st.markdown("---")
    
    # How It Works
    st.markdown("""
        ### 🔬 How It Works
        
        Our system uses a sophisticated pipeline to match candidates with jobs:
    """)
    
    st.markdown("""
        ```
        1. Job Description → Semantic Embedding (384-dimensional vector)
                                        ↓
        2. Search Similar Candidates (FAISS vector similarity search)
                                        ↓
        3. Multi-Criteria Scoring (semantic + skills + experience + location)
                                        ↓
        4. Ranked Results + Explanations (top 10 candidates with justifications)
        ```
    """)
    
    # Quick Start Guide
    st.markdown("---")
    st.markdown("""
        ### 🚀 Quick Start Guide
        
        **For Recruiters:**
        
        1. **Search Candidates**  
           Go to "Candidate Search" → Select a job position → Click "Find Matching Candidates"
        
        2. **Review Results**  
           Browse top matches with match scores and detailed breakdowns
        
        3. **Compare Finalists**  
           Select your top 2 candidates → Go to "Candidate Comparison" → Click "Generate Comparison"
        
        4. **Discover Hidden Gems**  
           Check "Dormant Talent" to find past candidates who now match new positions
        
        **For Hiring Managers:**
        
        1. **Create Job Positions**  
           Go to "Job Management" → Fill in position details → Save
        
        2. **Review Candidate Shortlists**  
           Work with recruiters to review pre-screened top matches
    """)
    
    st.markdown("---")
    
    # Team & Credits
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            ### 👥 Project Team
            
            **École Centrale Casablanca - Option S2D**
            
            - ABSRI Imad
            - EL BAHA Ali
            - EL MAIMOUNI Kenza
            - RAMDANI Nabil
            - TAMIM Yassine
            
            **Academic Supervision:** École Centrale Casablanca  
            **Industry Partner:** Forvis Mazars
        """)
    
    with col2:
        st.markdown("""
            ### 📧 Support
            
            **Questions?**  
            Contact your HR team or project leads.
            
            **Technical Issues?**  
            Check system status in the sidebar.
            
            **Feedback?**  
            We welcome your input to improve the system!
        """)
    
    st.markdown("---")
    
    # Version Info
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.85rem; padding: 2rem 0;">
            <strong>Version 2.1</strong> | Released February 2025 | Built with Streamlit & Python
        </div>
    """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    
    # Render navbar at top
    render_navbar()
    
    # Render sidebar
    render_sidebar()
    
    # Render current page
    current_page = st.session_state.current_page
    
    if current_page == "Dashboard":
        render_dashboard()
    
    elif current_page == "Candidate Search":
        render_candidate_search()
    
    elif current_page == "Candidate Comparison":
        render_candidate_comparison()
    
    elif current_page == "Dormant Talent":
        render_dormant_talent()
    
    elif current_page == "Job Management":
        render_job_management()
    
    elif current_page == "About":
        render_about()
    
    # Render footer at bottom
    render_footer()

if __name__ == "__main__":
    main()