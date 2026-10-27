"""
Invoice Digest — Screen D: Daily Digest
Automated Daily Financial Report Generation, High-Risk Negative Communication Filtering,
and CSV / Markdown Snapshot Exports.
Redesigned with a Minimal, Premium Editorial & Newspaper-Inspired Theme.
"""

from datetime import datetime, date
import pandas as pd
import streamlit as st
from src.database import DEFAULT_DB_PATH, get_db_connection, init_database
from src.report_generator import export_digest_to_csv, generate_daily_digest
from src.ui_theme import (
    apply_editorial_theme,
    render_editorial_masthead,
    render_editorial_sidebar,
)

st.set_page_config(
    page_title="Daily Digest | Invoice Digest",
    page_icon="📰",
    layout="wide"
)

# Apply global editorial theme and styling
apply_editorial_theme()
render_editorial_sidebar()

init_database()

# Editorial Masthead
render_editorial_masthead(
    title="DAILY FINANCIAL DIGEST",
    subtitle="Actionable Intelligence Briefing, High-Risk Communication Register & Executive Summary",
    kicker="MORNING FINANCIAL DISPATCH"
)

# Date Selection Bar
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT SUBSTR(received_at, 1, 10) as dt FROM emails ORDER BY dt DESC;")
    dates = [row["dt"] for row in cursor.fetchall() if row["dt"]]

today_str = date.today().isoformat()
default_date = dates[0] if dates else today_str

col_d1, col_d2 = st.columns([2, 1])
with col_d1:
    selected_date = st.selectbox(
        "Select Reporting Calendar Date:",
        options=dates if dates else [today_str],
        index=0
    )
with col_d2:
    st.write("")
    st.write("")
    gen_btn = st.button("⚡ Generate & Compile Daily Digest", type="primary", use_container_width=True)

# Generate Digest for selected date
digest = generate_daily_digest(selected_date, save_snapshot=True)

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# KPI Cards for Selected Date
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Communications", digest["total_emails"])
k2.metric("Positive Confirmations", digest["positive_count"], delta="Settled / Credits")
k3.metric("Neutral Operations", digest["neutral_count"], delta="Standard Bills / POs")
k4.metric(
    "Negative High-Risk",
    digest["negative_count"],
    delta="Action Required" if digest["negative_count"] > 0 else "All Clear",
    delta_color="inverse"
)

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# Priority Review: Negative Communications
st.markdown("""
<div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 0.5rem;">
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.35rem; font-weight: 700; color: #1A1A1A;">
        Priority Register: Adverse Communications Requiring Review
    </div>
</div>
""", unsafe_allow_html=True)

if digest["negative_emails"]:
    st.markdown("""
    <div class="editorial-card" style="border-left: 3px solid #B91C1C; background-color: #FEF2F2; margin-bottom: 1rem;">
        <span style="font-weight: 600; color: #991B1B;">URGENT AUDIT NOTICE:</span>
        <span style="color: #7F1D1D; font-size: 0.9rem;">
            The following communications exhibit high negative sentiment polarity indicative of past-due notices, 
            service cancellation warnings, or billing disputes. Immediate review is advised.
        </span>
    </div>
    """, unsafe_allow_html=True)

    neg_display = []
    for item in digest["negative_emails"]:
        neg_display.append({
            "Subject": item["subject"],
            "Sender": item["sender"],
            "Negative Confidence": f"{item['negative_score']:.1%}",
            "Correspondence Excerpt": item["body_text"][:160] + "..."
        })
    df_neg = pd.DataFrame(neg_display)
    st.dataframe(df_neg, use_container_width=True, hide_index=True)
else:
    st.markdown("""
    <div class="editorial-card" style="border-left: 3px solid #15803D; background-color: #F0FDF4;">
        <span style="font-weight: 600; color: #166534;">STATUS NORMAL:</span>
        <span style="color: #14532D; font-size: 0.9rem;">
            No adverse or contentious communications were detected for this date. All inbound dispatches remain within standard operational tolerance.
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)

# Formatted Markdown Report Preview & Export
c_rep1, c_rep2 = st.columns([3, 2])

with c_rep1:
    st.markdown("""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.35rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.5rem;">
        Executive Briefing Document (Formatted Snapshot)
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="editorial-card-elevated" style="font-family: 'Libre Baskerville', Georgia, serif; font-size: 0.95rem; line-height: 1.7; color: #1A1A1A; padding: 2rem; border-top: 3px solid #1A1A1A;">
{digest['report_markdown']}
    </div>
    """, unsafe_allow_html=True)

with c_rep2:
    st.markdown("""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.35rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.5rem;">
        Dispatch & Export Desk
    </div>
    <div style="font-size: 0.88rem; color: #66635E; margin-bottom: 1rem;">
        Export authenticated reports or transmit directly to executive stakeholders:
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="editorial-card-elevated">', unsafe_allow_html=True)
    
    csv_data = export_digest_to_csv(digest["all_emails"])
    st.download_button(
        label="📥 Download Daily Digest Ledger (CSV)",
        data=csv_data,
        file_name=f"invoice_digest_{selected_date}.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown('<div style="height: 6px;"></div>', unsafe_allow_html=True)

    st.download_button(
        label="📑 Download Formatted Briefing (Markdown)",
        data=digest["report_markdown"],
        file_name=f"invoice_digest_{selected_date}.md",
        mime="text/markdown",
        use_container_width=True
    )

    st.markdown('<hr class="editorial-divider">', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.1rem; font-weight: 700; color: #1A1A1A; margin-bottom: 0.35rem;">
        SMTP Transmission Terminal
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Dispatch via Email (SMTP)", expanded=False):
        dest_email = st.text_input("Recipient Address", placeholder="executive@enterprise.com", key="dest_email")
        smtp_sender = st.text_input("Sender Address", placeholder="digest-bot@gmail.com", key="smtp_sender")
        smtp_pass = st.text_input("16-Character App Token", type="password", key="smtp_pass")

        if st.button("🚀 Transmit Digest to Recipient", type="primary", use_container_width=True):
            if not dest_email or not smtp_sender or not smtp_pass:
                st.error("Please supply recipient address, sender address, and app token.")
            else:
                with st.spinner("Dispatching formatted digest over TLS..."):
                    from src.email_service import send_daily_digest_email
                    ok, msg_out = send_daily_digest_email(
                        recipient_email=dest_email,
                        sender_email=smtp_sender,
                        app_password=smtp_pass,
                        report_date=selected_date,
                        report_markdown=digest["report_markdown"],
                        csv_content=csv_data,
                        report_id=digest.get("report_id")
                    )
                    if ok:
                        st.success(msg_out)
                    else:
                        st.error(f"Transmission failed: {msg_out}")

    st.markdown("""
    <div style="font-size: 0.78rem; color: #66635E; margin-top: 0.5rem;">
        RECORD STATUS: <strong>VERIFIED / PERSISTED TO SQLITE</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
