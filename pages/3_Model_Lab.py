"""
Invoice Digest — Screen C: Model Lab
Comparative Benchmarking: Pretrained FinBERT Transformer vs BiLSTM Sequence Classifier.
Redesigned with a Minimal, Premium Editorial & Newspaper-Inspired Theme.
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.database import DEFAULT_DB_PATH, get_db_connection, init_database
from src.evaluation import compute_classification_metrics
from src.finbert_model import FinBERTClassifier, get_finbert_classifier
from src.lstm_model import LSTMClassifier
from training.evaluate_models import evaluate_both_models_on_test_set
from training.train_lstm import train_lstm_model
from src.ui_theme import (
    apply_editorial_theme,
    apply_plotly_editorial_theme,
    render_editorial_masthead,
    render_editorial_sidebar,
)

st.set_page_config(
    page_title="Model Lab | Invoice Digest",
    page_icon="📰",
    layout="wide"
)

# Apply global editorial theme and styling
apply_editorial_theme()
render_editorial_sidebar()

init_database()

# Editorial Masthead
render_editorial_masthead(
    title="MODEL EVALUATION LAB",
    subtitle="Rigorous Benchmarking: Pretrained FinBERT Transformer vs. Supervised BiLSTM Baseline",
    kicker="RESEARCH & BENCHMARKING DIVISION"
)

# Benchmark Overview & Execution Desk
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.markdown("""
    <div style="font-family: 'Inter', sans-serif; font-size: 0.95rem; line-height: 1.7; color: #1A1A1A;">
        This laboratory tests the foundational empirical hypothesis: 
        <strong>Does a specialized financial domain transformer (FinBERT) achieve statistically significant 
        superiority in macro F1 score and generalization over a recurrent neural baseline (BiLSTM) 
        on strictly held-out test splits?</strong>
    </div>
    """, unsafe_allow_html=True)
with top_col2:
    if st.button("🔄 Execute Held-Out Test Evaluation", type="primary", use_container_width=True):
        with st.spinner("Benchmarking both models on identical held-out test split..."):
            evaluate_both_models_on_test_set()
        st.success("Comparative benchmark completed.")
        st.rerun()

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# Load Benchmark Metrics from reports/
report_csv = "reports/model_comparison_metrics.csv"
if os.path.isfile(report_csv):
    df_metrics = pd.read_csv(report_csv)
    
    st.markdown("""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.35rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.75rem;">
        Comparative Benchmark Results (Held-Out Test Dataset)
    </div>
    """, unsafe_allow_html=True)
    
    # Comparison Cards
    m_col1, m_col2 = st.columns(2)
    
    fb_row = df_metrics[df_metrics["Model"].str.contains("FinBERT")].iloc[0]
    lstm_row = df_metrics[df_metrics["Model"].str.contains("BiLSTM")].iloc[0]

    with m_col1:
        st.markdown("""
        <div class="editorial-card-elevated" style="border-top: 3px solid #1E40AF; margin-bottom: 0.5rem;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #1E40AF; letter-spacing: 0.08em; text-transform: uppercase;">PRIMARY ARCHITECTURE</div>
            <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.35rem; font-weight: 700; color: #1A1A1A; margin-top: 2px;">
                FinBERT (Domain Transformer)
            </div>
        </div>
        """, unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        k1.metric("Macro F1", f"{fb_row['Macro F1']:.3f}")
        k2.metric("Accuracy", f"{fb_row['Accuracy']:.1%}")
        k3.metric("Latency / Email", f"{fb_row['Latency (ms/email)']:.1f} ms")
        st.caption(f"Precision: {fb_row['Macro Precision']:.3f} | Recall: {fb_row['Macro Recall']:.3f}")

    with m_col2:
        st.markdown("""
        <div class="editorial-card-elevated" style="border-top: 3px solid #0F766E; margin-bottom: 0.5rem;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #0F766E; letter-spacing: 0.08em; text-transform: uppercase;">BASELINE ARCHITECTURE</div>
            <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.35rem; font-weight: 700; color: #1A1A1A; margin-top: 2px;">
                BiLSTM (Supervised Baseline)
            </div>
        </div>
        """, unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        k1.metric("Macro F1", f"{lstm_row['Macro F1']:.3f}")
        k2.metric("Accuracy", f"{lstm_row['Accuracy']:.1%}")
        k3.metric("Latency / Email", f"{lstm_row['Latency (ms/email)']:.1f} ms")
        st.caption(f"Precision: {lstm_row['Macro Precision']:.3f} | Recall: {lstm_row['Macro Recall']:.3f}")

    st.markdown('<div style="height: 14px;"></div>', unsafe_allow_html=True)
    
    # Comparative Bar Chart
    comp_melt = pd.melt(
        df_metrics,
        id_vars=["Model"],
        value_vars=["Accuracy", "Macro F1", "Macro Precision", "Macro Recall"],
        var_name="Metric",
        value_name="Score"
    )
    bar_fig = px.bar(
        comp_melt,
        x="Metric",
        y="Score",
        color="Model",
        barmode="group",
        color_discrete_sequence=["#1E40AF", "#0F766E"],
        title="Side-by-Side Performance Comparison"
    )
    bar_fig.update_layout(
        yaxis=dict(range=[0, 1.05], tickformat=".0%"),
        height=300
    )
    apply_plotly_editorial_theme(bar_fig)
    st.plotly_chart(bar_fig, use_container_width=True)

    # Export metrics CSV button
    with open(report_csv, "rb") as f:
        st.download_button(
            label="📥 Export Comparative Metrics Table (CSV)",
            data=f,
            file_name="model_comparison_metrics.csv",
            mime="text/csv"
        )
else:
    st.info("No saved test evaluation found. Select 'Execute Held-Out Test Evaluation' to calculate performance benchmarks.")

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# Section: Interactive Inference Playground
st.markdown("""
<div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.35rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.25rem;">
    Interactive Sentiment Testbench
</div>
<div style="font-size: 0.88rem; color: #66635E; margin-bottom: 0.75rem;">
    Submit arbitrary invoice, billing, or dispute text to test real-time model inference:
</div>
""", unsafe_allow_html=True)

play_subject = st.text_input("Dispatch Subject", value="Notice of Immediate Account Hold - Invoice #5589 Overdue")
play_body = st.text_area(
    "Correspondence Body Text",
    value="This is our final reminder regarding unpaid invoice #5589 in the amount of $3,200.00. Unless wire transfer confirmation is provided by 5 PM today, your subscription and database access will be placed on administrative hold.",
    height=95
)

if st.button("🔮 Evaluate Live Inference Across Models", type="primary"):
    c_res1, c_res2 = st.columns(2)
    
    with c_res1:
        st.markdown("**FinBERT Inference Result:**")
        with st.spinner("Executing FinBERT inference..."):
            fb_clf = get_finbert_classifier()
            fb_res = fb_clf.predict_email(play_subject, play_body)
            
            sent = fb_res["sentiment"]
            if sent == "positive":
                st.markdown(f'<div class="badge-editorial badge-positive" style="font-size: 0.85rem; padding: 4px 10px;">POSITIVE • {fb_res["positive_score"]:.1%} CONFIDENCE</div>', unsafe_allow_html=True)
            elif sent == "negative":
                st.markdown(f'<div class="badge-editorial badge-negative" style="font-size: 0.85rem; padding: 4px 10px;">NEGATIVE • {fb_res["negative_score"]:.1%} CONFIDENCE</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="badge-editorial badge-neutral" style="font-size: 0.85rem; padding: 4px 10px;">NEUTRAL • {fb_res["neutral_score"]:.1%} CONFIDENCE</div>', unsafe_allow_html=True)
            
            st.caption(f"Inference Latency: {fb_res['inference_ms']} ms")
            
            fig1 = px.bar(
                x=[fb_res["positive_score"], fb_res["neutral_score"], fb_res["negative_score"]],
                y=["Positive", "Neutral", "Negative"],
                orientation="h",
                color=["Positive", "Neutral", "Negative"],
                color_discrete_map={"Positive": "#0F766E", "Neutral": "#66635E", "Negative": "#1E40AF"},
                labels={"x": "Probability", "y": "Class"}
            )
            fig1.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
            apply_plotly_editorial_theme(fig1)
            st.plotly_chart(fig1, use_container_width=True)

    with c_res2:
        st.markdown("**BiLSTM Inference Result:**")
        lstm_clf = LSTMClassifier()
        if not lstm_clf.is_trained():
            st.warning("BiLSTM model checkpoint not located in models/lstm_checkpoint.")
        else:
            with st.spinner("Executing BiLSTM inference..."):
                lstm_res = lstm_clf.predict_email(play_subject, play_body)
                
                l_sent = lstm_res["sentiment"]
                if l_sent == "positive":
                    st.markdown(f'<div class="badge-editorial badge-positive" style="font-size: 0.85rem; padding: 4px 10px;">POSITIVE • {lstm_res["positive_score"]:.1%} CONFIDENCE</div>', unsafe_allow_html=True)
                elif l_sent == "negative":
                    st.markdown(f'<div class="badge-editorial badge-negative" style="font-size: 0.85rem; padding: 4px 10px;">NEGATIVE • {lstm_res["negative_score"]:.1%} CONFIDENCE</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-editorial badge-neutral" style="font-size: 0.85rem; padding: 4px 10px;">NEUTRAL • {lstm_res["neutral_score"]:.1%} CONFIDENCE</div>', unsafe_allow_html=True)
                
                st.caption(f"Inference Latency: {lstm_res['inference_ms']} ms")
                
                fig2 = px.bar(
                    x=[lstm_res["positive_score"], lstm_res["neutral_score"], lstm_res["negative_score"]],
                    y=["Positive", "Neutral", "Negative"],
                    orientation="h",
                    color=["Positive", "Neutral", "Negative"],
                    color_discrete_map={"Positive": "#0F766E", "Neutral": "#66635E", "Negative": "#1E40AF"},
                    labels={"x": "Probability", "y": "Class"}
                )
                fig2.update_layout(height=140, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
                apply_plotly_editorial_theme(fig2)
                st.plotly_chart(fig2, use_container_width=True)

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# Historical Experiment Runs Database Log
st.markdown("""
<div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.35rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.5rem;">
    Experiment Run Ledger (SQLite <code>model_runs</code>)
</div>
""", unsafe_allow_html=True)

with get_db_connection() as conn:
    df_runs = pd.read_sql_query(
        "SELECT id AS 'Run ID', model_name AS 'Model', dataset_name AS 'Dataset', accuracy AS 'Accuracy', macro_f1 AS 'Macro F1', macro_precision AS 'Precision', macro_recall AS 'Recall', train_time_seconds AS 'Train Time (s)', created_at AS 'Timestamp' FROM model_runs ORDER BY id DESC LIMIT 10;",
        conn
    )

if not df_runs.empty:
    st.dataframe(df_runs, use_container_width=True, hide_index=True)
else:
    st.caption("No historical experiment runs registered in database yet.")
