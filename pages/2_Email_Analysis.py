"""
Invoice Digest — Screen B: Email Analysis & Verification Workspace
Granular Inspection, Multi-Model Confidence Vectors & Human Label Audit
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.database import (
    DEFAULT_DB_PATH,
    get_emails_with_latest_predictions,
    init_database,
    save_human_label,
)
from src.email_import import import_emails_from_csv
from src.lstm_model import LSTMClassifier
from src.preprocessing import prepare_email_for_model
from src.ui_theme import (
    apply_saas_theme,
    apply_plotly_saas_theme,
    render_app_header,
    render_saas_sidebar,
    render_sentiment_badge,
    render_disclaimer_callout,
)

st.set_page_config(
    page_title="Email Analysis & Audit | Invoice Digest",
    page_icon="📥",
    layout="wide"
)

# Apply global SaaS design system
apply_saas_theme()
render_saas_sidebar(active_page="analysis")
init_database()

# Header
render_app_header(
    title="Email Intelligence & Audit Workspace",
    subtitle="Inspect correspondence transcripts, review calibrated multi-model probability vectors, and record human ground-truth verifications.",
    kicker="INTELLIGENT EMAIL WORKSPACE"
)

# Optional Ingestion Desk
with st.expander("📥 Import New Communication Batch (CSV)", expanded=False):
    col_u1, col_u2 = st.columns([3, 1])
    with col_u1:
        up_file = st.file_uploader(
            "Upload CSV file (Required: subject, sender, received_at, body_text; Optional: sentiment)",
            type=["csv"],
            key="analysis_csv_uploader"
        )
    with col_u2:
        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        template_content = "subject,sender,received_at,body_text,sentiment\nINV-1001,billing@vendor.com,2026-10-25T10:00:00Z,\"Payment received for Invoice #1001 with thanks.\",positive\nINV-1002,collections@supplier.org,2026-10-25T11:00:00Z,\"Invoice #2040 is 30 days past due. Please remit payment.\",negative\nINV-1003,orders@parts-depot.com,2026-10-25T12:00:00Z,\"Attached is Purchase Order #PO-9912 for review.\",neutral"
        st.download_button(
            label="📄 CSV Schema Template",
            data=template_content,
            file_name="email_import_template.csv",
            mime="text/csv",
            use_container_width=True
        )

    if up_file is not None:
        if st.button("Process Batch Upload", type="primary", key="btn_import_analysis"):
            with st.spinner("Validating records and indexing SHA-256 hashes..."):
                res = import_emails_from_csv(up_file)
                if res.get("success"):
                    st.success(f"Successfully imported {res['imported']} records ({res['duplicates']} duplicate items reconciled).")
                    st.rerun()
                else:
                    st.error(f"Import Failed: {res.get('error')}")

# Search & Filter Controls
st.markdown("""
<div style="font-size: 1.05rem; font-weight: 600; color: #172B3A; margin-bottom: 0.25rem;">
    Search & Filter Correspondence Ledger
</div>
""", unsafe_allow_html=True)

f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
with f_col1:
    search_query = st.text_input(
        "Search Keyword (Subject, Sender, or Body)",
        placeholder="e.g. overdue, refund, invoice #, wire, discount...",
        key="search_input_audit"
    )
with f_col2:
    sentiment_filter = st.selectbox(
        "Filter by Polarity",
        options=["All", "Positive", "Neutral", "Negative"],
        index=0,
        key="sent_filter_audit"
    )
with f_col3:
    limit_select = st.selectbox("Record Limit", options=[25, 50, 100], index=1, key="limit_audit")

emails = get_emails_with_latest_predictions(
    sentiment_filter=None if sentiment_filter == "All" else sentiment_filter.lower(),
    search_query=search_query if search_query.strip() else None,
    limit=limit_select
)

if not emails:
    st.info("No communications match your search query or polarity filter.")
    st.stop()

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# Master-Detail Split Workspace
col_list, col_detail = st.columns([1, 2])

with col_list:
    st.markdown(f"""
    <div style="font-size: 0.95rem; font-weight: 600; color: #172B3A; margin-bottom: 0.2rem;">
        Indexed Dispatches ({len(emails)})
    </div>
    <div style="font-size: 0.78rem; color: #74808B; margin-bottom: 0.65rem;">
        Select an entry to examine full record and probability breakdown:
    </div>
    """, unsafe_allow_html=True)

    email_options = []
    for e in emails:
        tag = e.get("pred_sentiment") or "pending"
        badge_symbol = "✓" if tag == "positive" else ("!" if tag == "negative" else ("○" if tag == "neutral" else "·"))
        email_options.append(f"#{e['email_id']:04d} [{badge_symbol}] {e['subject'][:30]}...")

    selected_idx = st.radio(
        "Select email to inspect:",
        options=range(len(emails)),
        format_func=lambda i: email_options[i],
        label_visibility="collapsed"
    )

selected_email = emails[selected_idx]

with col_detail:
    # Header Card for Selected Email
    sent_label = selected_email["pred_sentiment"] or "pending"
    badge_html = render_sentiment_badge(sent_label)

    st.markdown(f"""
    <div class="saas-card" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 0.75rem; font-weight: 600; color: #74808B; text-transform: uppercase; letter-spacing: 0.05em;">
                COMMUNICATION RECORD #{selected_email['email_id']:04d}
            </span>
            <div>{badge_html}</div>
        </div>
        <div style="font-size: 1.25rem; font-weight: 700; color: #172B3A; line-height: 1.3;">
            {selected_email['subject']}
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #E4E7E5; font-size: 0.82rem;">
            <div><span style="color: #74808B;">Sender:</span> <strong style="color: #172B3A;">{selected_email['sender']}</strong></div>
            <div><span style="color: #74808B;">Timestamp:</span> <strong style="color: #172B3A;">{selected_email['received_at'][:19].replace('T', ' ')} UTC</strong></div>
            <div><span style="color: #74808B;">Source ID:</span> <strong style="color: #172B3A;">{selected_email['source_id'] or 'Manual / Stream'}</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Transcript Card
    st.markdown("""
    <div style="font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #74808B; margin-bottom: 0.25rem;">
        Full Correspondence Body Text
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="saas-card" style="font-size: 0.92rem; line-height: 1.65; color: #202B35; background-color: #FAF9F5; border-left: 3px solid #172B3A; min-height: 110px; white-space: pre-wrap;">
{selected_email['body_text']}
    </div>
    """, unsafe_allow_html=True)

    # Model Predictions & Probability Breakdown
    st.markdown("""
    <div style="font-size: 1.05rem; font-weight: 600; color: #172B3A; margin-top: 1rem; margin-bottom: 0.5rem;">
        Model Inference & Probability Vectors
    </div>
    """, unsafe_allow_html=True)

    finbert_sent = selected_email["pred_sentiment"]
    pos_score = selected_email["positive_score"] or 0.0
    neg_score = selected_email["negative_score"] or 0.0
    neu_score = selected_email["neutral_score"] or 0.0

    p_col1, p_col2 = st.columns([1, 1])

    with p_col1:
        st.markdown("**Primary Model: FinBERT (Transformer)**")
        if finbert_sent:
            conf_val = max(pos_score, neg_score, neu_score)
            st.markdown(render_sentiment_badge(finbert_sent, conf_val), unsafe_allow_html=True)

            prob_df = pd.DataFrame({
                "Sentiment": ["Positive", "Neutral", "Negative"],
                "Probability": [pos_score, neu_score, neg_score]
            })
            bar_fig = go.Figure(go.Bar(
                x=prob_df["Probability"],
                y=prob_df["Sentiment"],
                orientation="h",
                marker=dict(
                    color=["#18866B", "#DDA348", "#D96C63"],
                    line=dict(color="#FFFFFF", width=1)
                )
            ))
            bar_fig.update_layout(
                xaxis=dict(range=[0, 1], tickformat=".0%"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=130
            )
            apply_plotly_saas_theme(bar_fig)
            st.plotly_chart(bar_fig, use_container_width=True)
        else:
            st.info("Awaiting FinBERT inference. Run classification from the Dashboard.")

    with p_col2:
        st.markdown("**Comparison Baseline: Supervised BiLSTM**")
        lstm_clf = LSTMClassifier()
        if lstm_clf.is_trained():
            try:
                lstm_res = lstm_clf.predict_email(selected_email["subject"], selected_email["body_text"])
                lstm_sent = lstm_res["sentiment"]
                if finbert_sent and lstm_sent == finbert_sent:
                    st.markdown(f'<span class="saas-badge saas-badge-positive">✓ Models Concur ({lstm_sent.upper()})</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="saas-badge saas-badge-neutral">○ BiLSTM: {lstm_sent.upper()}</span>', unsafe_allow_html=True)

                st.caption(f"Probabilities — Negative: {lstm_res['negative_score']:.1%} | Neutral: {lstm_res['neutral_score']:.1%} | Positive: {lstm_res['positive_score']:.1%}")
                st.caption(f"BiLSTM Latency: {lstm_res['inference_ms']} ms/sample")
            except Exception as e:
                st.caption(f"BiLSTM inference error: {e}")
        else:
            st.info("BiLSTM checkpoint not trained yet.")

    # Human Ground Truth Audit Section
    st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 1.05rem; font-weight: 600; color: #172B3A; margin-bottom: 0.35rem;">
        Human Verification & Ground Truth Audit
    </div>
    """, unsafe_allow_html=True)

    current_human_label = selected_email.get("human_label")
    if current_human_label:
        st.markdown(f"""
        <div style="margin-bottom: 0.75rem; font-size: 0.85rem;">
            <span style="color: #74808B;">Verified Ground Truth:</span>
            <span class="saas-badge saas-badge-navy" style="margin-left: 0.4rem;">{current_human_label.upper()}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size: 0.82rem; color: #74808B; margin-bottom: 0.75rem;'>No human verification label recorded yet for this entry.</div>", unsafe_allow_html=True)

    v1, v2, v3 = st.columns(3)
    with v1:
        if st.button("Mark Positive (Settled)", key=f"btn_pos_{selected_email['email_id']}", use_container_width=True):
            save_human_label(selected_email["email_id"], "positive", labeled_by="auditor")
            st.success("Recorded Positive ground truth label.")
            st.rerun()
    with v2:
        if st.button("Mark Neutral (Standard)", key=f"btn_neu_{selected_email['email_id']}", use_container_width=True):
            save_human_label(selected_email["email_id"], "neutral", labeled_by="auditor")
            st.success("Recorded Neutral ground truth label.")
            st.rerun()
    with v3:
        if st.button("Mark Negative (Review)", key=f"btn_neg_{selected_email['email_id']}", use_container_width=True):
            save_human_label(selected_email["email_id"], "negative", labeled_by="auditor")
            st.success("Recorded Negative ground truth label.")
            st.rerun()

    render_disclaimer_callout()
