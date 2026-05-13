import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

API = "https://ai-powered-customer-support-u3rt.onrender.com"

st.set_page_config(
    page_title="SupportIQ",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
    .metric-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        border: 1px solid #e9ecef;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 6px; }
</style>
""", unsafe_allow_html=True)


def fetch(endpoint: str):
    try:
        r = requests.get(f"{API}{endpoint}", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Could not reach API: {e}. Make sure the backend is running.")
        return None


# ── Header ──────────────────────────────────────────────────────────────────
st.title("🎯 SupportIQ")
st.caption("Customer support insight platform")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Tickets", "Agent Assist", "Upload"])


# ── TAB 1: OVERVIEW ─────────────────────────────────────────────────────────
with tab1:
    data = fetch("/api/insights/summary")

    if data:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Tickets", f"{data['total_tickets']:,}")
        col2.metric("Avg Frustration", f"{data['avg_frustration']} / 10")
        col3.metric("High Priority", f"{data['high_priority_count']:,}")
        col4.metric("Revenue at Risk", f"${data['total_revenue_risk']:,.0f}")

        st.divider()

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Top issue categories")
            if data.get("categories"):
                df = pd.DataFrame(data["categories"])
                fig = px.bar(
                    df, x="count", y="category", orientation="h",
                    color="count", color_continuous_scale="Blues",
                    labels={"count": "Tickets", "category": ""},
                    height=320
                )
                fig.update_layout(
                    showlegend=False,
                    coloraxis_showscale=False,
                    margin=dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor="white",
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_right:
            st.subheader("Sentiment breakdown")
            if data.get("sentiment_distribution"):
                df_s = pd.DataFrame(data["sentiment_distribution"])
                colors = {
                    "frustrated": "#e74c3c",
                    "dissatisfied": "#f39c12",
                    "neutral": "#95a5a6",
                    "satisfied": "#27ae60"
                }
                fig2 = px.pie(
                    df_s, values="count", names="sentiment",
                    color="sentiment",
                    color_discrete_map=colors,
                    height=320
                )
                fig2.update_traces(textposition="inside", textinfo="percent+label")
                fig2.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Anomaly detection")
        anomalies = fetch("/api/insights/anomalies")
        if anomalies and anomalies.get("anomalies"):
            for a in anomalies["anomalies"]:
                spike = a.get("spike_pct", 0)
                st.warning(
                    f"**{a['category'].replace('_', ' ').title()}** spiked **{spike}%** above average "
                    f"(avg: {round(a['avg_count'])} tickets/week, peak: {a['max_count']})"
                )
        else:
            st.info("No unusual spikes detected in the current dataset.")

        st.subheader("Channel breakdown")
        channels = fetch("/api/insights/channels")
        if channels and channels.get("channels"):
            df_ch = pd.DataFrame(channels["channels"])
            fig3 = px.bar(
                df_ch, x="channel", y="count",
                color="avg_frustration",
                color_continuous_scale="RdYlGn_r",
                labels={"count": "Tickets", "channel": "Channel", "avg_frustration": "Avg Frustration"},
                height=280
            )
            fig3.update_layout(margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor="white")
            st.plotly_chart(fig3, use_container_width=True)


# ── TAB 2: TICKETS ──────────────────────────────────────────────────────────
with tab2:
    st.subheader("Browse tickets")

    col_a, col_b, col_c = st.columns(3)
    category_filter = col_a.selectbox("Category", ["All", "delivery_delay", "wrong_item", "payment_failed", "refund_not_received", "account_login", "product_quality", "cancellation"])
    sentiment_filter = col_b.selectbox("Sentiment", ["All", "frustrated", "dissatisfied", "neutral", "satisfied"])
    limit = col_c.select_slider("Show", options=[10, 20, 50, 100], value=20)

    params = f"?limit={limit}"
    if category_filter != "All":
        params += f"&category={category_filter}"
    if sentiment_filter != "All":
        params += f"&sentiment={sentiment_filter}"

    tickets_data = fetch(f"/api/tickets{params}")

    if tickets_data and tickets_data.get("tickets"):
        tickets = tickets_data["tickets"]
        st.caption(f"Showing {len(tickets)} of {tickets_data['total']:,} tickets")

        for t in tickets:
            sentiment_color = {
                "frustrated": "🔴",
                "dissatisfied": "🟠",
                "neutral": "🟡",
                "satisfied": "🟢"
            }.get(t.get("sentiment", "neutral"), "⚪")

            priority_badge = {"high": "🚨", "medium": "⚠️", "low": "✅"}.get(t.get("priority", "low"), "")

            with st.expander(
                f"{priority_badge} {t.get('ticket_id', 'N/A')} — {t.get('category', '').replace('_', ' ').title()} {sentiment_color}  |  ${t.get('order_value', 0):.0f}  |  {t.get('channel', '')}",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Customer message**")
                    st.write(t.get("message", ""))
                    st.caption(f"Product: {t.get('product', 'N/A')}  ·  Country: {t.get('customer_country', 'N/A')}  ·  Status: {t.get('resolution_status', 'N/A')}")
                with col2:
                    st.markdown("**AI suggested response**")
                    suggested = t.get("suggested_response") or t.get("agent_reply", "No response generated.")
                    st.info(suggested)
    else:
        st.info("No tickets found. Upload a CSV in the Upload tab first.")


# ── TAB 3: AGENT ASSIST ─────────────────────────────────────────────────────
with tab3:
    st.subheader("Agent assist")
    st.write("Ask a question about your support data or get a weekly report.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Ask a question**")
        question = st.text_area(
            "What do you want to know?",
            placeholder="e.g. What is the most common issue this week?",
            height=100,
            label_visibility="collapsed"
        )
        if st.button("Ask", use_container_width=True):
            if question:
                try:
                    r = requests.post(f"{API}/api/agent/ask", json={"question": question}, timeout=10)
                    result = r.json()
                    st.markdown("**Answer**")
                    st.write(result.get("answer", "No response."))
                    if result.get("note"):
                        st.caption(result["note"])
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter a question first.")

    with col2:
        st.markdown("**Weekly report**")
        if st.button("Generate report", use_container_width=True):
            report = fetch("/api/agent/weekly-report")
            if report:
                col_a, col_b = st.columns(2)
                col_a.metric("Tickets this week", report.get("total_tickets", 0))
                col_b.metric("Frustrated %", f"{report.get('frustrated_pct', 0)}%")
                st.markdown("---")
                st.write(report.get("report", "No summary available."))


# ── TAB 4: UPLOAD ───────────────────────────────────────────────────────────
with tab4:
    st.subheader("Upload tickets")
    st.write("Upload a CSV file to process tickets through the AI pipeline.")

    st.markdown("""
    **Expected columns:**
    `ticket_id`, `timestamp`, `customer_id`, `channel`, `message`, `agent_reply`, `product`, `order_value`, `customer_country`, `resolution_status`
    """)

    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded:
        st.info(f"File selected: **{uploaded.name}** ({uploaded.size:,} bytes)")
        if st.button("Process and upload", use_container_width=True):
            with st.spinner("Processing tickets through AI pipeline..."):
                try:
                    r = requests.post(
                        f"{API}/api/tickets/upload",
                        files={"file": (uploaded.name, uploaded.getvalue(), "text/csv")},
                        timeout=120
                    )
                    result = r.json()
                    st.success(result.get("message", "Upload complete"))
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    st.divider()
    st.markdown("**Or generate a synthetic dataset to get started:**")
    col1, col2 = st.columns(2)
    rows = col1.number_input("Number of tickets", min_value=100, max_value=50000, value=1000, step=100)

    if col2.button("Generate dataset", use_container_width=True):
        with st.spinner("Generating..."):
            try:
                from generate_dataset import generate
                import os
                out_path = str(Path(__file__).parent.parent / "data" / "tickets.csv")
                generate(rows=int(rows), output=out_path)
                st.success(f"Generated {rows:,} tickets at data/tickets.csv")

                with open(out_path, "rb") as f:
                    st.download_button(
                        "Download CSV",
                        f,
                        file_name="tickets.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error: {e}")
