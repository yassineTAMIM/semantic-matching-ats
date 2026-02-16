"""
Forvis Mazars Brand Theme Configuration
Professional styling aligned with brand identity
"""

# Forvis Mazars Brand Colors
BRAND_COLORS = {
    "primary": "#171C8F",      # Deep Koamaru - primary navy
    "secondary": "#0066CC",    # Lighter blue from logo
    "accent": "#3F3F3F",       # Mine Shaft - charcoal
    "white": "#FFFFFF",
    "background": "#F8F9FA",   # Light gray background
    "surface": "#FFFFFF",
    "border": "#E0E0E0",
    "text_primary": "#1A1A1A",
    "text_secondary": "#666666",
    "success": "#28A745",
    "warning": "#FFC107",
    "danger": "#DC3545",
    "info": "#17A2B8"
}

# Forvis Mazars Logo SVG
FORVIS_LOGO_SVG = """
<svg width="200" height="50" viewBox="0 0 200 50" xmlns="http://www.w3.org/2000/svg">
    <text x="10" y="32" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="700" fill="#171C8F">forvis</text>
    <text x="95" y="32" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="700" fill="#0066CC">mazars</text>
</svg>
"""

# Custom CSS for professional, corporate look
CUSTOM_CSS = f"""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Main app container */
    .main {{
        background-color: {BRAND_COLORS['background']};
    }}
    
    /* HIDE DEFAULT STREAMLIT PAGES */
    section[data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    
    /* Remove Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Header */
    .app-header {{
        background: linear-gradient(135deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['secondary']} 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 1rem 1rem;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    .app-header h1 {{
        color: white;
        margin: 0;
        font-size: 1.75rem;
        font-weight: 600;
        letter-spacing: -0.02em;
    }}
    
    .app-header p {{
        color: rgba(255,255,255,0.9);
        margin: 0.25rem 0 0 0;
        font-size: 0.95rem;
    }}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid {BRAND_COLORS['border']};
    }}
    
    section[data-testid="stSidebar"] > div {{
        padding-top: 2rem;
    }}
    
    /* Navigation buttons */
    .nav-button {{
        width: 100%;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border: none;
        border-radius: 0.5rem;
        background-color: transparent;
        color: {BRAND_COLORS['text_primary']};
        text-align: left;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .nav-button:hover {{
        background-color: {BRAND_COLORS['background']};
        transform: translateX(4px);
    }}
    
    .nav-button.active {{
        background-color: {BRAND_COLORS['primary']};
        color: white;
    }}
    
    /* Cards */
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid {BRAND_COLORS['border']};
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        transition: all 0.2s;
    }}
    
    .metric-card:hover {{
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }}
    
    .candidate-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid {BRAND_COLORS['primary']};
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }}
    
    .job-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid {BRAND_COLORS['secondary']};
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }}
    
    /* Buttons */
    .stButton button {{
        background: linear-gradient(135deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['secondary']} 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(23, 28, 143, 0.2);
    }}
    
    .stButton button:hover {{
        box-shadow: 0 4px 8px rgba(23, 28, 143, 0.3);
        transform: translateY(-1px);
    }}
    
    /* Metrics */
    div[data-testid="stMetric"] {{
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid {BRAND_COLORS['border']};
    }}
    
    div[data-testid="stMetric"] label {{
        color: {BRAND_COLORS['text_secondary']};
        font-size: 0.85rem;
        font-weight: 500;
    }}
    
    div[data-testid="stMetric"] div {{
        color: {BRAND_COLORS['primary']};
        font-weight: 600;
    }}
    
    /* Score badges */
    .score-excellent {{
        color: {BRAND_COLORS['success']};
        font-weight: 600;
    }}
    
    .score-good {{
        color: {BRAND_COLORS['info']};
        font-weight: 600;
    }}
    
    .score-moderate {{
        color: {BRAND_COLORS['warning']};
        font-weight: 600;
    }}
    
    /* Tables */
    .dataframe {{
        border: 1px solid {BRAND_COLORS['border']} !important;
        border-radius: 0.5rem;
    }}
    
    .dataframe thead th {{
        background-color: {BRAND_COLORS['primary']} !important;
        color: white !important;
        font-weight: 600 !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background-color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        color: {BRAND_COLORS['text_primary']};
        font-weight: 500;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {BRAND_COLORS['primary']};
        color: white;
    }}
    
    /* Progress bars */
    .stProgress > div > div > div {{
        background-color: {BRAND_COLORS['primary']};
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {BRAND_COLORS['background']};
        border-radius: 0.5rem;
        font-weight: 500;
    }}
    
    /* Select boxes and inputs */
    .stSelectbox label, .stTextInput label {{
        color: {BRAND_COLORS['text_primary']};
        font-weight: 500;
        font-size: 0.9rem;
    }}
    
    /* Logo container */
    .logo-container {{
        text-align: center;
        padding: 1rem 0 2rem 0;
        border-bottom: 1px solid {BRAND_COLORS['border']};
        margin-bottom: 2rem;
    }}
    
    .logo-container img {{
        max-width: 180px;
        height: auto;
    }}
    
    /* Section headers */
    .section-header {{
        color: {BRAND_COLORS['primary']};
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {BRAND_COLORS['primary']};
    }}
    
    /* Status indicators */
    .status-active {{
        color: {BRAND_COLORS['success']};
        font-weight: 500;
    }}
    
    .status-dormant {{
        color: {BRAND_COLORS['warning']};
        font-weight: 500;
    }}
    
    /* Comparison highlights */
    .comparison-winner {{
        background-color: rgba(40, 167, 69, 0.1);
        border-left: 3px solid {BRAND_COLORS['success']};
    }}
    
    /* Chart containers */
    .chart-container {{
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid {BRAND_COLORS['border']};
        margin-bottom: 1.5rem;
    }}
</style>
"""

# Forvis Mazars Logo SVG (inline)
FORVIS_LOGO_SVG = """
<svg viewBox="0 0 200 60" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#171C8F;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0066CC;stop-opacity:1" />
    </linearGradient>
  </defs>
  <text x="10" y="25" font-family="Inter, sans-serif" font-size="20" font-weight="600" fill="url(#logoGradient)">forvis</text>
  <text x="10" y="50" font-family="Inter, sans-serif" font-size="20" font-weight="700" fill="#171C8F">mazars</text>
</svg>
"""

def apply_theme():
    """Apply Forvis Mazars theme to Streamlit app"""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)