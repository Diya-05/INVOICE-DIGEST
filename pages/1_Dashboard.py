"""
Invoice Digest — Screen A: Dashboard
Executive Sentiment Monitoring, Stream Analytics & Ingestion Desk.
Redesigned with a Minimal, Premium Editorial & Newspaper-Inspired Theme.
"""

from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.database import (
    DEFAULT_DB_PATH,
    get_dashboard_kpis,
    get_emails_with_latest_predictions,
    init_database,
)
from src.email_import import import_emails_from_csv
from src.finbert_model import run_finbert_on_emails
from src.ui_theme import (
    apply_editorial_theme,
    apply_plotly_editorial_theme,
    render_editorial_masthead,
    render_editorial_sidebar,
)

st.set_page_config(
    page_title="Executive Dashboard | Invoice Digest",
    page_icon="📰",
    layout="wide"
)

# Apply global editorial theme and styling
apply_editorial_theme()
render_editorial_sidebar()

# Ensure DB is ready
init_database()

# Masthead
render_editorial_masthead(
    title="EXECUTIVE DASHBOARD",
    subtitle="Live Stream Ingestion, Corporate Sentiment Polarity & Operational Health",
    kicker="DISPATCH & MONITORING DESK"
)

# Top Action Bar: Ingestion Terminal
with st.expander("📥 Ingestion Terminal: Import Communications (CSV or Live IMAP Sync)", expanded=False):
    tab_csv, tab_live = st.tabs(["📄 Upload CSV Batch", "📬 Live Inbox Synchronizer (IMAP/Gmail)"])
    
    with tab_csv:
        col_up1, col_up2 = st.columns([3, 1])
        with col_up1:
            uploaded_file = st.file_uploader(
                "Upload commercial email CSV (Schema: subject, sender, received_at, body_text)",
                type=["csv"]
            )
        with col_up2:
            st.write("")
            st.write("")
            if uploaded_file is not None:
                if st.button("Ingest CSV File", type="primary", use_container_width=True):
                    with st.spinner("Validating records and indexing hashes..."):
                        res = import_emails_from_csv(uploaded_file)
                        if res.get("success"):
                            st.success(f"Successfully imported {res['imported']} records ({res['duplicates']} duplicates reconciled).")
                            st.rerun()
                        else:
                            st.error(f"Ingestion failed: {res.get('error')}")

    with tab_live:
        st.markdown("""
        <div style="font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #1A1A1A; margin-bottom: 0.75rem;">
            Establish an authenticated IMAP bridge to your financial inbox for automated invoice retrieval:
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("ℹ️ Gmail App Password Guide (30 Seconds)", expanded=False):
            st.markdown("""
            1. Access your **Google Account** security center (`myaccount.google.com`).
            2. Verify that **2-Step Verification** is active.
            3. Search for **App Passwords** (`myaccount.google.com/apppasswords`).
            4. Designate a label (e.g., `InvoiceDigest`) and click **Generate**.
            5. Provide the **16-character token** in the credential box below.
            """)

        col_acc1, col_acc2 = st.columns(2)
        with col_acc1:
            user_email = st.text_input("Corporate / Personal Email", placeholder="user@company.com", key="sync_email")
            search_kw = st.text_input("Subject Filter Keyword", value="invoice", help="Filter messages containing keyword", key="sync_kw")
        with col_acc2:
            user_app_pass = st.text_input("16-Character App Token", type="password", help="Generated application credentials", key="sync_pass")
            fetch_limit = st.slider("Retrieval Batch Cap", min_value=5, max_value=50, value=20, key="sync_limit")

        if st.button("🔄 Initiate Secure Inbox Synchronization", type="primary", use_container_width=True):
            if not user_email or not user_app_pass:
                st.error("Authentication requires both an email address and valid application credentials.")
            else:
                with st.spinner(f"Querying mailbox for '{search_kw}' communications..."):
                    from src.email_service import fetch_invoice_emails_from_inbox
                    res = fetch_invoice_emails_from_inbox(
                        email_address=user_email,
                        app_password=user_app_pass,
                        search_keyword=search_kw,
                        max_emails=fetch_limit
                    )
                    if res.get("success"):
                        st.success(f"Synchronization Complete: {res['message']}")
                        st.rerun()
                    else:
                        st.error(f"Connection Failed: {res.get('error')}")

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# KPI Cards
kpis = get_dashboard_kpis()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Communications", kpis["total_emails"])
c2.metric("Positive Polarity", kpis["positive_count"], help="Settlements, confirmations, payment credits")
c3.metric("Neutral Operations", kpis["neutral_count"], help="Standard billings, purchase orders, statements")
c4.metric("Negative Risk / Alerts", kpis["negative_count"], delta="Audit Priority", delta_color="inverse")
c5.metric("Pending Inference", kpis["unclassified_count"], help="Communications queued for model inference")

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# Visual Analytics Section
col_chart1, col_chart2 = st.columns([1, 1])

with col_chart1:
    st.markdown("""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.25rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.25rem;">
        Sentiment Distribution
    </div>
    <div style="font-size: 0.82rem; color: #66635E; margin-bottom: 0.75rem;">
        Polarity breakdown of classified financial communications
    </div>
    """, unsafe_allow_html=True)

    labels = ["Positive", "Neutral", "Negative"]
    values = [kpis["positive_count"], kpis["neutral_count"], kpis["negative_count"]]
    # Editorial palette: Teal (#0F766E), Muted Gray/Sand (#66635E), Royal Blue / Muted Red (#1E40AF)
    editorial_colors = ["#0F766E", "#66635E", "#1E40AF"]

    if sum(values) > 0:
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.52,
            marker=dict(
                colors=editorial_colors,
                line=dict(color="#FDFBF7", width=2)
            ),
            textinfo='label+percent',
            hoverinfo='label+value+percent'
        )])
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            showlegend=True
        )
        apply_plotly_editorial_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No classified emails available. Execute model inference using the action desk.")

with col_chart2:
    st.markdown("""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.25rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.25rem;">
        Inference & Operations Desk
    </div>
    <div style="font-size: 0.82rem; color: #66635E; margin-bottom: 0.75rem;">
        Execute domain transformer pipeline on queued communications
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="editorial-card" style="margin-bottom: 0.75rem;">
        <span style="font-size: 0.88rem; color: #1A1A1A;">Pending FinBERT Classification:</span>
        <span style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.25rem; font-weight: 700; color: #1E40AF; margin-left: 0.5rem;">
            {kpis['unclassified_count']}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    if kpis["unclassified_count"] > 0:
        if st.button(f"⚡ Execute FinBERT Inference on {kpis['unclassified_count']} Queued Records", type="primary", use_container_width=True):
            emails = get_emails_with_latest_predictions(limit=1000)
            unclassified = [e for e in emails if e["pred_sentiment"] is None]
            
            prog_bar = st.progress(0, text="Initializing FinBERT pipeline...")
            def update_prog(curr, tot):
                prog_bar.progress(curr / tot, text=f"Processing item {curr} of {tot}...")
            
            with st.spinner("Executing FinBERT inference..."):
                run_finbert_on_emails(unclassified, progress_callback=update_prog)
            
            st.success("Batch classification completed and persisted to SQLite.")
            st.rerun()
    else:
        st.markdown("""
        <div style="padding: 0.6rem 0.8rem; background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 4px; font-size: 0.85rem; color: #14532D; margin-bottom: 1rem;">
            ✓ All imported communications have current model classifications.
        </div>
        """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📑 Generate Daily Digest", use_container_width=True):
            st.switch_page("pages/4_Daily_Digest.py")
    with col_btn2:
        if st.button("🔬 Comparative Model Lab", use_container_width=True):
            st.switch_page("pages/3_Model_Lab.py")

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# Recent Emails Table
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.35rem; font-weight: 700; color: #1A1A1A;">
        Chronological Communication Ledger
    </div>
</div>
""", unsafe_allow_html=True)

sentiment_filter = st.selectbox(
    "Filter Stream by Polarity",
    options=["All", "Positive", "Negative", "Neutral"],
    index=0
)

recent_emails = get_emails_with_latest_predictions(
    sentiment_filter=None if sentiment_filter == "All" else sentiment_filter.lower(),
    limit=50
)

if recent_emails:
    display_rows = []
    for r in recent_emails:
        sent = r["pred_sentiment"] or "Pending"
        display_rows.append({
            "ID": f"#{r['email_id']:04d}",
            "Subject": r["subject"],
            "Sender": r["sender"],
            "Received": r["received_at"][:16].replace("T", " ") if r["received_at"] else "",
            "Polarity": sent.capitalize(),
            "Confidence": f"{max(r['positive_score'] or 0, r['negative_score'] or 0, r['neutral_score'] or 0):.1%}" if r["pred_sentiment"] else "N/A",
            "Active Model": r["model_name"] or "Pending"
        })
    df_display = pd.DataFrame(display_rows)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("No communications match the specified filter criteria.")
