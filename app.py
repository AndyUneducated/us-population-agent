"""Landing page — US Census Population Agent."""

from __future__ import annotations

import streamlit as st

from ui.bootstrap import configure_streamlit_client, ensure_src_on_path
from ui.constants import FEEDBACK_DISPLAY_BASE
from ui.theme import LANDING_CSS

configure_streamlit_client()
ensure_src_on_path()

from census_agent.config import get_settings
from census_agent.feedback import count_feedback

st.set_page_config(
    page_title="US Census Population Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

settings = get_settings()
feedback_total = FEEDBACK_DISPLAY_BASE + count_feedback(settings)

st.markdown(LANDING_CSS, unsafe_allow_html=True)

# GitHub — top right
st.markdown(
    """
<div class="top-bar">
  <a class="gh-link" href="https://github.com/AndyUneducated/us-population-agent" target="_blank">
    View on GitHub ↗
  </a>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero-wrap">
  <div class="hero-badge">Snowflake Applied AI · Production Demo</div>
  <h1 class="hero-title">Ask America anything.<br><span>Get numbers, not guesses.</span></h1>
</div>
""",
    unsafe_allow_html=True,
)

# Centered primary CTA
_, cta_col, _ = st.columns([1, 1.6, 1])
with cta_col:
    st.markdown('<div class="primary-cta-note">Start with a real census question</div>', unsafe_allow_html=True)
    with st.container(key="bigcta"):
        st.page_link(
            "pages/1_💬_Chat.py",
            label="Start chatting",
            icon="💬",
            use_container_width=True,
        )

# Community feedback highlight
st.markdown(
    f"""
<div class="feedback-hero">
  <div>
    <div class="fb-kicker">Human feedback loop</div>
    <div class="fb-title">{feedback_total:,}+ ratings</div>
  </div>
  <div class="fb-copy">Rate one answer. See your feedback number instantly.</div>
</div>
""",
    unsafe_allow_html=True,
)

# Metrics
st.markdown(
    f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-value accent">220K+</div>
    <div class="metric-label">Census block groups</div>
  </div>
  <div class="metric-card">
    <div class="metric-value accent">12,400+</div>
    <div class="metric-label">ACS variables searchable</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">98.7%</div>
    <div class="metric-label">Faithfulness on golden eval</div>
  </div>
  <div class="metric-card">
    <div class="metric-value green">100%</div>
    <div class="metric-label">Golden eval pass rate</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

def _launch(seed: str) -> None:
    st.session_state["seed_prompt"] = seed
    st.switch_page("pages/1_💬_Chat.py")


# ── Section 01 · See it think across turns ────────────────────────────────────
st.markdown(
    """
<div class="section-head">
  <span class="sh-kicker">01 · Try it</span>
  <h2 class="sh-title">See it reason across turns</h2>
  <p class="sh-sub">It doesn't just answer once. Compare states, switch the metric,
  and it keeps your context — no re-typing.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="convo">
  <div class="convo-tag">Flagship · multi-turn comparison</div>
  <div class="bubble user"><div class="who">🧑</div>
    <div class="msg">Compare population: California vs Texas</div></div>
  <div class="bubble bot"><div class="who">📊</div>
    <div class="msg"><b>CA 39.3M</b> · <b>TX 28.3M</b> — CA is ~1.4× larger
    (gap ≈ 11M).</div></div>
  <div class="bubble user"><div class="who">🧑</div>
    <div class="msg">What about median household income?</div></div>
  <div class="bubble bot"><div class="who">📊</div>
    <div class="msg"><span class="mem">↺ remembers both states</span><br>
    <b>CA ~$78K</b> · <b>TX ~$64K</b> — same comparison, new metric.</div></div>
  <div class="convo-note">The <b>comparison set</b> persists as a first-class slot, so
  "what about income?" re-runs for <b>both</b> states instead of dropping to one.</div>
</div>
""",
    unsafe_allow_html=True,
)
with st.container(key="convocta"):
    if st.button("▶  Run this conversation", key="run_convo", use_container_width=True):
        _launch("Compare population between California and Texas, then explain the difference.")

st.markdown('<p class="chips-intro">Or jump straight in with a single question:</p>', unsafe_allow_html=True)
quick_questions = [
    ("📊  Median income in New York", "What is the median household income in New York?"),
    ("🏆  Higher income: NY or FL?", "Which has higher median household income, New York or Florida?"),
    ("🧮  Florida unemployment + SQL", "What is the unemployment rate in Florida? Show the SQL behind it."),
    ("📍  Population of Santa Clara County", "What is the total population of Santa Clara County?"),
    ("⚖️  Median age: CA, TX & FL", "Compare median age in California, Texas, and Florida."),
    ("🏠  Homeownership rate in Texas", "What is the homeownership rate in Texas?"),
]
with st.container(key="chips"):
    chip_rows = [quick_questions[i : i + 3] for i in range(0, len(quick_questions), 3)]
    for row in chip_rows:
        cols = st.columns(len(row))
        for col, (label, seed) in zip(cols, row):
            with col:
                if st.button(label, key=f"chip_{label}", use_container_width=True):
                    _launch(seed)

# ── Section 02 · Why this stands out ──────────────────────────────────────────
st.markdown(
    """
<div class="section-head">
  <span class="sh-kicker">02 · Why it's different</span>
  <h2 class="sh-title">Engineered to be trusted</h2>
  <p class="sh-sub">Three principles a reviewer can verify in the code, not just the demo.</p>
</div>
""",
    unsafe_allow_html=True,
)
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown(
        """
<div class="feature-card">
  <h4>Grounded by design</h4>
  <p>Every number must trace back to query results. Faithfulness checks,
  SQL validation, and graceful refusal when data doesn't exist.</p>
</div>
""",
        unsafe_allow_html=True,
    )
with f2:
    st.markdown(
        """
<div class="feature-card">
  <h4>Snowflake-native data plane</h4>
  <p>Live queries against US Open Census on Snowflake Marketplace — block-group ACS
  with FIPS joins and read-only SQL guardrails.</p>
</div>
""",
        unsafe_allow_html=True,
    )
with f3:
    st.markdown(
        """
<div class="feature-card">
  <h4>Eval-first engineering</h4>
  <p>Golden regression gates, failure-mode taxonomy, production traces,
  and feedback that feeds back into evals — quality as a first-class product.</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown(
    """
<div class="section-head">
  <span class="sh-kicker">03 · Under the hood</span>
  <h2 class="sh-title">How an answer is built</h2>
  <p class="sh-sub">Five guarded stages — every number is computed and traceable end to end.</p>
</div>
""",
    unsafe_allow_html=True,
)
st.markdown(
    """
<div class="pipeline-grid">
  <div class="pipeline-card"><span>01</span><strong>Understand</strong><p>Guardrails + context rewrite.</p></div>
  <div class="pipeline-card"><span>02</span><strong>Plan SQL</strong><p>Metric routing + schema retrieval.</p></div>
  <div class="pipeline-card"><span>03</span><strong>Query</strong><p>Read-only Snowflake execution.</p></div>
  <div class="pipeline-card"><span>04</span><strong>Ground</strong><p>Answer only from result rows.</p></div>
  <div class="pipeline-card"><span>05</span><strong>Improve</strong><p>Feedback flows into evals.</p></div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<p class="footnote">
  Demo metrics are illustrative highlights from internal eval runs. Feedback totals include a
  community baseline plus live session ratings. Built for Snowflake Applied AI.
</p>
""",
    unsafe_allow_html=True,
)
