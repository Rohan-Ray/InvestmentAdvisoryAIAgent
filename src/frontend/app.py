"""
Investment Advisory AI Agent — Streamlit Frontend
Educational demo for banking customers. Not real financial advice.
"""

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import streamlit as st
import plotly.graph_objects as go

from src.backend.advisor import UserProfile, get_recommendation

@st.cache_resource
def _start_metrics_server():
    """Start the Prometheus HTTP server once inside the Streamlit process."""
    from prometheus_client import start_http_server
    try:
        start_http_server(8502)
        return True
    except OSError:
        return True  # already running on hot-reload

_start_metrics_server()

# ── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Investment Advisory AI Agent",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS for a clean banking look ──────────────────────────────────────
st.markdown(
    """
    <style>
    .main { background-color: #f5f7fa; }
    .stButton > button {
        background-color: #1a3c6e;
        color: white;
        border-radius: 8px;
        padding: 0.5em 2em;
        font-size: 1rem;
        border: none;
    }
    .stButton > button:hover { background-color: #2a5298; }
    .disclaimer-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        font-size: 0.85rem;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_header():
    """Render the app title and top-level disclaimer."""
    st.title("💰 Investment Advisory AI Agent")
    st.markdown(
        "**Powered by rule-based logic — for banking customers learning about investment options.**"
    )
    st.markdown(
        '<div class="disclaimer-box">⚠️ <strong>DISCLAIMER:</strong> This is an educational demo only. '
        'It does not constitute real financial advice. Always consult a SEBI-registered advisor.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")


def render_input_form() -> UserProfile | None:
    """
    Render the user input form.
    Returns a UserProfile when the user submits, else None.
    """
    st.subheader("📋 Tell us about yourself")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "Your Age",
            min_value=18,
            max_value=80,
            value=30,
            step=1,
            help="Used to adjust equity exposure near retirement.",
        )
        monthly_income = st.number_input(
            "Monthly Income (₹)",
            min_value=5000,
            max_value=10_000_000,
            value=50000,
            step=1000,
            format="%d",
            help="Your gross or net monthly earnings.",
        )

    with col2:
        monthly_savings = st.number_input(
            "Monthly Savings (₹)",
            min_value=0,
            max_value=10_000_000,
            value=10000,
            step=500,
            format="%d",
            help="Amount you can invest each month.",
        )

    st.markdown("### 🎯 Your Preferences")

    col3, col4 = st.columns(2)
    with col3:
        risk = st.radio(
            "Risk Appetite",
            options=["Low", "Medium", "High"],
            index=1,
            help="How comfortable are you with potential losses for higher returns?",
        )

    with col4:
        goal = st.radio(
            "Investment Goal Horizon",
            options=["Short-term", "Medium-term", "Long-term"],
            index=1,
            help="Short-term: < 3 yrs | Medium-term: 3–7 yrs | Long-term: 7+ yrs",
        )

    # Validation
    if monthly_savings > monthly_income:
        st.warning("Your savings cannot exceed your income. Please adjust.")

    submitted = st.button("🔍 Get My Investment Plan", use_container_width=True)

    if submitted:
        if monthly_savings > monthly_income:
            st.error("Please fix the savings/income mismatch before proceeding.")
            return None
        return UserProfile(
            age=int(age),
            monthly_income=float(monthly_income),
            monthly_savings=float(monthly_savings),
            risk_preference=risk,
            investment_goal=goal,
        )
    return None


def render_pie_chart(allocations: dict[str, float]):
    """Render an interactive Plotly pie chart of allocation percentages."""
    # Colour palette inspired by Indian banking brands
    colours = ["#1a3c6e", "#2a5298", "#4a7ac5", "#6fa0e0", "#a8c8f0"]

    labels = list(allocations.keys())
    values = list(allocations.values())

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colours[: len(labels)], line=dict(color="white", width=2)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Allocation: %{value:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title_text="Recommended Portfolio Allocation",
        title_x=0.5,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(t=60, b=60, l=20, r=20),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_allocation_table(allocations: dict[str, float], monthly_savings: float):
    """Show a breakdown table with rupee amounts per category."""
    st.markdown("### 📊 Monthly Savings Breakdown")

    rows = []
    for category, pct in sorted(allocations.items(), key=lambda x: -x[1]):
        rupees = monthly_savings * pct / 100
        rows.append(
            f"| {category} | {pct:.1f}% | ₹{rupees:,.0f} |"
        )

    table_md = (
        "| Investment Category | Allocation | Monthly Amount |\n"
        "|---------------------|-----------|----------------|\n"
        + "\n".join(rows)
    )
    st.markdown(table_md)


def render_recommendation(profile: UserProfile):
    """Run the advisor engine and display results."""
    with st.spinner("Analysing your profile…"):
        rec = get_recommendation(profile)

    st.success("✅ Your personalised investment plan is ready!")
    st.markdown(f"**Risk Profile:** `{rec.risk_label}` | **Horizon:** `{rec.horizon_label}`")

    # Pie chart
    render_pie_chart(rec.allocations)

    # Allocation table
    render_allocation_table(rec.allocations, profile.monthly_savings)

    # Plan narrative — Sonnet-generated when API key is set, static fallback otherwise
    if rec.ai_powered:
        st.markdown("### 💡 Your Personalised Investment Plan")
        st.caption("✨ Generated by Claude Sonnet 4.6 based on your profile")
    else:
        st.markdown("### 💡 What This Means For You")
        st.caption("ℹ️ Set ANTHROPIC_API_KEY to get a personalised AI-generated plan")
    st.markdown(rec.explanation)

    # Category descriptions
    with st.expander("📚 Learn about each investment category"):
        st.markdown(
            """
| Category | What it is | Best for |
|---|---|---|
| **Fixed Deposit** | Lock money for a fixed period at a guaranteed interest rate | Capital safety, predictable income |
| **Recurring Deposit** | Save a fixed amount every month; bank pays interest | Building savings discipline |
| **Bonds** | Lend money to government/companies and earn coupon interest | Steady income, lower risk than equity |
| **Mutual Funds** | Pool money with others; professional managers invest it | Diversified growth, moderate risk |
| **Equity** | Buy shares of companies directly | High long-term growth; high short-term volatility |
"""
        )

    st.markdown("---")
    st.markdown(
        '<div class="disclaimer-box">⚠️ <strong>DISCLAIMER:</strong> This is an educational demo only. '
        "The recommendations above are generated by a simple rule-based algorithm and do not account "
        "for your complete financial picture, tax situation, or regulatory requirements. "
        "Please consult a SEBI-registered investment advisor before making real investment decisions.</div>",
        unsafe_allow_html=True,
    )


def main():
    render_header()
    # Track page loads as active sessions
    try:
        from observability.metrics_exporter import active_sessions
        active_sessions.inc()
    except Exception:
        pass
    profile = render_input_form()
    if profile is not None:
        render_recommendation(profile)


if __name__ == "__main__":
    main()
