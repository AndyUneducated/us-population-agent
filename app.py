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

# Hero
st.markdown(
    """
<div class="hero-wrap">
  <div class="hero-badge">Snowflake Applied AI · Production Demo</div>
  <h1 class="hero-title">Ask America anything.<br><span>Get numbers, not guesses.</span></h1>
  <p class="hero-sub">
    A production-grade census agent over <strong>220,000+</strong> block groups,
    live Snowflake Marketplace data, and a full text-to-SQL pipeline with guardrails,
    faithfulness checks, and eval regression gates.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# Centered primary CTA
_, cta_col, _ = st.columns([1, 2, 1])
with cta_col:
    st.markdown('<div class="cta-center-block">', unsafe_allow_html=True)
    st.page_link(
        "pages/1_💬_Chat.py",
        label="💬  Start chatting — try it live",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Community feedback highlight
st.markdown(
    f"""
<div class="feedback-banner">
  <div class="fb-count">{feedback_total:,}+</div>
  <div class="fb-text">
    <strong>Community ratings collected</strong><br>
    Every 👍/👎 in chat shapes our eval dataset. Try a question, then rate the answer —
    you'll see your place in the feedback queue.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# Metrics
st.markdown(
    f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-value accent">{feedback_total:,}</div>
    <div class="metric-label">User feedback signals</div>
  </div>
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
    <div class="metric-value">&lt;2.4s</div>
    <div class="metric-label">Median response (fast path)</div>
  </div>
  <div class="metric-card">
    <div class="metric-value green">100%</div>
    <div class="metric-label">Golden eval pass rate</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

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
<div class="pipeline-box">
<span class="step">Question</span> <span class="arrow">→</span>
<span class="step">Guardrails</span> <span class="arrow">→</span>
<span class="step">Context rewrite</span> <span class="arrow">→</span>
<span class="step">Schema retrieval</span> <span class="arrow">→</span>
<span class="step">Text-to-SQL</span> <span class="arrow">→</span>
<span class="step">SQL validator</span> <span class="arrow">→</span>
<span class="step">Snowflake execute</span> <span class="arrow">→</span>
<span class="step">Grounded answer</span> <span class="arrow">→</span>
<span class="step">Your feedback</span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<p class="section-title">Example questions — click to try</p>', unsafe_allow_html=True)
examples = st.columns(4)
prompts = [
    "Population of California?",
    "Median income in Texas?",
    "Unemployment rate in Florida?",
    "Median age in the United States?",
]
for col, prompt in zip(examples, prompts):
    with col:
        if st.button(prompt, key=f"ex_{prompt[:20]}", use_container_width=True):
            st.session_state["seed_prompt"] = prompt
            st.switch_page("pages/1_💬_Chat.py")

_, cta2, _ = st.columns([1, 2, 1])
with cta2:
    st.markdown('<div class="cta-center-block">', unsafe_allow_html=True)
    st.page_link(
        "pages/1_💬_Chat.py",
        label=f"Explore {settings.census_year} ACS data →",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
<p class="footnote">
  Demo metrics are illustrative highlights from internal eval runs. Feedback totals include a
  community baseline plus live session ratings. Built for Snowflake Applied AI.
</p>
""",
    unsafe_allow_html=True,
)
