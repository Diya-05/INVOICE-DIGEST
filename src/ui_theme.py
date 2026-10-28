"""
UI/UX Design System and Reusable Theme Components for Invoice Digest
Modern B2B SaaS Financial Email Intelligence Visual Identity:
- Primary Ink Navy: #172B3A
- Main App Background: #F6F5F0
- Card/Surface Background: #FFFFFF
- Intelligence Green (Positive / Settled): #18866B
- Muted Amber (Neutral / Operational / Pending): #DDA348
- Soft Coral (Negative / Review Recommended): #D96C63
- Primary Text: #202B35
- Secondary Text: #74808B
- Subtle Borders: #E4E7E5
"""

from datetime import datetime
import streamlit as st
from src.database import get_dashboard_kpis


SAAS_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --color-ink-navy: #172B3A;
        --color-app-bg: #F6F5F0;
        --color-surface: #FFFFFF;
        --color-surface-hover: #FBFBF9;
        --color-intelligence-green: #18866B;
        --color-intelligence-green-bg: #E8F5F1;
        --color-intelligence-green-border: #A3D9C9;
        --color-muted-amber: #DDA348;
        --color-muted-amber-dark: #9A6B1F;
        --color-muted-amber-bg: #FBF4E8;
        --color-muted-amber-border: #F3DCB3;
        --color-soft-coral: #D96C63;
        --color-soft-coral-dark: #9C3831;
        --color-soft-coral-bg: #FDF0EF;
        --color-soft-coral-border: #F5C5C0;
        --color-text-primary: #202B35;
        --color-text-secondary: #74808B;
        --color-border: #E4E7E5;
        --border-radius-sm: 6px;
        --border-radius-md: 10px;
        --border-radius-lg: 14px;
        --shadow-card: 0 1px 3px rgba(23, 43, 58, 0.05), 0 1px 2px rgba(23, 43, 58, 0.03);
        --shadow-elevated: 0 4px 14px rgba(23, 43, 58, 0.06), 0 1px 3px rgba(23, 43, 58, 0.03);
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace;
    }

    /* Main Application Body */
    .stApp {
        background-color: var(--color-app-bg) !important;
        color: var(--color-text-primary) !important;
        font-family: var(--font-sans) !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Top Streamlit Header */
    header[data-testid="stHeader"] {
        background-color: var(--color-app-bg) !important;
        border-bottom: 1px solid var(--color-border) !important;
    }

    /* Sidebar Shell */
    [data-testid="stSidebar"] {
        background-color: #FAF9F5 !important;
        border-right: 1px solid var(--color-border) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--color-text-primary);
        font-family: var(--font-sans) !important;
    }
    [data-testid="stSidebarNav"] a {
        border-radius: var(--border-radius-sm) !important;
        padding: 0.45rem 0.75rem !important;
        margin: 2px 0 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: var(--color-text-primary) !important;
        transition: all 0.15s ease-in-out !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background-color: #EFECE6 !important;
        color: var(--color-ink-navy) !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #FFFFFF !important;
        color: var(--color-ink-navy) !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(23, 43, 58, 0.06) !important;
        border-left: 3px solid var(--color-ink-navy) !important;
    }

    /* Typography Hierarchy */
    h1, .stTitle {
        font-family: var(--font-sans) !important;
        color: var(--color-ink-navy) !important;
        font-weight: 700 !important;
        font-size: 1.65rem !important;
        letter-spacing: -0.02em !important;
        line-height: 1.25 !important;
        margin-bottom: 0.25rem !important;
    }
    h2 {
        font-family: var(--font-sans) !important;
        color: var(--color-ink-navy) !important;
        font-weight: 600 !important;
        font-size: 1.35rem !important;
        letter-spacing: -0.01em !important;
    }
    h3 {
        font-family: var(--font-sans) !important;
        color: var(--color-ink-navy) !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
    }
    h4, h5, h6 {
        font-family: var(--font-sans) !important;
        color: var(--color-text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    p, span, label {
        color: var(--color-text-primary);
        font-family: var(--font-sans);
        line-height: 1.55;
    }
    .stCaption, caption {
        color: var(--color-text-secondary) !important;
        font-size: 0.82rem !important;
    }

    /* SaaS Header Block */
    .saas-header {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-lg);
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: var(--shadow-card);
    }
    .saas-kicker {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--color-intelligence-green);
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .saas-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--color-ink-navy);
        letter-spacing: -0.02em;
        margin: 0;
    }
    .saas-subtitle {
        font-size: 0.92rem;
        color: var(--color-text-secondary);
        margin-top: 0.35rem;
        line-height: 1.5;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: var(--color-surface) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 1rem 1.15rem !important;
        box-shadow: var(--shadow-card) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    [data-testid="stMetric"]:hover {
        box-shadow: var(--shadow-elevated) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.74rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: var(--color-text-secondary) !important;
    }
    [data-testid="stMetricValue"] {
        font-family: var(--font-sans) !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: var(--color-ink-navy) !important;
        letter-spacing: -0.02em !important;
    }

    /* White Surface Container */
    .saas-card {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-md);
        padding: 1.25rem 1.35rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-card);
    }
    .saas-card-elevated {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius-lg);
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: var(--shadow-elevated);
    }

    /* Interactive Buttons */
    .stButton > button,
    button[kind="primary"],
    button[kind="secondary"],
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-secondary"],
    .stDownloadButton > button {
        border-radius: 8px !important;
        font-family: var(--font-sans) !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        padding: 0.45rem 0.75rem !important;
        transition: all 0.15s ease-in-out !important;
        white-space: normal !important;
        word-break: normal !important;
        line-height: 1.35 !important;
        height: auto !important;
        min-height: 42px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }

    /* Prevent truncation and enforce crisp typography on all button labels */
    .stButton > button *,
    .stButton > button [data-testid="stMarkdownContainer"] p,
    .stDownloadButton > button *,
    .stDownloadButton > button [data-testid="stMarkdownContainer"] p,
    [data-testid="baseButton-primary"] *,
    [data-testid="baseButton-primary"] [data-testid="stMarkdownContainer"] p,
    [data-testid="baseButton-secondary"] *,
    [data-testid="baseButton-secondary"] [data-testid="stMarkdownContainer"] p {
        white-space: normal !important;
        word-break: normal !important;
        text-overflow: unset !important;
        overflow: visible !important;
        line-height: 1.35 !important;
        font-family: var(--font-sans) !important;
        margin: 0 !important;
    }

    /* Primary Buttons (Deep Ink Navy background with crisp, guaranteed WHITE text) */
    button[kind="primary"],
    .stButton > button[kind="primary"],
    [data-testid="baseButton-primary"] {
        background-color: var(--color-ink-navy) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--color-ink-navy) !important;
        box-shadow: 0 1px 2px rgba(23, 43, 58, 0.12) !important;
    }
    button[kind="primary"] *,
    button[kind="primary"] p,
    button[kind="primary"] span,
    button[kind="primary"] div,
    .stButton > button[kind="primary"] *,
    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span,
    .stButton > button[kind="primary"] div,
    [data-testid="baseButton-primary"] *,
    [data-testid="baseButton-primary"] p,
    [data-testid="baseButton-primary"] span,
    [data-testid="baseButton-primary"] div {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }
    button[kind="primary"]:hover,
    .stButton > button[kind="primary"]:hover,
    [data-testid="baseButton-primary"]:hover {
        background-color: #27435B !important;
        border-color: #27435B !important;
        color: #FFFFFF !important;
    }
    button[kind="primary"]:hover *,
    button[kind="primary"]:hover p,
    button[kind="primary"]:hover span,
    .stButton > button[kind="primary"]:hover *,
    .stButton > button[kind="primary"]:hover p,
    .stButton > button[kind="primary"]:hover span,
    [data-testid="baseButton-primary"]:hover *,
    [data-testid="baseButton-primary"]:hover p,
    [data-testid="baseButton-primary"]:hover span {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    /* Secondary Buttons (Clean white surface with dark text) */
    button[kind="secondary"],
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]),
    [data-testid="baseButton-secondary"] {
        background-color: var(--color-surface) !important;
        color: var(--color-text-primary) !important;
        border: 1px solid var(--color-border) !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }
    button[kind="secondary"] *,
    button[kind="secondary"] p,
    button[kind="secondary"] span,
    .stButton > button[kind="secondary"] *,
    .stButton > button[kind="secondary"] p,
    .stButton > button[kind="secondary"] span,
    .stButton > button:not([kind="primary"]) *,
    .stButton > button:not([kind="primary"]) p,
    .stButton > button:not([kind="primary"]) span,
    [data-testid="baseButton-secondary"] *,
    [data-testid="baseButton-secondary"] p,
    [data-testid="baseButton-secondary"] span {
        color: var(--color-text-primary) !important;
        fill: var(--color-text-primary) !important;
    }
    button[kind="secondary"]:hover,
    .stButton > button[kind="secondary"]:hover,
    .stButton > button:not([kind="primary"]):hover,
    [data-testid="baseButton-secondary"]:hover {
        background-color: #F8F9FA !important;
        border-color: var(--color-ink-navy) !important;
        color: var(--color-ink-navy) !important;
    }
    button[kind="secondary"]:hover *,
    button[kind="secondary"]:hover p,
    button[kind="secondary"]:hover span,
    .stButton > button[kind="secondary"]:hover *,
    .stButton > button[kind="secondary"]:hover p,
    .stButton > button[kind="secondary"]:hover span,
    .stButton > button:not([kind="primary"]):hover *,
    .stButton > button:not([kind="primary"]):hover p,
    .stButton > button:not([kind="primary"]):hover span,
    [data-testid="baseButton-secondary"]:hover *,
    [data-testid="baseButton-secondary"]:hover p,
    [data-testid="baseButton-secondary"]:hover span {
        color: var(--color-ink-navy) !important;
        fill: var(--color-ink-navy) !important;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        background-color: var(--color-surface) !important;
        color: var(--color-ink-navy) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }
    .stDownloadButton > button *,
    .stDownloadButton > button p,
    .stDownloadButton > button span {
        color: var(--color-ink-navy) !important;
        fill: var(--color-ink-navy) !important;
    }
    .stDownloadButton > button:hover {
        background-color: #F8F9FA !important;
        border-color: var(--color-ink-navy) !important;
        color: var(--color-ink-navy) !important;
    }
    .stDownloadButton > button:hover *,
    .stDownloadButton > button:hover p,
    .stDownloadButton > button:hover span {
        color: var(--color-ink-navy) !important;
        fill: var(--color-ink-navy) !important;
    }

    /* Form Inputs */
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
        background-color: var(--color-surface) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: 8px !important;
        color: var(--color-text-primary) !important;
        font-family: var(--font-sans) !important;
        font-size: 0.9rem !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, [data-baseweb="select"]:focus-within {
        border-color: var(--color-ink-navy) !important;
        box-shadow: 0 0 0 1px var(--color-ink-navy) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid var(--color-border) !important;
        background-color: transparent !important;
        gap: 1.5rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: var(--color-text-secondary) !important;
        font-family: var(--font-sans) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 0.25rem !important;
        border-bottom: 2px solid transparent !important;
        background-color: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--color-ink-navy) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--color-ink-navy) !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background-color: var(--color-surface) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--border-radius-md) !important;
        margin-bottom: 0.85rem !important;
        box-shadow: var(--shadow-card) !important;
    }

    /* Dataframe / Table */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--color-border) !important;
        border-radius: var(--border-radius-md) !important;
        background-color: var(--color-surface) !important;
        box-shadow: var(--shadow-card) !important;
    }

    /* SaaS Badges */
    .saas-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 3px 8px;
        border-radius: var(--border-radius-sm);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-family: var(--font-sans);
    }
    .saas-badge-positive {
        background-color: var(--color-intelligence-green-bg);
        color: var(--color-intelligence-green);
        border: 1px solid var(--color-intelligence-green-border);
    }
    .saas-badge-negative {
        background-color: var(--color-soft-coral-bg);
        color: var(--color-soft-coral-dark);
        border: 1px solid var(--color-soft-coral-border);
    }
    .saas-badge-neutral {
        background-color: var(--color-muted-amber-bg);
        color: var(--color-muted-amber-dark);
        border: 1px solid var(--color-muted-amber-border);
    }
    .saas-badge-unclassified {
        background-color: #F1F3F5;
        color: var(--color-text-secondary);
        border: 1px solid var(--color-border);
    }
    .saas-badge-navy {
        background-color: #EBF0F5;
        color: var(--color-ink-navy);
        border: 1px solid #D1DDE7;
    }

    /* Alerts */
    .stAlert {
        border-radius: var(--border-radius-md) !important;
        border-width: 1px !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="stAlert"]:has([data-testid="stNotificationContentSuccess"]) {
        background-color: var(--color-intelligence-green-bg) !important;
        border-color: var(--color-intelligence-green-border) !important;
        color: var(--color-intelligence-green) !important;
    }
    div[data-testid="stAlert"]:has([data-testid="stNotificationContentError"]) {
        background-color: var(--color-soft-coral-bg) !important;
        border-color: var(--color-soft-coral-border) !important;
        color: var(--color-soft-coral-dark) !important;
    }
    div[data-testid="stAlert"]:has([data-testid="stNotificationContentInfo"]) {
        background-color: #FAF9F5 !important;
        border-color: var(--color-border) !important;
        color: var(--color-text-primary) !important;
    }
    div[data-testid="stAlert"]:has([data-testid="stNotificationContentWarning"]) {
        background-color: var(--color-muted-amber-bg) !important;
        border-color: var(--color-muted-amber-border) !important;
        color: var(--color-muted-amber-dark) !important;
    }

    /* Analytical Disclaimer Banner */
    .saas-callout {
        background-color: #FAF9F5;
        border-left: 3px solid var(--color-ink-navy);
        border-top: 1px solid var(--color-border);
        border-right: 1px solid var(--color-border);
        border-bottom: 1px solid var(--color-border);
        border-radius: var(--border-radius-sm);
        padding: 0.85rem 1rem;
        margin: 1rem 0;
        font-size: 0.85rem;
        color: var(--color-text-secondary);
        line-height: 1.55;
    }
    .saas-callout strong {
        color: var(--color-ink-navy);
    }

    /* Code Blocks */
    code, pre {
        background-color: #FAF9F5 !important;
        color: var(--color-text-primary) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: 6px !important;
        font-family: var(--font-mono) !important;
    }

    /* Section Divider */
    .saas-divider {
        border: none;
        border-top: 1px solid var(--color-border);
        margin: 1.25rem 0;
    }
</style>
"""


def apply_editorial_theme():
    """Injects the global SaaS design system stylesheet into the Streamlit session."""
    st.markdown(SAAS_CSS, unsafe_allow_html=True)


apply_saas_theme = apply_editorial_theme  # Alias for clear SaaS semantics


def render_app_header(
    title: str,
    subtitle: str,
    kicker: str = "FINANCIAL EMAIL INTELLIGENCE",
    action_label: str = None
):
    """
    Renders a clean, modern SaaS header with kicker, title, and clear subtitle.
    """
    header_html = f"""
    <div class="saas-header">
        <div class="saas-kicker">
            <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background-color:#18866B;"></span>
            {kicker}
        </div>
        <div class="saas-title">{title}</div>
        <div class="saas-subtitle">{subtitle}</div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_editorial_masthead(
    title: str = "INVOICE DIGEST",
    subtitle: str = "Financial Email Sentiment Intelligence & Daily Risk Reporting",
    kicker: str = "FINANCIAL EMAIL INTELLIGENCE"
):
    """Backward-compatible header renderer delegating to the SaaS header."""
    render_app_header(title=title, subtitle=subtitle, kicker=kicker)


def render_saas_sidebar(active_page: str = "overview"):
    """
    Renders the polished SaaS sidebar with brand mark, product descriptor,
    primary navigation links, real-time system status card, and version footer.
    """
    # Tasteful geometric SVG Brandmark combining letterform/document & analytics chevron
    brand_svg = """
    <svg width="26" height="26" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="28" height="28" rx="7" fill="#172B3A"/>
        <path d="M7 9H21" stroke="#F6F5F0" stroke-width="2" stroke-linecap="round"/>
        <path d="M7 14H16" stroke="#F6F5F0" stroke-width="2" stroke-linecap="round"/>
        <path d="M7 19H13" stroke="#A3D9C9" stroke-width="2" stroke-linecap="round"/>
        <circle cx="19" cy="18" r="3" fill="#18866B"/>
    </svg>
    """

    st.sidebar.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.65rem; padding-bottom: 0.85rem; margin-bottom: 0.5rem; border-bottom: 1px solid #E4E7E5;">
        <div>{brand_svg}</div>
        <div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #172B3A; letter-spacing: -0.02em; line-height: 1.1;">
                Invoice Digest
            </div>
            <div style="font-size: 0.72rem; font-weight: 500; color: #74808B; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px;">
                Financial Email Intelligence
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Primary Navigation (Clean Streamlit page_links)
    st.sidebar.markdown("""
    <div style="font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #74808B; margin: 0.6rem 0 0.35rem 0.2rem;">
        Workspaces
    </div>
    """, unsafe_allow_html=True)

    try:
        st.sidebar.page_link("app.py", label="Overview Hub", icon="🏢")
        st.sidebar.page_link("pages/1_Dashboard.py", label="Executive Dashboard", icon="📊")
        st.sidebar.page_link("pages/2_Email_Analysis.py", label="Email Analysis & Ledger", icon="📥")
        st.sidebar.page_link("pages/3_Model_Lab.py", label="Model Evaluation Lab", icon="🔬")
        st.sidebar.page_link("pages/4_Daily_Digest.py", label="Daily Intelligence Briefing", icon="📑")
    except Exception:
        # Fallback if running outside multi-page router
        st.sidebar.markdown("""
        - [Overview Hub](/)
        - [Executive Dashboard](/1_Dashboard)
        - [Email Analysis](/2_Email_Analysis)
        - [Model Lab](/3_Model_Lab)
        - [Daily Digest](/4_Daily_Digest)
        """)

    # Real-time System Status Card
    kpis = get_dashboard_kpis()
    total_emails = kpis.get("total_emails", 0)

    st.sidebar.markdown(f"""
    <div style="margin-top: 1.75rem; background-color: #FFFFFF; border: 1px solid #E4E7E5; border-radius: 8px; padding: 0.75rem 0.85rem; box-shadow: 0 1px 3px rgba(23,43,58,0.03);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
            <span style="font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #74808B;">System Engine</span>
            <span style="display: inline-flex; align-items: center; gap: 4px; font-size: 0.72rem; color: #18866B; font-weight: 600;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background-color: #18866B;"></span> Ready
            </span>
        </div>
        <div style="font-size: 0.78rem; color: #202B35; line-height: 1.45;">
            <div>• Database: <strong>SQLite (WAL)</strong></div>
            <div>• Primary: <strong>FinBERT Transformer</strong></div>
            <div>• Baseline: <strong>BiLSTM (Supervised)</strong></div>
            <div>• Ingested: <strong>{total_emails} communications</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Footer
    st.sidebar.markdown("""
    <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid #E4E7E5; font-size: 0.72rem; color: #74808B; text-align: center;">
        Invoice Digest v1.2.0 • MLIS Enterprise Edition
    </div>
    """, unsafe_allow_html=True)


render_editorial_sidebar = render_saas_sidebar  # Backward compatible alias


def apply_plotly_saas_theme(fig):
    """
    Applies the modern SaaS color palette and clean layout to any Plotly figure:
    - Background: Transparent or clean surface
    - Typography: 'Inter', sans-serif
    - Grid lines: #E4E7E5
    - Palette: Intelligence Green (#18866B), Muted Amber (#DDA348), Soft Coral (#D96C63), Navy (#172B3A)
    """
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            size=12,
            color="#202B35"
        ),
        title_font=dict(
            family="'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            size=14,
            color="#172B3A"
        ),
        margin=dict(l=20, r=20, t=35, b=25),
        legend=dict(
            font=dict(color="#202B35", size=11),
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#E4E7E5",
            borderwidth=1
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#E4E7E5",
            gridwidth=1,
            linecolor="#E4E7E5",
            linewidth=1,
            tickfont=dict(color="#74808B", size=10),
            title_font=dict(color="#202B35", size=11)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E4E7E5",
            gridwidth=1,
            linecolor="#E4E7E5",
            linewidth=1,
            tickfont=dict(color="#74808B", size=10),
            title_font=dict(color="#202B35", size=11)
        )
    )
    return fig


apply_plotly_editorial_theme = apply_plotly_saas_theme  # Backward compatible alias


def render_sentiment_badge(sentiment: str, confidence: float = None) -> str:
    """Returns HTML for a standardized, accessible sentiment badge."""
    s = str(sentiment).strip().lower()
    conf_str = f" • {confidence:.1%}" if confidence is not None else ""
    
    if s == "positive":
        return f'<span class="saas-badge saas-badge-positive">✓ Positive{conf_str}</span>'
    elif s == "negative":
        return f'<span class="saas-badge saas-badge-negative">! Negative{conf_str}</span>'
    elif s == "neutral":
        return f'<span class="saas-badge saas-badge-neutral">○ Neutral{conf_str}</span>'
    else:
        return f'<span class="saas-badge saas-badge-unclassified">Pending Analysis</span>'


def render_disclaimer_callout():
    """Renders the required domain distinction between sentiment polarity and financial urgency."""
    st.markdown("""
    <div class="saas-callout">
        <strong>Domain Analysis Note:</strong> Sentiment classification evaluates contractual tone and counterparty 
        affect (e.g., courteous remittances vs. adversarial dispute notices). It serves as an analytical indicator, 
        not an independent determination of accounting priority or commercial liability.
    </div>
    """, unsafe_allow_html=True)
