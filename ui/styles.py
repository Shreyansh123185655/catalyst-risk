import streamlit as st

def apply_custom_css():
    """
    Injects custom CSS to match the premium Bloomberg/Palantir aesthetic
    specified in the requirements.
    """
    st.markdown("""
    <style>
    /* Global Variables and Background */
    :root {
      --bg-main: #0B1020;
      --bg-panel: #111827;
      --bg-panel-alt: #172033;
      --accent-cyan: #38BDF8;
      --accent-blue: #818CF8;
      --status-green: #22C55E;
      --status-warn: #F59E0B;
      --status-danger: #EF4444;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --font-sans: 'Inter', -apple-system, sans-serif;
      --font-mono: 'IBM Plex Mono', monospace;
    }
    
    /* Overall Background Override */
    .stApp {
        background-color: var(--bg-main);
        color: var(--text-main);
        font-family: var(--font-sans);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #060913 !important;
        border-right: 1px solid rgba(148, 163, 184, 0.15);
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-main) !important;
        font-family: var(--font-sans);
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-weight: 700 !important;
    }
    
    /* Cards (Using st.container or standard divs) */
    div.css-1r6slb0, div.st-emotion-cache-1r6slb0 {
        background-color: var(--bg-panel);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 6px;
        padding: 20px;
    }
    
    /* KPI Metric Cards specific formatting */
    [data-testid="stMetric"] {
        background-color: var(--bg-panel);
        border: 1px solid rgba(148, 163, 184, 0.2);
        padding: 16px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
    }
    
    [data-testid="stMetricValue"] {
        font-family: var(--font-mono);
        color: var(--text-main);
        font-size: 28px !important;
        font-weight: 700 !important;
        letter-spacing: -1px;
    }
    
    [data-testid="stMetricLabel"] {
        text-transform: uppercase;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
        color: var(--text-muted);
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 11px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-cyan), #3b82f6) !important;
        color: #fff !important;
        border: none !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 6px 16px;
        border-radius: 4px;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
        transition: opacity 0.2s;
    }
    
    .stButton > button:hover {
        opacity: 0.9;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
    }
    
    /* Dataframes and Tables */
    .stDataFrame {
        font-family: var(--font-mono);
    }
    
    /* Hide top padding */
    .block-container {
        padding-top: 2rem !important;
    }
    
    /* Custom divider */
    hr {
        border-color: rgba(148, 163, 184, 0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_top_header(title: str, subtitle: str, status_dict: dict = None):
    """Renders the standard page header."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f'<div style="font-size: 11px; color: #38BDF8; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">CATASTROPHE RISK INTELLIGENCE</div>', unsafe_allow_html=True)
        st.markdown(f'<h1 style="margin-top: -10px; margin-bottom: 0;">{title}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #94A3B8; font-size: 14px; max-width: 600px;">{subtitle}</p>', unsafe_allow_html=True)
        
    with col2:
        if status_dict:
            status_color = "#22C55E" if status_dict.get("ready") else "#F59E0B"
            st.markdown(f"""
            <div style="background-color: #111827; border: 1px solid rgba(148, 163, 184, 0.15); padding: 12px 16px; border-radius: 6px; text-align: right; height: 100%;">
                <div style="font-size: 10px; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Simulation Status</div>
                <div style="font-size: 12px; font-weight: 700; color: {status_color};"><span style="display:inline-block; width:6px; height:6px; background-color:{status_color}; border-radius:50%; margin-right:6px; box-shadow: 0 0 8px {status_color};"></span>{status_dict.get('status_text', 'MODEL READY')}</div>
                <div style="font-size: 11px; color: #94A3B8; margin-top: 8px; font-family: monospace;">EVENTS: {status_dict.get('events', 0):,}</div>
                <div style="font-size: 11px; color: #94A3B8; font-family: monospace;">RUNTIME: {status_dict.get('runtime', '0.00')}s</div>
            </div>
            """, unsafe_allow_html=True)
