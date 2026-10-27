"""
Editorial Design System and Theme Utilities for Invoice Digest
Implements a minimal, premium editorial/newspaper-inspired visual identity:
- Primary Background: #FDFBF7 (warm cream)
- Primary Text: #1A1A1A (ink black)
- Primary Accent: #1E40AF (deep royal blue)
- Secondary Accent: #0F766E (professional teal)
- Borders/Dividers: #E5E1D8
- Muted Text: #66635E
- Elevated Surface: #FFFFFF
"""

from datetime import datetime
import streamlit as st

EDITORIAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,400&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Root Variables */
    :root {
        --bg-primary: #FDFBF7;
        --bg-secondary: #F4EFE6;
        --text-primary: #1A1A1A;
        --text-muted: #66635E;
        --accent-primary: #1E40AF;
        --accent-secondary: #0F766E;
        --border-color: #E5E1D8;
        --surface-white: #FFFFFF;
        --font-serif: 'Playfair Display', 'Libre Baskerville', Georgia, serif;
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Main App Container */
    .stApp {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Override Streamlit Top Header */
    header[data-testid="stHeader"] {
        background-color: var(--bg-primary) !important;
        border-bottom: 1px solid var(--border-color) !important;
    }

    /* Sidebar Styling (Clean Editorial Masthead Style, NOT Dark Mode) */
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: var(--text-muted) !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        font-family: var(--font-serif) !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.01em !important;
    }
    [data-testid="stSidebarNav"] a {
        border-radius: 4px !important;
        transition: all 0.15s ease-in-out !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background-color: var(--border-color) !important;
        color: var(--accent-primary) !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: var(--border-color) !important;
        color: var(--accent-primary) !important;
        font-weight: 600 !important;
        border-left: 3px solid var(--accent-primary) !important;
    }

    /* Typography Hierarchy */
    h1, .stTitle {
        font-family: var(--font-serif) !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        line-height: 1.15 !important;
    }
    h2, h3 {
        font-family: var(--font-serif) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
    }
    h4, h5, h6 {
        font-family: var(--font-sans) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-size: 0.85rem !important;
    }
    p, span, label {
        color: var(--text-primary);
        font-family: var(--font-sans);
        line-height: 1.6;
    }
    .stCaption, caption {
        color: var(--text-muted) !important;
        font-family: var(--font-sans) !important;
        font-size: 0.875rem !important;
    }

    /* Editorial Masthead Component */
    .editorial-masthead {
        border-bottom: 3px double var(--text-primary);
        padding-bottom: 1.25rem;
        margin-bottom: 2rem;
        background: transparent;
    }
    .editorial-meta-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid var(--text-primary);
        border-bottom: 1px solid var(--border-color);
        padding: 0.35rem 0;
        margin-bottom: 1rem;
        font-family: var(--font-sans);
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-muted);
    }
    .editorial-title {
        font-family: var(--font-serif);
        font-size: 2.75rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.1;
        letter-spacing: -0.03em;
        margin: 0.25rem 0;
    }
    .editorial-subtitle {
        font-family: 'Libre Baskerville', Georgia, serif;
        font-style: italic;
        font-size: 1.05rem;
        color: var(--text-muted);
        line-height: 1.5;
        margin-top: 0.5rem;
    }

    /* Editorial Section Rule */
    .editorial-divider {
        border: none;
        border-top: 1px solid var(--border-color);
        margin: 1.75rem 0;
    }
    .editorial-divider-heavy {
        border: none;
        border-top: 2px solid var(--text-primary);
        margin: 2rem 0;
    }

    /* Minimal Editorial Cards */
    .editorial-card {
        background-color: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .editorial-card-elevated {
        background-color: var(--surface-white);
        border: 1px solid var(--border-color);
        border-radius: 4px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(26, 26, 26, 0.03);
    }

    /* Streamlit Metrics (Editorial Styling) */
    [data-testid="stMetric"] {
        background-color: var(--bg-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        padding: 0.85rem 1rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: var(--font-sans) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: var(--text-muted) !important;
    }
    [data-testid="stMetricValue"] {
        font-family: var(--font-serif) !important;
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
    }
    [data-testid="stMetricDelta"] svg {
        fill: currentColor !important;
    }

    /* Buttons: Primary & Secondary */
    button[kind="primary"], .stButton > button[kind="primary"], [data-testid="baseButton-primary"] {
        background-color: var(--accent-primary) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--accent-primary) !important;
        border-radius: 4px !important;
        font-family: var(--font-sans) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        letter-spacing: 0.01em !important;
        padding: 0.45rem 1rem !important;
        box-shadow: none !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover, [data-testid="baseButton-primary"]:hover {
        background-color: #1E3A8A !important;
        border-color: #1E3A8A !important;
        color: #FFFFFF !important;
    }

    button[kind="secondary"], .stButton > button[kind="secondary"], [data-testid="baseButton-secondary"],
    .stButton > button {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        font-family: var(--font-sans) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.45rem 1rem !important;
        box-shadow: none !important;
        transition: all 0.15s ease-in-out !important;
    }
    button[kind="secondary"]:hover, .stButton > button[kind="secondary"]:hover, [data-testid="baseButton-secondary"]:hover,
    .stButton > button:hover {
        background-color: var(--bg-secondary) !important;
        border-color: var(--text-primary) !important;
        color: var(--text-primary) !important;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        background-color: var(--bg-primary) !important;
        color: var(--accent-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
    }
    .stDownloadButton > button:hover {
        background-color: var(--bg-secondary) !important;
        border-color: var(--accent-primary) !important;
    }

    /* Links */
    a {
        color: var(--accent-primary) !important;
        text-decoration: none !important;
        transition: all 0.15s ease !important;
    }
    a:hover {
        color: #1E3A8A !important;
        text-decoration: underline !important;
    }

    /* Forms, Inputs & Selectboxes */
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
        background-color: var(--surface-white) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
        font-size: 0.9rem !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, [data-baseweb="select"]:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 1px var(--accent-primary) !important;
    }
    [data-baseweb="menu"] {
        background-color: var(--surface-white) !important;
        border: 1px solid var(--border-color) !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid var(--border-color) !important;
        background-color: transparent !important;
        gap: 1.5rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--text-muted) !important;
        font-family: var(--font-sans) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 0.25rem !important;
        border-bottom: 2px solid transparent !important;
        background-color: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-primary) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--accent-primary) !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background-color: var(--bg-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        margin-bottom: 1rem !important;
    }
    [data-testid="stExpander"] details {
        border: none !important;
    }
    [data-testid="stExpander"] summary {
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    /* Dataframe / Table Styling */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        background-color: var(--bg-primary) !important;
    }

    /* Muted Status Badges */
    .badge-editorial {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 3px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: var(--font-sans);
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .badge-positive {
        background-color: #F0FDF4;
        color: #15803D;
        border: 1px solid #BBF7D0;
    }
    .badge-negative {
        background-color: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
    }
    .badge-neutral {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    .badge-accent {
        background-color: #EFF6FF;
        color: var(--accent-primary);
        border: 1px solid #BFDBFE;
    }

    /* Alerts / Feedback Overrides */
    .stAlert {
        border-radius: 4px !important;
        border-width: 1px !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="stAlert"]:has([data-testid="stNotificationContentSuccess"]) {
        background-color: #F0FDF4 !important;
        border-color: #BBF7D0 !important;
        color: #14532D !important;
    }
    div[data-testid="stAlert"]:has([data-testid="stNotificationContentError"]) {
        background-color: #FEF2F2 !important;
        border-color: #FECACA !important;
        color: #7F1D1D !important;
    }
    div[data-testid="stAlert"]:has([data-testid="stNotificationContentInfo"]) {
        background-color: #F4EFE6 !important;
        border-color: var(--border-color) !important;
        color: var(--text-primary) !important;
    }
    div[data-testid="stAlert"]:has([data-testid="stNotificationContentWarning"]) {
        background-color: #FFFBEB !important;
        border-color: #FDE68A !important;
        color: #78350F !important;
    }

    /* Code & Pre */
    code, pre {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 3px !important;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: var(--accent-primary) !important;
    }
</style>
"""


def apply_editorial_theme():
    """Injects the global editorial stylesheet into the Streamlit session."""
    st.markdown(EDITORIAL_CSS, unsafe_allow_html=True)


def render_editorial_masthead(
    title: str = "INVOICE DIGEST",
    subtitle: str = "Financial Sentiment Intelligence & Daily Risk Assessment",
    kicker: str = "FINANCIAL COMMUNICATIONS CHRONICLE"
):
    """
    Renders a high-end newspaper masthead with date line, volume,
    double-rule dividers, serif title, and editorial subtitle.
    """
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    masthead_html = f"""
    <div class="editorial-masthead">
        <div class="editorial-meta-bar">
            <span>{kicker}</span>
            <span>{current_date}</span>
            <span>VOL. IV • NO. 104</span>
        </div>
        <div class="editorial-title">{title}</div>
        <div class="editorial-subtitle">{subtitle}</div>
    </div>
    """
    st.markdown(masthead_html, unsafe_allow_html=True)


def render_editorial_sidebar():
    """Renders the newspaper-style editorial sidebar navigation & masthead."""
    st.sidebar.markdown(f"""
    <div style="border-bottom: 1px solid #E5E1D8; padding-bottom: 0.75rem; margin-bottom: 1rem;">
        <div style="font-family: 'Inter', sans-serif; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; color: #66635E; text-transform: uppercase;">
            EDITORIAL DESK
        </div>
        <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.4rem; font-weight: 700; color: #1A1A1A; margin-top: 2px;">
            Invoice Digest
        </div>
        <div style="font-family: 'Inter', sans-serif; font-size: 0.78rem; color: #66635E; margin-top: 2px;">
            Financial Sentiment Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("""
    **NAVIGATION DESK**
    - **1. Dashboard** — Executive Sentiment Overview
    - **2. Email Analysis** — Deep-Dive & Label Audit
    - **3. Model Lab** — FinBERT vs. BiLSTM Benchmark
    - **4. Daily Digest** — Daily Dispatch & Risk Register
    """)

    st.sidebar.markdown("""
    <div style="border-top: 1px solid #E5E1D8; padding-top: 0.75rem; margin-top: 1.5rem; font-size: 0.75rem; color: #66635E;">
        <strong>SPECIFICATION:</strong><br>
        60% Cream (<code>#FDFBF7</code>)<br>
        30% Ink Black (<code>#1A1A1A</code>)<br>
        10% Royal Blue / Teal
    </div>
    """, unsafe_allow_html=True)


def apply_plotly_editorial_theme(fig):
    """
    Applies the newspaper/editorial color palette and clean layout to any Plotly figure:
    - Cream background (#FDFBF7)
    - Ink black typography (#1A1A1A)
    - Border lines (#E5E1D8)
    - Primary Accent (#1E40AF), Secondary (#0F766E), Muted (#66635E)
    """
    fig.update_layout(
        paper_bgcolor="#FDFBF7",
        plot_bgcolor="#FDFBF7",
        font=dict(
            family="'Inter', -apple-system, sans-serif",
            size=12,
            color="#1A1A1A"
        ),
        title_font=dict(
            family="'Playfair Display', Georgia, serif",
            size=15,
            color="#1A1A1A"
        ),
        margin=dict(l=20, r=20, t=35, b=25),
        legend=dict(
            font=dict(color="#1A1A1A", size=11),
            bgcolor="rgba(253, 251, 247, 0.8)",
            bordercolor="#E5E1D8",
            borderwidth=1
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#E5E1D8",
            gridwidth=1,
            linecolor="#E5E1D8",
            linewidth=1,
            tickfont=dict(color="#66635E", size=10),
            title_font=dict(color="#1A1A1A", size=11)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E5E1D8",
            gridwidth=1,
            linecolor="#E5E1D8",
            linewidth=1,
            tickfont=dict(color="#66635E", size=10),
            title_font=dict(color="#1A1A1A", size=11)
        )
    )
    return fig
