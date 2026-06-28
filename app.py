"""Landing page — US Census Population Agent."""

from __future__ import annotations

import streamlit as st

from ui.bootstrap import ensure_src_on_path
from ui.constants import FEEDBACK_DISPLAY_BASE
from ui.theme import LANDING_CSS

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
  <p class="hero-sub">Live Census data · Snowflake SQL · Eval-driven AI</p>
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

st.markdown('<p class="section-title">Example questions — click to launch</p>', unsafe_allow_html=True)
example_items = [
    (
        "State comparison",
        "Compare population between California and Texas, then explain the difference.",
    ),
    (
        "Economic signal",
        "What is the median household income in New York, and how should I interpret it?",
    ),
    (
        "Labor market",
        "What is the unemployment rate in Florida? Show the SQL behind it.",
    ),
    (
        "Follow-up ready",
        "Start with California population, then ask: what about Texas?",
    ),
]
example_cols = st.columns(4)
for col, (title, prompt) in zip(example_cols, example_items):
    with col:
        st.markdown(
            f"""
<div class="example-card">
  <div class="example-title">{title}</div>
  <div class="example-copy">{prompt}</div>
</div>
""",
            unsafe_allow_html=True,
        )
        if st.button("Ask this", key=f"ex_{title}", use_container_width=True):
            st.session_state["seed_prompt"] = prompt
            st.switch_page("pages/1_💬_Chat.py")

st.markdown('<p class="section-title">Why this stands out</p>', unsafe_allow_html=True)
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

st.markdown('<p class="section-title">The pipeline</p>', unsafe_allow_html=True)
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
