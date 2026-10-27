"""
Invoice Digest — Screen B: Email Analysis
Granular Email Inspection, Comparative Probability Breakdown & Human Label Audit.
Redesigned with a Minimal, Premium Editorial & Newspaper-Inspired Theme.
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
from src.lstm_model import LSTMClassifier
from src.preprocessing import prepare_email_for_model
from src.ui_theme import (
    apply_editorial_theme,
    apply_plotly_editorial_theme,
    render_editorial_masthead,
    render_editorial_sidebar,
)

st.set_page_config(
    page_title="Email Analysis | Invoice Digest",
    page_icon="📰",
    layout="wide"
)

# Apply global editorial theme and styling
apply_editorial_theme()
render_editorial_sidebar()

init_database()

# Editorial Masthead
render_editorial_masthead(
    title="EMAIL AUDIT & VERIFICATION",
    subtitle="Detailed Correspondence Inspection, Multi-Model Confidence & Human Verification",
    kicker="INVESTIGATIVE AUDIT DESK"
)

# Filters and Search Bar
st.markdown("""
<div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.25rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.25rem;">
    Search & Filter Correspondence Ledger
</div>
""", unsafe_allow_html=True)

f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
with f_col1:
    search_query = st.text_input(
        "Search by Subject, Sender, or Body Keyword",
        placeholder="e.g., overdue, wire transfer, billing dispute, invoice #..."
    )
with f_col2:
    sentiment_filter = st.selectbox(
        "Filter by Polarity",
        options=["All", "Positive", "Negative", "Neutral"],
        index=0
    )
with f_col3:
    limit_select = st.selectbox("Max Display Records", options=[25, 50, 100], index=1)

emails = get_emails_with_latest_predictions(
    sentiment_filter=None if sentiment_filter == "All" else sentiment_filter.lower(),
    search_query=search_query if search_query.strip() else None,
    limit=limit_select
)

if not emails:
    st.warning("No records match your search query or filter criteria.")
    st.stop()

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# Master-Detail Layout
col_list, col_detail = st.columns([1, 2])

with col_list:
    st.markdown(f"""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.15rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.5rem;">
        Indexed Dispatches ({len(emails)})
    </div>
    <div style="font-size: 0.8rem; color: #66635E; margin-bottom: 0.75rem;">
        Select an entry to examine full record:
    </div>
    """, unsafe_allow_html=True)

    email_titles = [f"#{e['email_id']:04d} — {e['subject'][:32]}..." for e in emails]
    selected_idx = st.radio(
        "Select email to inspect:",
        options=range(len(emails)),
        format_func=lambda i: email_titles[i],
        label_visibility="collapsed"
    )

selected_email = emails[selected_idx]

with col_detail:
    st.markdown(f"""
    <div style="border-bottom: 1px solid #E5E1D8; padding-bottom: 0.5rem; margin-bottom: 1rem;">
        <span class="badge-editorial badge-neutral">RECORD #{selected_email['email_id']:04d}</span>
        <span style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.4rem; font-weight: 700; color: #1A1A1A; margin-left: 0.5rem;">
            {selected_email['subject']}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Metadata Ledger
    m1, m2, m3 = st.columns(3)
    m1.markdown(f"<div style='font-size: 0.82rem; color: #66635E;'>SENDER</div><div style='font-family: monospace; font-size: 0.88rem; color: #1A1A1A;'>{selected_email['sender']}</div>", unsafe_allow_html=True)
    m2.markdown(f"<div style='font-size: 0.82rem; color: #66635E;'>TIMESTAMP (UTC)</div><div style='font-size: 0.88rem; color: #1A1A1A;'>{selected_email['received_at'][:19].replace('T', ' ')}</div>", unsafe_allow_html=True)
    m3.markdown(f"<div style='font-size: 0.82rem; color: #66635E;'>SOURCE ID</div><div style='font-family: monospace; font-size: 0.88rem; color: #1A1A1A;'>{selected_email['source_id'] or 'Manual / Stream'}</div>", unsafe_allow_html=True)

    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
    
    # Correspondence Body rendered as clean editorial manuscript
    st.markdown(f"""
    <div style="font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #66635E; margin-bottom: 0.25rem;">
        Original Correspondence Transcript
    </div>
    <div class="editorial-card-elevated" style="font-family: 'Libre Baskerville', Georgia, serif; font-size: 0.95rem; line-height: 1.7; color: #1A1A1A; min-height: 120px; white-space: pre-wrap; background-color: #FFFFFF; border-left: 3px solid #1A1A1A;">
{selected_email['body_text']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)
    
    # Model Predictions & Probabilities
    st.markdown("""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.25rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.75rem;">
        Model Inference & Probability Vectors
    </div>
    """, unsafe_allow_html=True)

    finbert_sent = selected_email["pred_sentiment"] or "Not Run"
    pos_score = selected_email["positive_score"] or 0.0
    neg_score = selected_email["negative_score"] or 0.0
    neu_score = selected_email["neutral_score"] or 0.0

    p_col1, p_col2 = st.columns([1, 1])

    with p_col1:
        st.markdown("**Primary Model: FinBERT (Domain Transformer)**")
        if finbert_sent == "positive":
            st.markdown(f'<div class="badge-editorial badge-positive" style="font-size: 0.85rem; padding: 4px 10px;">POSITIVE • {pos_score:.1%} CONFIDENCE</div>', unsafe_allow_html=True)
        elif finbert_sent == "negative":
            st.markdown(f'<div class="badge-editorial badge-negative" style="font-size: 0.85rem; padding: 4px 10px;">NEGATIVE • {neg_score:.1%} CONFIDENCE</div>', unsafe_allow_html=True)
        elif finbert_sent == "neutral":
            st.markdown(f'<div class="badge-editorial badge-neutral" style="font-size: 0.85rem; padding: 4px 10px;">NEUTRAL • {neu_score:.1%} CONFIDENCE</div>', unsafe_allow_html=True)
        else:
            st.warning("Awaiting initial FinBERT inference.")

        # Plotly probability bar chart (Clean editorial styling)
        if selected_email["pred_sentiment"]:
            prob_df = pd.DataFrame({
                "Sentiment": ["Positive", "Neutral", "Negative"],
                "Probability": [pos_score, neu_score, neg_score]
            })
            bar_fig = go.Figure(go.Bar(
                x=prob_df["Probability"],
                y=prob_df["Sentiment"],
                orientation="h",
                marker=dict(
                    color=["#0F766E", "#66635E", "#1E40AF"],
                    line=dict(color="#1A1A1A", width=0.5)
                )
            ))
            bar_fig.update_layout(
                xaxis=dict(range=[0, 1], tickformat=".0%"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=140
            )
            apply_plotly_editorial_theme(bar_fig)
            st.plotly_chart(bar_fig, use_container_width=True)

    with p_col2:
        st.markdown("**Benchmark Model: BiLSTM Baseline**")
        lstm_clf = LSTMClassifier()
        if lstm_clf.is_trained():
            try:
                lstm_res = lstm_clf.predict_email(selected_email["subject"], selected_email["body_text"])
                lstm_sent = lstm_res["sentiment"]
                if lstm_sent == finbert_sent:
                    st.markdown(f'<div class="badge-editorial badge-positive" style="font-size: 0.85rem; padding: 4px 10px;">CLASSIFIED: {lstm_sent.upper()} (MODELS CONCUR)</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-editorial badge-negative" style="font-size: 0.85rem; padding: 4px 10px;">CLASSIFIED: {lstm_sent.upper()} (DISAGREES WITH FINBERT)</div>', unsafe_allow_html=True)
                
                st.caption(f"BiLSTM Probabilities: Negative: {lstm_res['negative_score']:.1%} | Neutral: {lstm_res['neutral_score']:.1%} | Positive: {lstm_res['positive_score']:.1%}")
            except Exception as e:
                st.caption(f"BiLSTM inference error: {e}")
        else:
            st.info("BiLSTM checkpoint not trained yet. Train model in Model Lab.")

    st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)
    
    # Human Ground Truth Verification
    st.markdown("""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.25rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.35rem;">
        Human Verification & Ground Truth Audit
    </div>
    """, unsafe_allow_html=True)
    
    current_human_label = selected_email.get("human_label")
    if current_human_label:
        st.markdown(f"""
        <div style="margin-bottom: 0.75rem;">
            <span style="font-size: 0.85rem; color: #66635E;">Verified Ground Truth:</span>
            <span class="badge-editorial badge-accent" style="margin-left: 0.5rem;">{current_human_label.upper()}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size: 0.85rem; color: #66635E; margin-bottom: 0.75rem;'>No human verification recorded yet for this entry.</div>", unsafe_allow_html=True)

    v1, v2, v3 = st.columns(3)
    with v1:
        if st.button("Mark Positive (Settled / Credit)", key=f"btn_pos_{selected_email['email_id']}", use_container_width=True):
            save_human_label(selected_email["email_id"], "positive", labeled_by="auditor")
            st.success("Logged Positive ground truth label.")
            st.rerun()
    with v2:
        if st.button("Mark Neutral (Standard / Invoice)", key=f"btn_neu_{selected_email['email_id']}", use_container_width=True):
            save_human_label(selected_email["email_id"], "neutral", labeled_by="auditor")
            st.success("Logged Neutral ground truth label.")
            st.rerun()
    with v3:
        if st.button("Mark Negative (Dispute / Hold)", key=f"btn_neg_{selected_email['email_id']}", use_container_width=True):
            save_human_label(selected_email["email_id"], "negative", labeled_by="auditor")
            st.success("Logged Negative ground truth label.")
            st.rerun()
