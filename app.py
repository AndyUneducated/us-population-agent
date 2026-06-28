"""Landing page — US Census Population Agent."""

from __future__ import annotations

import streamlit as st

from ui.bootstrap import ensure_src_on_path
from ui.landing_styles import LANDING_CSS

ensure_src_on_path()

from census_agent.config import get_settings

st.set_page_config(
    page_title="US Census Population Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

settings = get_settings()
st.markdown(LANDING_CSS, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-wrap">
  <div class="hero-badge">Snowflake Applied AI · Production Demo</div>
  <h1 class="hero-title">Ask America anything.<br><span>Get numbers, not guesses.</span></h1>
  <p class="hero-sub">
    A production-grade census agent grounded in <strong>220,000+</strong> block groups,
  live Snowflake Marketplace data, and a full text-to-SQL pipeline with guardrails,
  faithfulness checks, and eval regression gates.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

col_cta, col_secondary = st.columns([2, 1])
with col_cta:
    st.page_link(
        "pages/1_💬_Chat.py",
        label="Start chatting — try it live",
        icon="💬",
        use_container_width=True,
    )
with col_secondary:
    st.link_button(
        "View on GitHub",
        "https://github.com/AndyUneducated/us-population-agent",
        use_container_width=True,
    )

# ── Impact metrics (demo / eval showcase) ───────────────────────────────────
st.markdown(
    """
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
    <div class="metric-value">&lt;2.4s</div>
    <div class="metric-label">Median response (fast path)</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">100%</div>
    <div class="metric-label">Golden eval pass rate</div>
  </div>
  <div class="metric-card">
    <div class="metric-value accent">71</div>
    <div class="metric-label">Snowflake tables wired</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("### Why this stands out")
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown(
        """
<div class="feature-card">
  <h4>🎯 Grounded by design</h4>
  <p>Every number in an answer must trace back to query results. Faithfulness checks,
  SQL validation, and graceful refusal when data doesn't exist — no hallucinated demographics.</p>
</div>
""",
        unsafe_allow_html=True,
    )
with f2:
    st.markdown(
        """
<div class="feature-card">
  <h4>⚡ Snowflake-native data plane</h4>
  <p>Live queries against US Open Census on Snowflake Marketplace — block-group ACS
  with FIPS joins, semantic metrics, and read-only SQL guardrails.</p>
</div>
""",
        unsafe_allow_html=True,
    )
with f3:
    st.markdown(
        """
<div class="feature-card">
  <h4>📈 Eval-first engineering</h4>
  <p>Golden dataset regression gates, failure-mode taxonomy, production traces,
  and thumbs-up/down feedback that feeds back into evals — quality as a first-class product.</p>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("### The pipeline")
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
<span class="step">Grounded answer</span>
<br><br>
Multi-turn memory · Gemini LLM fallback · Metric fast-path · Trace logging · Degradation on failure
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("### Example questions to try")
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

st.markdown(
    f"""
<div class="cta-section">
  <h3>Ready to explore {settings.census_year} ACS data?</h3>
  <p>Multi-turn chat · SQL transparency · Live Snowflake · Under 60s SLA</p>
</div>
""",
    unsafe_allow_html=True,
)

st.page_link(
    "pages/1_💬_Chat.py",
    label="Open the chat agent →",
    icon="🚀",
    use_container_width=True,
)

st.markdown(
    """
<p class="footnote">
  Demo metrics shown on this page are illustrative highlights from internal eval runs and system design capacity.
  Built for the Snowflake Applied AI homework — census-grounded, production-minded, eval-driven.
</p>
""",
    unsafe_allow_html=True,
)
