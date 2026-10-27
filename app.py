"""
Invoice Digest — Streamlit Entry Point
Financial Email Sentiment Analysis & Daily Reporting
Redesigned with a Minimal, Premium Editorial & Newspaper-Inspired Theme.
"""

import os
import streamlit as st
from src.database import get_dashboard_kpis, init_database
from src.ui_theme import (
    apply_editorial_theme,
    render_editorial_masthead,
    render_editorial_sidebar,
)

st.set_page_config(
    page_title="Invoice Digest — Financial Sentiment Intelligence",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global editorial theme and custom stylesheet
apply_editorial_theme()

# Ensure database tables exist
init_database()

# Sidebar Navigation Summary
render_editorial_sidebar()

# Masthead
render_editorial_masthead(
    title="INVOICE DIGEST",
    subtitle="Financial Email Sentiment Intelligence, Transformer Benchmarks & Risk Reporting",
    kicker="EXECUTIVE INTELLIGENCE EDITION"
)

# Top KPI Overview
kpis = get_dashboard_kpis()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Ingested Communications", value=kpis["total_emails"])
with col2:
    st.metric(label="Positive Confirmations", value=kpis["positive_count"], delta="Settled / Credits")
with col3:
    st.metric(label="Neutral Operations", value=kpis["neutral_count"], delta="Invoices / POs")
with col4:
    st.metric(label="Negative Risk Alerts", value=kpis["negative_count"], delta="-Requires Audit", delta_color="inverse")

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# Main Editorial Column & Action Desk
c_left, c_right = st.columns([3, 2])

with c_left:
    st.markdown("""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.45rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.5rem;">
        Executive Memorandum: The Financial Communication Challenge
    </div>
    <div style="font-family: 'Inter', sans-serif; font-size: 0.95rem; line-height: 1.7; color: #1A1A1A;">
        <strong>Invoice Digest</strong> addresses an acute operational vulnerability in modern accounts payable 
        and treasury operations: the deluge of unvetted incoming commercial correspondence. By evaluating tone, 
        contractual urgency, and implicit risk signals, the platform categorizes every incoming financial dispatch 
        into three distinct polarities:
        <ul style="margin-top: 0.5rem; padding-left: 1.25rem;">
            <li><strong>Negative:</strong> Overdue statements, impending service suspensions, billing disputes, and fraud alerts.</li>
            <li><strong>Neutral:</strong> Standard purchase orders, vendor invoices, W-9 submissions, and routine operational inquiries.</li>
            <li><strong>Positive:</strong> Confirmed remittances, early payment discounts, account reconciliations, and vendor commendations.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="editorial-card" style="margin-top: 1.25rem; border-left: 3px solid #1E40AF;">
        <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.05rem; font-weight: 700; color: #1A1A1A;">
            Analytical Interpretation Note
        </div>
        <div style="font-family: 'Inter', sans-serif; font-size: 0.88rem; color: #66635E; margin-top: 0.35rem; line-height: 1.6;">
            Sentiment polarity serves as an analytical proxy for emotional temperature and counterparty urgency, 
            not pure accounting priority. A measured, neutral invoice may represent significant liability, 
            while an impassioned dispute demands immediate client-success intervention. Automated models 
            augment human financial stewards.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c_right:
    st.markdown("""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.45rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.5rem;">
        Operational Desks
    </div>
    <div style="font-size: 0.88rem; color: #66635E; margin-bottom: 1rem;">
        Select an operational terminal to begin processing financial communications:
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="editorial-card-elevated">', unsafe_allow_html=True)
    
    if st.button("📊 Open Operational Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Dashboard.py")
    
    st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

    if st.button("🔍 Search & Verify Email Labels", use_container_width=True):
        st.switch_page("pages/2_Email_Analysis.py")

    st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

    if st.button("🔬 Explore Model Lab (FinBERT vs BiLSTM)", use_container_width=True):
        st.switch_page("pages/3_Model_Lab.py")

    st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

    if st.button("📑 Generate Today's Daily Digest", use_container_width=True):
        st.switch_page("pages/4_Daily_Digest.py")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="border-top: 1px solid #E5E1D8; margin-top: 2.5rem; padding-top: 1rem; display: flex; justify-content: space-between; font-size: 0.78rem; color: #66635E; font-family: 'Inter', sans-serif;">
    <span>MLIS ACADEMIC RESEARCH PROJECT</span>
    <span>BASELINE: FINBERT TRANSFORMER VS. BIDIRECTIONAL LSTM</span>
    <span>PRINTED IN #FDFBF7 CREAM & INK</span>
</div>
""", unsafe_allow_html=True)
