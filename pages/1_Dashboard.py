"""
Invoice Digest — Screen A: Executive Dashboard
Operational Stream Analytics, Ingestion Terminal & Batch Pipeline
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
    apply_saas_theme,
    apply_plotly_saas_theme,
    render_app_header,
    render_saas_sidebar,
    render_disclaimer_callout,
)

st.set_page_config(
    page_title="Executive Dashboard | Invoice Digest",
    page_icon="📊",
    layout="wide"
)

# Apply global SaaS design system
apply_saas_theme()
render_saas_sidebar(active_page="dashboard")
init_database()

# Header
render_app_header(
    title="Executive Operational Dashboard",
    subtitle="Real-time financial communication stream, batch ingestion terminal, sentiment distribution, and active inference pipeline.",
    kicker="OPERATIONAL MONITORING DESK"
)

# Ingestion Terminal
with st.expander("📥 Ingestion Terminal: Upload CSV Batch or Connect Live IMAP Inbox", expanded=False):
    tab_csv, tab_live = st.tabs(["📄 Upload CSV Batch", "📬 Live Inbox Synchronizer (IMAP/Gmail)"])
    
    with tab_csv:
        col_up1, col_up2 = st.columns([3, 1])
        with col_up1:
            uploaded_file = st.file_uploader(
                "Upload commercial email CSV (Required schema: subject, sender, received_at, body_text)",
                type=["csv"]
            )
        with col_up2:
            st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
            # Sample CSV template download
            sample_csv_text = "subject,sender,received_at,body_text,sentiment\nINV-1001,billing@cloudservers.io,2026-10-20T08:15:00Z,\"We have successfully processed payment for Invoice #94821\",positive\nINV-1002,collections@saasmetrics.com,2026-10-20T09:30:00Z,\"Final notice: invoice #8812 is 45 days overdue. Payment required.\",negative\nINV-1003,finance@apexconsulting.org,2026-10-20T10:00:00Z,\"Attached monthly invoice #INV-2026-10 for consulting hours logged.\",neutral"
            st.download_button(
                label="📄 Download CSV Template",
                data=sample_csv_text,
                file_name="invoice_digest_sample_template.csv",
                mime="text/csv",
                use_container_width=True
            )

        if uploaded_file is not None:
            if st.button("Process & Ingest CSV Records", type="primary", use_container_width=True):
                with st.spinner("Validating schema and calculating SHA-256 deduplication hashes..."):
                    res = import_emails_from_csv(uploaded_file)
                    if res.get("success"):
                        st.success(f"✓ Ingestion Complete: {res['imported']} records stored ({res['duplicates']} duplicates reconciled).")
                        st.rerun()
                    else:
                        st.error(f"Ingestion Failed: {res.get('error')}")

    with tab_live:
        st.markdown("""
        <div style="font-size: 0.88rem; color: #202B35; margin-bottom: 0.75rem;">
            Establish an authenticated TLS/IMAP bridge to your corporate mailbox for automatic invoice retrieval:
        </div>
        """, unsafe_allow_html=True)

        col_acc1, col_acc2 = st.columns(2)
        with col_acc1:
            user_email = st.text_input("Mailbox Address", placeholder="finance@company.com", key="sync_email")
            search_kw = st.text_input("Subject Keyword Filter", value="invoice", help="Retrieve messages matching this term", key="sync_kw")
        with col_acc2:
            user_app_pass = st.text_input("16-Digit App Password", type="password", help="Generated Google or Exchange App Token", key="sync_pass")
            fetch_limit = st.slider("Max Batch Retrieval Cap", min_value=5, max_value=50, value=20, key="sync_limit")

        if st.button("🔄 Synchronize Mailbox via IMAP", type="primary", use_container_width=True):
            if not user_email or not user_app_pass:
                st.error("Authentication requires both an email address and a valid application token.")
            else:
                with st.spinner(f"Querying secure IMAP mailbox for '{search_kw}'..."):
                    from src.email_service import fetch_invoice_emails_from_inbox
                    res = fetch_invoice_emails_from_inbox(
                        email_address=user_email,
                        app_password=user_app_pass,
                        search_keyword=search_kw,
                        max_emails=fetch_limit
                    )
                    if res.get("success"):
                        st.success(f"Inbox Synchronization Complete: {res['message']}")
                        st.rerun()
                    else:
                        st.error(f"Connection Failed: {res.get('error')}")

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# Top KPIs
kpis = get_dashboard_kpis()
total = kpis["total_emails"]
pos = kpis["positive_count"]
neu = kpis["neutral_count"]
neg = kpis["negative_count"]
unclass = kpis["unclassified_count"]

pos_pct = f"{(pos / total * 100):.1f}%" if total > 0 else "0.0%"
neu_pct = f"{(neu / total * 100):.1f}%" if total > 0 else "0.0%"
neg_pct = f"{(neg / total * 100):.1f}%" if total > 0 else "0.0%"

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Communications", total, help="Total unique records indexed in SQLite")
c2.metric("Positive Sentiment", pos, delta=f"{pos_pct} share", delta_color="normal")
c3.metric("Neutral Operations", neu, delta=f"{neu_pct} share", delta_color="off")
c4.metric("Negative Sentiment", neg, delta=f"{neg_pct} review", delta_color="inverse")
c5.metric("Pending Inference", unclass, delta="Queued" if unclass > 0 else "All Classified", delta_color="off")

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# Analytics & Operations Desk
col_chart1, col_chart2 = st.columns([1, 1])

with col_chart1:
    st.markdown("""
    <div style="font-size: 1.05rem; font-weight: 600; color: #172B3A; margin-bottom: 0.25rem;">
        Sentiment Polarity Composition
    </div>
    <div style="font-size: 0.8rem; color: #74808B; margin-bottom: 0.75rem;">
        Distribution across verified and inferred correspondence
    </div>
    """, unsafe_allow_html=True)

    if total > 0:
        labels = ["Positive", "Neutral", "Negative"]
        values = [pos, neu, neg]
        colors = ["#18866B", "#DDA348", "#D96C63"]

        if unclass > 0:
            labels.append("Pending")
            values.append(unclass)
            colors.append("#CBD0D4")

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.54,
            marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
            textinfo='label+percent',
            hoverinfo='label+value+percent'
        )])
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=260,
            showlegend=True
        )
        apply_plotly_saas_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No communications indexed yet. Upload a CSV using the Ingestion Terminal above.")

with col_chart2:
    st.markdown("""
    <div style="font-size: 1.05rem; font-weight: 600; color: #172B3A; margin-bottom: 0.25rem;">
        Inference & Model Pipeline
    </div>
    <div style="font-size: 0.8rem; color: #74808B; margin-bottom: 0.75rem;">
        Execute domain transformer FinBERT pipeline on pending dispatches
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="saas-card" style="margin-bottom: 0.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: baseline;">
            <span style="font-size: 0.85rem; color: #74808B;">Pending FinBERT Classification:</span>
            <span style="font-size: 1.25rem; font-weight: 700; color: {'#D96C63' if unclass > 0 else '#18866B'};">
                {unclass}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if unclass > 0:
        if st.button(f"⚡ Execute FinBERT Inference on {unclass} Queued Records", type="primary", use_container_width=True):
            emails = get_emails_with_latest_predictions(limit=1000)
            pending_emails = [e for e in emails if e["pred_sentiment"] is None]
            
            prog_bar = st.progress(0, text="Initializing FinBERT tokenizer & model...")
            def update_prog(curr, tot):
                prog_bar.progress(curr / tot, text=f"Evaluating dispatch {curr} of {tot}...")
            
            with st.spinner("Executing FinBERT batch classification..."):
                run_finbert_on_emails(pending_emails, progress_callback=update_prog)
            
            st.success("Batch classification completed and persisted to SQLite.")
            st.rerun()
    else:
        st.markdown("""
        <div style="padding: 0.65rem 0.85rem; background-color: #E8F5F1; border: 1px solid #A3D9C9; border-radius: 8px; font-size: 0.84rem; color: #18866B; margin-bottom: 0.75rem;">
            ✓ All imported communications have current sentiment classifications.
        </div>
        """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📑 Open Daily Briefing", use_container_width=True):
            st.switch_page("pages/4_Daily_Digest.py")
    with col_btn2:
        if st.button("🔬 Open Model Lab", use_container_width=True):
            st.switch_page("pages/3_Model_Lab.py")

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# Recent Activity Ledger
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
    <div style="font-size: 1.15rem; font-weight: 600; color: #172B3A;">
        Chronological Communication Ledger
    </div>
</div>
""", unsafe_allow_html=True)

f_c1, f_c2 = st.columns([1, 2])
with f_c1:
    sentiment_filter = st.selectbox(
        "Filter Stream by Polarity",
        options=["All", "Positive", "Neutral", "Negative"],
        index=0
    )
with f_c2:
    search_term = st.text_input(
        "Filter by Subject / Sender",
        placeholder="Type keyword to filter ledger...",
        key="dash_search"
    )

recent_emails = get_emails_with_latest_predictions(
    sentiment_filter=None if sentiment_filter == "All" else sentiment_filter.lower(),
    search_query=search_term if search_term.strip() else None,
    limit=50
)

if recent_emails:
    display_rows = []
    for r in recent_emails:
        sent = r["pred_sentiment"] or "Pending"
        conf_val = max(r['positive_score'] or 0, r['negative_score'] or 0, r['neutral_score'] or 0)
        display_rows.append({
            "ID": f"#{r['email_id']:04d}",
            "Subject": r["subject"],
            "Sender": r["sender"],
            "Received": r["received_at"][:16].replace("T", " ") if r["received_at"] else "",
            "Sentiment": sent.capitalize(),
            "Confidence": f"{conf_val:.1%}" if r["pred_sentiment"] else "Pending",
            "Model": r["model_name"] or "None"
        })
    df_display = pd.DataFrame(display_rows)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("No communications match the specified filter criteria.")

render_disclaimer_callout()
