"""
Invoice Digest — Screen D: Daily Intelligence Briefing
Daily Operational Reporting, Negative Correspondence Flagging, and Multi-Format Exports
"""

from datetime import datetime, date
import pandas as pd
import streamlit as st
from src.database import DEFAULT_DB_PATH, get_db_connection, init_database
from src.report_generator import export_digest_to_csv, generate_daily_digest
from src.ui_theme import (
    apply_saas_theme,
    render_app_header,
    render_saas_sidebar,
    render_sentiment_badge,
    render_disclaimer_callout,
)

st.set_page_config(
    page_title="Daily Intelligence Briefing | Invoice Digest",
    page_icon="📑",
    layout="wide"
)

# Apply global SaaS design system
apply_saas_theme()
render_saas_sidebar(active_page="digest")
init_database()

# Header
render_app_header(
    title="Daily Intelligence Briefing",
    subtitle="Compiled daily executive report aggregating verified dispatches, flagging negative sentiment items for human review, and exporting audit logs.",
    kicker="OPERATIONAL INTELLIGENCE BRIEFING"
)

# Date Selection & Snapshot Controls
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
        index=0,
        key="select_digest_date"
    )
with col_d2:
    st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
    save_snapshot_btn = st.button("💾 Compile & Save Report Snapshot", type="primary", use_container_width=True)

# Generate or read digest (only save to DB when user clicks button or if first compile)
digest = generate_daily_digest(selected_date, save_snapshot=save_snapshot_btn)

if save_snapshot_btn:
    st.success(f"✓ Daily snapshot compiled and recorded to SQLite (Report #{digest.get('report_id')}).")

# Briefing Metadata Banner
total_emails = digest["total_emails"]
pos_count = digest["positive_count"]
neu_count = digest["neutral_count"]
neg_count = digest["negative_count"]
unclass_count = digest.get("unclassified_count", 0)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Indexed for Date", total_emails)
k2.metric("Positive Sentiment", pos_count, delta="Confirmations / Credits", delta_color="normal")
k3.metric("Neutral Operations", neu_count, delta="Standard Invoices / POs", delta_color="off")
k4.metric("Negative Sentiment", neg_count, delta="Review Recommended" if neg_count > 0 else "All Clear", delta_color="inverse")
k5.metric("Pending Inference", unclass_count, delta="Queued" if unclass_count > 0 else "Complete", delta_color="off")

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# Section: Priority Review (Negative Sentiment Items)
st.markdown("""
<div style="font-size: 1.15rem; font-weight: 600; color: #172B3A; margin-bottom: 0.25rem;">
    Priority Register: Negative Sentiment Correspondence
</div>
<div style="font-size: 0.82rem; color: #74808B; margin-bottom: 0.75rem;">
    Linguistic signals indicative of overdue balances, billing disputes, or service holds requiring human audit:
</div>
""", unsafe_allow_html=True)

if digest["negative_emails"]:
    st.markdown("""
    <div style="padding: 0.65rem 0.85rem; background-color: #FDF0EF; border-left: 3px solid #D96C63; border-radius: 6px; font-size: 0.85rem; color: #9C3831; margin-bottom: 1rem;">
        <strong>Review Recommended:</strong> The following communications exhibit negative emotional or contractual polarity. Please verify whether operational or treasury action is necessary.
    </div>
    """, unsafe_allow_html=True)

    neg_rows = []
    for item in digest["negative_emails"]:
        neg_rows.append({
            "Subject": item["subject"],
            "Sender": item["sender"],
            "Negative Confidence": f"{item['negative_score']:.1%}",
            "Correspondence Excerpt": item["body_text"][:140] + "..."
        })
    df_neg = pd.DataFrame(neg_rows)
    st.dataframe(df_neg, use_container_width=True, hide_index=True)
else:
    st.markdown("""
    <div style="padding: 0.65rem 0.85rem; background-color: #E8F5F1; border-left: 3px solid #18866B; border-radius: 6px; font-size: 0.85rem; color: #18866B; margin-bottom: 1rem;">
        ✓ <strong>Status Normal:</strong> No adverse or contentious communications identified for this date.
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

# Section: Formatted Report & Export Desk
c_rep1, c_rep2 = st.columns([3, 2])

with c_rep1:
    st.markdown("""
    <div style="font-size: 1.15rem; font-weight: 600; color: #172B3A; margin-bottom: 0.5rem;">
        Formatted Intelligence Briefing Document
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="saas-card" style="font-size: 0.9rem; line-height: 1.65; color: #202B35; padding: 1.5rem; background-color: #FFFFFF; border-left: 3px solid #172B3A;">
{digest['report_markdown']}
    </div>
    """, unsafe_allow_html=True)

with c_rep2:
    st.markdown("""
    <div style="font-size: 1.15rem; font-weight: 600; color: #172B3A; margin-bottom: 0.5rem;">
        Dispatch & Export Actions
    </div>
    <div style="font-size: 0.82rem; color: #74808B; margin-bottom: 0.85rem;">
        Export report artifacts or transmit to executive stakeholders:
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="saas-card">', unsafe_allow_html=True)

    csv_data = export_digest_to_csv(digest["all_emails"])
    st.download_button(
        label="📥 Download Daily Digest Ledger (CSV)",
        data=csv_data,
        file_name=f"invoice_digest_{selected_date}.csv",
        mime="text/csv",
        use_container_width=True,
        key="btn_dl_csv"
    )

    st.markdown('<div style="height: 6px;"></div>', unsafe_allow_html=True)

    st.download_button(
        label="📑 Download Formatted Briefing (Markdown)",
        data=digest["report_markdown"],
        file_name=f"invoice_digest_{selected_date}.md",
        mime="text/markdown",
        use_container_width=True,
        key="btn_dl_md"
    )

    st.markdown('<div class="saas-divider"></div>', unsafe_allow_html=True)

    with st.expander("✉️ Dispatch via SMTP Relay", expanded=False):
        dest_email = st.text_input("Recipient Address", placeholder="finance-exec@company.com", key="dest_email")
        smtp_sender = st.text_input("Sender Mailbox", placeholder="invoicedigest-bot@company.com", key="smtp_sender")
        smtp_pass = st.text_input("SMTP App Token", type="password", key="smtp_pass")

        if st.button("🚀 Transmit Briefing via TLS", type="primary", use_container_width=True):
            if not dest_email or not smtp_sender or not smtp_pass:
                st.error("Please supply recipient address, sender address, and app password.")
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

    st.markdown('</div>', unsafe_allow_html=True)

render_disclaimer_callout()
