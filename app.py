"""
Invoice Digest — Application Hub & Executive Overview
Modern B2B SaaS Financial Email Sentiment Intelligence Platform
"""

import streamlit as st
from src.database import get_dashboard_kpis, init_database
from src.ui_theme import (
    apply_saas_theme,
    render_app_header,
    render_saas_sidebar,
    apply_plotly_saas_theme,
    render_disclaimer_callout
)
import plotly.graph_objects as go

st.set_page_config(
    page_title="Invoice Digest — Financial Email Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global SaaS design system
apply_saas_theme()
init_database()
render_saas_sidebar(active_page="overview")

# App Header
render_app_header(
    title="Financial Email Intelligence Hub",
    subtitle="Enterprise natural language intelligence platform for classifying incoming financial dispatches, benchmarking domain transformers against recurrent baselines, and automating risk digests.",
    kicker="EXECUTIVE OVERVIEW"
)

# Real Database KPIs
kpis = get_dashboard_kpis()
total = kpis["total_emails"]
pos = kpis["positive_count"]
neu = kpis["neutral_count"]
neg = kpis["negative_count"]
unclass = kpis["unclassified_count"]

pos_pct = f"{(pos / total * 100):.1f}%" if total > 0 else "0.0%"
neu_pct = f"{(neu / total * 100):.1f}%" if total > 0 else "0.0%"
neg_pct = f"{(neg / total * 100):.1f}%" if total > 0 else "0.0%"

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(label="Total Ingested", value=total, help="All unique emails recorded in SQLite database")
with col2:
    st.metric(label="Positive", value=pos, delta=f"{pos_pct} share", delta_color="normal")
with col3:
    st.metric(label="Neutral", value=neu, delta=f"{neu_pct} share", delta_color="off")
with col4:
    st.metric(label="Negative", value=neg, delta=f"{neg_pct} review", delta_color="inverse")
with col5:
    st.metric(label="Pending Inference", value=unclass, delta="Queued" if unclass > 0 else "All Classified", delta_color="off")

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# Main Section: Analytics & Capabilities Grid
c_left, c_right = st.columns([3, 2])

with c_left:
    st.markdown("""
    <div style="font-size: 1.1rem; font-weight: 600; color: #172B3A; margin-bottom: 0.25rem;">
        Sentiment Polarity Distribution
    </div>
    <div style="font-size: 0.82rem; color: #74808B; margin-bottom: 0.85rem;">
        Aggregated sentiment classifications across all currently indexed commercial correspondence
    </div>
    """, unsafe_allow_html=True)

    if total > 0:
        labels = ["Positive (Settled / Credits)", "Neutral (Operations / POs)", "Negative (Disputes / Overdue)"]
        values = [pos, neu, neg]
        colors = ["#18866B", "#DDA348", "#D96C63"]

        if unclass > 0:
            labels.append("Pending Analysis")
            values.append(unclass)
            colors.append("#CBD0D4")

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.56,
            marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
            textinfo='label+percent',
            hoverinfo='label+value+percent'
        )])
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            showlegend=True
        )
        apply_plotly_saas_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No communications indexed yet. Navigate to Email Analysis or Executive Dashboard to upload a CSV batch.")

    render_disclaimer_callout()

with c_right:
    st.markdown("""
    <div style="font-size: 1.1rem; font-weight: 600; color: #172B3A; margin-bottom: 0.25rem;">
        Platform Capabilities & Desks
    </div>
    <div style="font-size: 0.82rem; color: #74808B; margin-bottom: 0.85rem;">
        Navigate directly to your designated operational workspace:
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="saas-card">', unsafe_allow_html=True)

    if st.button("📊 Open Executive Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Dashboard.py")

    st.markdown('<div style="height: 6px;"></div>', unsafe_allow_html=True)

    if st.button("📥 Open Email Analysis & Ledger", use_container_width=True):
        st.switch_page("pages/2_Email_Analysis.py")

    st.markdown('<div style="height: 6px;"></div>', unsafe_allow_html=True)

    if st.button("🔬 Open Model Evaluation Lab", use_container_width=True):
        st.switch_page("pages/3_Model_Lab.py")

    st.markdown('<div style="height: 6px;"></div>', unsafe_allow_html=True)

    if st.button("📑 Open Daily Intelligence Briefing", use_container_width=True):
        st.switch_page("pages/4_Daily_Digest.py")

    st.markdown("""
    <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid #E4E7E5; font-size: 0.8rem; color: #74808B; line-height: 1.5;">
        <strong style="color: #172B3A;">Enterprise Architecture:</strong>
        <ul style="margin: 0.35rem 0 0 1.1rem; padding: 0;">
            <li>Zero cloud leakage: all embeddings and inferencing run locally.</li>
            <li>SHA-256 deduplication preserves idempotent database integrity.</li>
            <li>Comparative evaluation benchmarks FinBERT against supervised BiLSTM.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# System Summary Strip
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; color: #74808B; padding: 0.5rem 0;">
    <span>MLIS RESEARCH & ENTERPRISE INTELLIGENCE SYSTEM</span>
    <span>DUAL-MODEL BENCHMARK: FINBERT vs. BIDIRECTIONAL LSTM</span>
    <span>PERSISTENCE: SQLITE (WAL)</span>
</div>
""", unsafe_allow_html=True)
