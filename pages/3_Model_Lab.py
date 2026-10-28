"""
Invoice Digest — Screen C: Model Evaluation Lab
Comparative Benchmarking: Pretrained FinBERT Transformer vs BiLSTM Sequence Classifier
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
from src.ui_theme import (
    apply_saas_theme,
    apply_plotly_saas_theme,
    render_app_header,
    render_saas_sidebar,
    render_sentiment_badge,
    render_disclaimer_callout,
)

st.set_page_config(
    page_title="Model Evaluation Lab | Invoice Digest",
    page_icon="🔬",
    layout="wide"
)

# Apply global SaaS design system
apply_saas_theme()
render_saas_sidebar(active_page="models")
init_database()

# Header
render_app_header(
    title="Model Evaluation & Benchmark Lab",
    subtitle="Comparative empirical assessment: Pretrained FinBERT Transformer versus Supervised Bidirectional LSTM Baseline.",
    kicker="RESEARCH & BENCHMARKING DIVISION"
)

# Benchmark Overview Card & Execution Desk
b_col1, b_col2 = st.columns([3, 1])
with b_col1:
    st.markdown("""
    <div class="saas-card" style="margin-bottom: 0;">
        <div style="font-size: 0.95rem; font-weight: 600; color: #172B3A; margin-bottom: 0.25rem;">
            Empirical Evaluation Objective
        </div>
        <div style="font-size: 0.85rem; color: #74808B; line-height: 1.6;">
            Evaluates whether domain-specialized transformer representations (<strong>FinBERT</strong>) 
            provide statistically meaningful advantages in Macro F1 and semantic transfer over a supervised 
            recurrent baseline (<strong>BiLSTM</strong>) on held-out commercial invoices.
        </div>
        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #9A6B1F; background-color: #FBF4E8; border: 1px solid #F3DCB3; border-radius: 6px; padding: 0.4rem 0.65rem;">
            <strong>Sample Size Disclosure:</strong> Benchmark evaluation utilizes the held-out test split (<code>data/test.csv</code>, <em>N = 6</em> balanced samples). While small, it enforces strict out-of-sample isolation for qualitative architecture benchmarking.
        </div>
    </div>
    """, unsafe_allow_html=True)
with b_col2:
    st.markdown('<div style="height: 4px;"></div>', unsafe_allow_html=True)
    if st.button("🔄 Run Held-Out Test Evaluation", type="primary", use_container_width=True):
        with st.spinner("Benchmarking both architectures on test split..."):
            evaluate_both_models_on_test_set()
        st.success("Test set evaluation completed and metrics persisted.")
        st.rerun()

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# Load Benchmark Metrics from reports/
report_csv = "reports/model_comparison_metrics.csv"
if os.path.isfile(report_csv):
    df_metrics = pd.read_csv(report_csv)
    
    st.markdown("""
    <div style="font-size: 1.15rem; font-weight: 600; color: #172B3A; margin-bottom: 0.5rem;">
        Held-Out Test Set Benchmark Results
    </div>
    """, unsafe_allow_html=True)

    m_col1, m_col2 = st.columns(2)
    fb_row = df_metrics[df_metrics["Model"].str.contains("FinBERT")].iloc[0]
    lstm_row = df_metrics[df_metrics["Model"].str.contains("BiLSTM")].iloc[0]

    with m_col1:
        st.markdown("""
        <div class="saas-card" style="border-top: 3px solid #172B3A; margin-bottom: 0.75rem;">
            <div style="font-size: 0.72rem; font-weight: 600; color: #172B3A; letter-spacing: 0.05em; text-transform: uppercase;">
                PRIMARY ARCHITECTURE
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #172B3A; margin-top: 2px;">
                FinBERT (Domain Transformer)
            </div>
            <div style="font-size: 0.8rem; color: #74808B; margin-top: 2px;">
                110M parameters • ProsusAI Pretrained Weights • MPS/CUDA/CPU
            </div>
        </div>
        """, unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        k1.metric("Macro F1", f"{fb_row['Macro F1']:.3f}")
        k2.metric("Accuracy", f"{fb_row['Accuracy']:.1%}")
        k3.metric("Latency", f"{fb_row['Latency (ms/email)']:.1f} ms/item")
        st.caption(f"Macro Precision: {fb_row['Macro Precision']:.3f} | Macro Recall: {fb_row['Macro Recall']:.3f}")

    with m_col2:
        st.markdown("""
        <div class="saas-card" style="border-top: 3px solid #18866B; margin-bottom: 0.75rem;">
            <div style="font-size: 0.72rem; font-weight: 600; color: #18866B; letter-spacing: 0.05em; text-transform: uppercase;">
                COMPARISON BASELINE
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #172B3A; margin-top: 2px;">
                BiLSTM (Supervised Recurrent)
            </div>
            <div style="font-size: 0.8rem; color: #74808B; margin-top: 2px;">
                2-Layer Bidirectional • PyTorch nn.LSTM • Embedded Vocabulary
            </div>
        </div>
        """, unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        k1.metric("Macro F1", f"{lstm_row['Macro F1']:.3f}")
        k2.metric("Accuracy", f"{lstm_row['Accuracy']:.1%}")
        k3.metric("Latency", f"{lstm_row['Latency (ms/email)']:.1f} ms/item")
        st.caption(f"Macro Precision: {lstm_row['Macro Precision']:.3f} | Macro Recall: {lstm_row['Macro Recall']:.3f}")

    # Comparative Performance Bar Chart
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
        color_discrete_sequence=["#172B3A", "#18866B"],
        title="Side-by-Side Model Comparison on Held-Out Test Set"
    )
    bar_fig.update_layout(
        yaxis=dict(range=[0, 1.05], tickformat=".0%"),
        height=280
    )
    apply_plotly_saas_theme(bar_fig)
    st.plotly_chart(bar_fig, use_container_width=True)

    with open(report_csv, "rb") as f:
        st.download_button(
            label="📥 Export Comparative Metrics Table (CSV)",
            data=f,
            file_name="model_comparison_metrics.csv",
            mime="text/csv"
        )
else:
    st.info("No saved test evaluation found. Select 'Run Held-Out Test Evaluation' to calculate performance benchmarks.")

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# Interactive Sandbox
st.markdown("""
<div style="font-size: 1.15rem; font-weight: 600; color: #172B3A; margin-bottom: 0.25rem;">
    Interactive Sentiment Testbench
</div>
<div style="font-size: 0.82rem; color: #74808B; margin-bottom: 0.75rem;">
    Submit arbitrary invoice, billing, or inquiry text to test real-time comparative inference without retraining:
</div>
""", unsafe_allow_html=True)

play_subject = st.text_input("Dispatch Subject", value="Immediate Account Hold: Invoice #8841 Overdue", key="sandbox_subj")
play_body = st.text_area(
    "Correspondence Body Text",
    value="Final reminder: invoice #8841 ($4,500.00) is 60 days overdue. Please submit remittance confirmation within 24 hours to prevent immediate service suspension.",
    height=85,
    key="sandbox_body"
)

if st.button("🔮 Run Multi-Model Comparison on Sample", type="primary", key="sandbox_run"):
    c_res1, c_res2 = st.columns(2)
    
    with c_res1:
        st.markdown("**FinBERT Transformer:**")
        with st.spinner("Evaluating FinBERT..."):
            fb_clf = get_finbert_classifier()
            fb_res = fb_clf.predict_email(play_subject, play_body)
            sent = fb_res["sentiment"]
            conf = max(fb_res["positive_score"], fb_res["neutral_score"], fb_res["negative_score"])
            st.markdown(render_sentiment_badge(sent, conf), unsafe_allow_html=True)
            st.caption(f"Inference Latency: {fb_res['inference_ms']} ms")

            fig1 = px.bar(
                x=[fb_res["positive_score"], fb_res["neutral_score"], fb_res["negative_score"]],
                y=["Positive", "Neutral", "Negative"],
                orientation="h",
                color=["Positive", "Neutral", "Negative"],
                color_discrete_map={"Positive": "#18866B", "Neutral": "#DDA348", "Negative": "#D96C63"},
                labels={"x": "Probability", "y": "Class"}
            )
            fig1.update_layout(height=130, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
            apply_plotly_saas_theme(fig1)
            st.plotly_chart(fig1, use_container_width=True)

    with c_res2:
        st.markdown("**BiLSTM Supervised Baseline:**")
        lstm_clf = LSTMClassifier()
        if not lstm_clf.is_trained():
            st.warning("BiLSTM model checkpoint not located in models/lstm_checkpoint.")
        else:
            with st.spinner("Evaluating BiLSTM..."):
                lstm_res = lstm_clf.predict_email(play_subject, play_body)
                l_sent = lstm_res["sentiment"]
                l_conf = max(lstm_res["positive_score"], lstm_res["neutral_score"], lstm_res["negative_score"])
                st.markdown(render_sentiment_badge(l_sent, l_conf), unsafe_allow_html=True)
                st.caption(f"Inference Latency: {lstm_res['inference_ms']} ms")

                fig2 = px.bar(
                    x=[lstm_res["positive_score"], lstm_res["neutral_score"], lstm_res["negative_score"]],
                    y=["Positive", "Neutral", "Negative"],
                    orientation="h",
                    color=["Positive", "Neutral", "Negative"],
                    color_discrete_map={"Positive": "#18866B", "Neutral": "#DDA348", "Negative": "#D96C63"},
                    labels={"x": "Probability", "y": "Class"}
                )
                fig2.update_layout(height=130, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
                apply_plotly_saas_theme(fig2)
                st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# Historical Experiment Runs Database Log
st.markdown("""
<div style="font-size: 1.15rem; font-weight: 600; color: #172B3A; margin-bottom: 0.5rem;">
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

render_disclaimer_callout()
