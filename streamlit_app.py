"""AI Infrastructure Economics Control Tower — local executive demonstration.

Real consulting lens, synthetic public datasets. No live accounts or tokens.
This app deliberately keeps 2023–24 baselines separate from 2025–26 operations.
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from finops_intelligence.metrics import build_summary, verify  # noqa: E402
from finops_intelligence.economics import (  # noqa: E402
    TokenAssumptions, calculate_token_plan, gpu_cost_share, priority_signals
)

DATA = ROOT / "data"
TEAL = "#6ADBD0"
BLUE = "#729BDD"
AMBER = "#E0B175"
MUTED = "#95ABC2"
GRID = "#253A4E"
PLOT_BG = "#102034"
WHITE = "#ECF6FC"

st.set_page_config(
    page_title="AI Infrastructure | Economics Control Tower",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');
html, body, [class*="css"], [data-testid="stApp"] {font-family: 'DM Sans',sans-serif;}
[data-testid="stAppViewContainer"] {background: #07121f;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stSidebar"] {background: #0a1929;border-right:1px solid #24384c;}
.block-container {padding-top: 1.5rem; max-width: 1540px;}
h1,h2,h3 {font-family: 'Manrope',sans-serif;letter-spacing:-.035em;}
div[data-testid="stMetric"] {background: #12243a;border:1px solid #294257;padding:18px 21px;border-radius:13px;}
div[data-testid="stMetricLabel"] {color:#9AB1C5;}
div[data-testid="stMetricValue"] {color:#F0F7FE;font-weight:800;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-color:#2c4256;}
.hero-kicker {font-size:12px;font-weight:800;letter-spacing:.18em;color:#69daca;margin-bottom:12px;}
.hero-title {font-family:'Manrope',sans-serif;font-weight:800;font-size:clamp(2.1rem,4.1vw,3.9rem);letter-spacing:-.065em;line-height:1.12;color:#f1f7ff;}
.hero-title span {color:#6ADBD0;}
.hero-sub {color:#afc0d0;font-size:15px;line-height:1.7;max-width:850px;margin:16px 0;}
.tag {display:inline-block;border:1px solid #397a79;color:#a0efe3;border-radius:40px;padding:7px 12px;font-size:11px;letter-spacing:.08em;font-weight:700;}
.section-note {color:#96acbf;font-size:12px;line-height:1.6;}
.caption-card {background:#102635;border:1px solid #2e6467;border-radius:12px;padding:15px 18px;color:#c5e6e4;font-size:13px;line-height:1.6;}
.caption-card b {color:#edfffb;}
.warn-card {border:1px solid #5b5148;background:#221e21;border-radius:12px;padding:14px 16px;margin:12px 0;}
.warn-card strong {font-size:13px;color:#f1d1a4;}
.warn-card p {font-size:12px;color:#c5bdba;margin:6px 0;}
.warn-card small {font-size:11px;color:#a5c5cf;}
.stTabs [data-baseweb="tab-list"] {gap:7px;}
.stTabs [data-baseweb="tab"] {background:#0e2234;border:1px solid #294154;border-radius:9px;color:#b5c7d4;}
.stTabs [aria-selected="true"] {background:#1b4350!important;color:#d6fff5!important;}
[data-testid="stSidebar"] .stSlider {margin-bottom:7px;}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_evidence() -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    summary = build_summary(DATA)
    verify(summary)
    billing = pd.read_csv(DATA / "finops_billing_daily.csv")
    billing["date"] = pd.to_datetime(billing["date"], format="%m/%d/%Y", errors="raise")
    billing["cost_unblended_usd"] = pd.to_numeric(
        billing["cost_unblended_usd"], errors="raise"
    )
    budget = pd.read_csv(DATA / "finops_budget_tracking.csv")
    budget["Date"] = pd.to_datetime(budget["Date"], format="%m/%d/%Y", errors="raise")
    for field in ("Monthly Budget", "Actual Cost"):
        budget[field] = pd.to_numeric(budget[field], errors="raise")
    return summary, billing, budget


def money(number: object, decimals: int = 0) -> str:
    return f"\${Decimal(str(number)):,.{decimals}f}"


def scaled_money(number: object) -> str:
    value = Decimal(str(number))
    if abs(value) >= Decimal("1000000"):
        return f"\${value / Decimal('1000000'):,.2f}M"
    if abs(value) >= Decimal("1000"):
        return f"\${value / Decimal('1000'):,.1f}K"
    return money(value, 2)


def chart_style(fig: go.Figure, *, height: int = 310) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color="#C4D7E5", family="DM Sans"),
        margin=dict(l=18, r=14, t=24, b=20),
        showlegend=True,
        legend=dict(orientation="h", y=-0.23),
        hoverlabel=dict(bgcolor="#142A40", font_color="#EFF7FF"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, griddash="dot", zeroline=False, linecolor=GRID)
    return fig


def simple_bars(entries: dict[str, Decimal], *, title: str, color: str) -> None:
    items = list(entries.items())[:10]
    names = [key for key, _ in items][::-1]
    amounts = [float(value) for _, value in items][::-1]
    fig = go.Figure(go.Bar(
        x=amounts, y=names, orientation="h",
        marker_color=color,
        hovertemplate="%{y}<br>$%{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(title=title, showlegend=False)
    fig.update_xaxes(tickprefix="$", tickformat="~s")
    st.plotly_chart(chart_style(fig, height=335), use_container_width=True, config={"displayModeBar": False})


try:
    summary, billing, budget = load_evidence()
except (ValueError, KeyError, AssertionError, OSError) as exc:
    st.error("The synthetic evidence did not pass validation; dashboard withheld.")
    st.exception(exc)
    st.stop()

baseline = summary["executive_baseline"]
ops = summary["operational_extension"]
gpu_share = gpu_cost_share(ops["gpu_spend"], ops["operational_spend"])

with st.sidebar:
    st.markdown("### ◈ AI INFRA / ECONOMICS")
    st.caption("EXECUTIVE DECISION CONTROL TOWER")
    st.divider()
    st.markdown("**Planning assumptions**")
    st.caption("These are illustrative values, not observed billing data or quoted vendor prices.")
    input_tokens = st.slider("Assumed input tokens / inference", 250, 5000, 1800, 250)
    output_tokens = st.slider("Assumed output tokens / inference", 50, 2000, 400, 50)
    efficient_share = st.slider("Lower-cost model routing (%)", 0, 100, 50, 5)
    retry = st.slider("Assumed retry overhead (%)", 0, 100, 10, 5)
    growth = st.slider("Scenario volume growth (%)", 0, 300, 0, 25)
    with st.expander("Editable hypothetical rates / 1M tokens", expanded=False):
        p_input = st.number_input("Tier A input ($)", 0.0, 100.0, 5.0, 0.25)
        p_output = st.number_input("Tier A output ($)", 0.0, 200.0, 15.0, 0.25)
        e_input = st.number_input("Tier B input ($)", 0.0, 100.0, 0.25, 0.05)
        e_output = st.number_input("Tier B output ($)", 0.0, 200.0, 1.25, 0.25)
    limit = st.number_input("90-day token-cost planning limit ($)", 1.0, 1000000.0, 2500.0, 100.0)
    st.divider()
    st.caption("SOURCE WINDOWS ARE SEPARATE")
    st.caption("Budget: Jan 2023–Dec 2024")
    st.caption("Operations: Nov 3, 2025–Jan 31, 2026")
    st.caption("Local-only · synthetic datasets · no write actions")

assumptions = TokenAssumptions(
    inferences=ops["model_inferences"],
    input_tokens_per_inference=input_tokens,
    output_tokens_per_inference=output_tokens,
    premium_input_per_million=Decimal(str(p_input)),
    premium_output_per_million=Decimal(str(p_output)),
    efficient_input_per_million=Decimal(str(e_input)),
    efficient_output_per_million=Decimal(str(e_output)),
    efficient_share_pct=efficient_share,
    retry_overhead_pct=retry,
    volume_growth_pct=growth,
)
token_plan = calculate_token_plan(assumptions)
signals = priority_signals(
    gpu_share_pct=gpu_share,
    modeled_token_cost=token_plan["total_cost"],
    planning_limit=Decimal(str(limit)),
    retry_overhead_pct=retry,
)

st.markdown(
    '<div class="hero-kicker">FINOPS / AI INFRASTRUCTURE / EXECUTIVE INTELLIGENCE</div>'
    '<div class="hero-title">Economics <span>Control Tower.</span></div>'
    '<div class="hero-sub">From cloud spend to inference economics. Separate what the dataset '
    'proves from what the model assumes—and make the next business decision explicit.</div>'
    '<span class="tag">REPRODUCIBLE SYNTHETIC EVIDENCE · HUMAN DECISION RIGHTS</span>',
    unsafe_allow_html=True,
)
st.write("")

overview, economics, cloud, assurance = st.tabs([
    "01 / Command Center", "02 / Token Economics",
    "03 / Cloud Optimization", "04 / Decision Controls",
])

with overview:
    st.subheader("90-day AI infrastructure operations")
    st.caption("Synthetic operational window: Nov 3, 2025–Jan 31, 2026. These figures are not part of the 2023–24 budget baseline.")
    a, b, c, d = st.columns(4)
    a.metric("Operational cloud spend", scaled_money(ops["operational_spend"]))
    b.metric("GPU-tagged spend", scaled_money(ops["gpu_spend"]))
    c.metric("Model inferences", f"{ops['model_inferences']:,}")
    d.metric("Application requests", f"{ops['requests']:,}")
    a, b = st.columns([1.5, 1])
    with a:
        with st.container(border=True):
            st.markdown("**Operational spend / day**")
            daily = billing.groupby("date", as_index=False)["cost_unblended_usd"].sum().sort_values("date")
            fig = go.Figure(go.Scatter(
                x=daily["date"], y=daily["cost_unblended_usd"],
                mode="lines", line=dict(color=TEAL, width=3),
                fill="tozeroy", fillcolor="rgba(106,219,208,0.13)",
                hovertemplate="%{x|%b %d, %Y}<br>$%{y:,.2f}<extra></extra>",
            ))
            fig.update_yaxes(tickprefix="$")
            st.plotly_chart(chart_style(fig, height=320), use_container_width=True, config={"displayModeBar": False})
    with b:
        with st.container(border=True):
            st.markdown("**GPU cost concentration**")
            other = ops["operational_spend"] - ops["gpu_spend"]
            fig = go.Figure(go.Pie(
                labels=["GPU-tagged", "Other operational cloud"],
                values=[float(ops["gpu_spend"]), float(other)],
                hole=0.68, marker=dict(colors=[TEAL, BLUE]),
                textinfo="percent",
            ))
            fig.update_layout(showlegend=True)
            st.plotly_chart(chart_style(fig, height=320), use_container_width=True, config={"displayModeBar": False})
    st.markdown(
        f'<div class="caption-card"><b>Financial discipline:</b> {gpu_share:.1f}% of the '
        'synthetic 90-day cloud spend is GPU-tagged. A concentration signal is not proof of '
        'waste or poor utilization. Inspect job scheduling and GPU utilization before '
        'making an optimization claim.</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown("#### Executive signals")
    for signal in signals[:4]:
        st.markdown(
            f'<div class="warn-card"><strong>{signal["severity"]}: {signal["name"]}</strong>'
            f'<p>{signal["detail"]}</p><small>Next action: {signal["next_step"]}</small></div>',
            unsafe_allow_html=True,
        )

with economics:
    st.subheader("Token economics — explicit planning scenario")
    st.warning(
        "No observed token counts, model-level pricing, retries, or token invoices exist in "
        "the committed dataset. This is a standalone, hypothetical 90-day cost model using "
        "the synthetic inference count as its volume anchor. DO NOT add this amount to "
        "historical cloud spend: that could double count costs."
    )
    a, b, c, d = st.columns(4)
    a.metric("Hypothetical token charges", money(token_plan["total_cost"], 2))
    b.metric("Modeled input tokens", f"{int(token_plan['assumed_input_tokens']):,}")
    c.metric("Modeled output tokens", f"{int(token_plan['assumed_output_tokens']):,}")
    d.metric("Scenario $ / 1K inferences", money(token_plan["cost_per_thousand_primary_inferences"], 2))
    a, b = st.columns([1.15, 1])
    with a:
        with st.container(border=True):
            st.markdown("**What drives modeled token cost?**")
            fig = go.Figure()
            for name, key, color in [
                ("Input token cost", "input_cost", BLUE),
                ("Output token cost", "output_cost", TEAL),
                ("Retry overhead", "retry_cost", AMBER),
            ]:
                fig.add_trace(go.Bar(
                    x=["90-day what-if"], y=[float(token_plan[key])],
                    name=name, marker_color=color,
                    hovertemplate="%{fullData.name}: $%{y:,.2f}<extra></extra>",
                ))
            fig.update_layout(barmode="stack")
            fig.update_yaxes(tickprefix="$")
            st.plotly_chart(chart_style(fig, height=330), use_container_width=True, config={"displayModeBar": False})
    with b:
        with st.container(border=True):
            st.markdown("**Model routing sensitivity**")
            shares = list(range(0, 101, 10))
            costs = []
            for share in shares:
                case = TokenAssumptions(**{**assumptions.__dict__, "efficient_share_pct": share})
                costs.append(float(calculate_token_plan(case)["total_cost"]))
            fig = go.Figure(go.Scatter(
                x=shares, y=costs,
                mode="lines+markers", line=dict(color=TEAL, width=3),
                marker=dict(color=TEAL, size=7),
                hovertemplate="Lower-cost tier: %{x}%<br>Modeled spend: $%{y:,.2f}<extra></extra>",
            ))
            fig.update_xaxes(title="Assumed share routed to Tier B")
            fig.update_yaxes(title="Hypothetical 90-day token cost", tickprefix="$")
            st.plotly_chart(chart_style(fig, height=330), use_container_width=True, config={"displayModeBar": False})
    st.markdown(
        '<div class="caption-card"><b>Architecture decision:</b> Use cheaper models only '
        'when evals demonstrate adequate quality, latency and safety. Routing percentages '
        'alone do not establish business value. Rates are editable illustrative assumptions '
        'and are not current vendor prices.</div>',
        unsafe_allow_html=True,
    )
    with st.expander("Calculation and lineage"):
        st.code(
            "scenario_inferences = synthetic_inferences * (1 + volume_growth_pct / 100)\n"
            "input_tokens = scenario_inferences * assumed_input_tokens_per_inference\n"
            "output_tokens = scenario_inferences * assumed_output_tokens_per_inference\n"
            "blended_price = tier_A_rate * (1 - tier_B_share) + tier_B_rate * tier_B_share\n"
            "primary_cost = input_tokens / 1e6 * input_rate + output_tokens / 1e6 * output_rate\n"
            "scenario_cost = primary_cost * (1 + retry_overhead_pct / 100)\n"
            "No observed token spend or offset against measured cloud billing is asserted.",
            language="text",
        )

with cloud:
    st.subheader("2023–2024 financial baseline")
    st.caption("Separate synthetic baseline covering Jan 2023–Dec 2024; NOT combined with 2025–26 operational measurements.")
    a, b, c, d = st.columns(4)
    a.metric("Modeled budget", scaled_money(baseline["budget_total"]))
    b.metric("Modeled actual spend", scaled_money(baseline["actual_from_cloud_costs"]))
    c.metric("Budget / actual variance", scaled_money(baseline["budget_variance"]))
    d.metric("Optimization opportunity", scaled_money(baseline["potential_savings"]))
    st.info(
        "The budget-to-actual gap is not booked savings. Additional potential "
        "optimization is a modeled candidate backlog—not automatically realized savings."
    )
    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            simple_bars(baseline["cost_by_provider"], title="Historical spend by provider", color=BLUE)
    with b:
        with st.container(border=True):
            simple_bars(baseline["opportunity_by_status"], title="Optimization candidate classification", color=TEAL)
    with st.container(border=True):
        st.markdown("**Budget vs synthetic actual / month**")
        timeline = budget.groupby("Date", as_index=False)[["Monthly Budget", "Actual Cost"]].sum().sort_values("Date")
        fig = go.Figure()
        for name, col, color in [
            ("Budget", "Monthly Budget", AMBER),
            ("Actual", "Actual Cost", TEAL),
        ]:
            fig.add_trace(go.Scatter(
                x=timeline["Date"], y=timeline[col], name=name,
                mode="lines", line=dict(color=color, width=3),
            ))
        fig.update_yaxes(tickprefix="$")
        st.plotly_chart(chart_style(fig, height=325), use_container_width=True, config={"displayModeBar": False})
    st.markdown(
        '<div class="caption-card"><b>Recommendation:</b> Validate reservations and '
        'right-sizing candidates against commitments, utilization, business criticality '
        'and migration costs. Only verified realized outcomes belong in booked savings.</div>',
        unsafe_allow_html=True,
    )

with assurance:
    st.subheader("Evidence, limitations & accountable decisions")
    c1, c2, c3 = st.columns(3)
    c1.metric("Budget / department-month rows", baseline["budget_rows"])
    c2.metric("Daily billing resource rows", f"{ops['billing_rows']:,}")
    c3.metric("Usage KPI rows", ops["usage_rows"])
    st.markdown("### Executive review queue")
    for signal in signals:
        with st.container(border=True):
            st.markdown(f"**{signal['severity']} · {signal['name']}**")
            st.write(signal["detail"])
            st.caption(f"Recommended human follow-up: {signal['next_step']}")
    st.markdown("### Evidence classes")
    st.table(pd.DataFrame([
        {"Class": "Synthetic source evidence", "Meaning": "Committed cloud cost, billing and inference-count CSVs"},
        {"Class": "Derived and reconciled", "Meaning": "Budget variance, GPU spend share, optimization sums"},
        {"Class": "What-if assumptions", "Meaning": "Tokens/inference, rates, retry %, growth and route mix"},
        {"Class": "Human decision", "Meaning": "Savings recognition, product changes, budget and security sign-off"},
    ]))
    st.markdown(
        '<div class="caption-card"><b>Boundaries:</b> Local read-only prototype; synthetic '
        'data only; no live AWS or GCP access, no client billing information, no measured '
        'token or model-specific costs, no automated remediation or purchasing decisions. '
        'Historical baseline and 90-day operations remain analytically separate.</div>',
        unsafe_allow_html=True,
    )

st.divider()
st.caption("AI INFRASTRUCTURE ECONOMICS CONTROL TOWER · Synthetic portfolio reference implementation · Evidence before action.")
