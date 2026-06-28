"""Dark theme CSS shared across landing and chat pages."""

DARK_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0b0f17;
    --surface: #111827;
    --surface-2: #1a2332;
    --border: #243044;
    --text: #e8eef7;
    --muted: #8b9cb3;
    --accent: #22d3ee;
    --accent-2: #38bdf8;
    --accent-dim: rgba(34, 211, 238, 0.12);
    --success: #34d399;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', system-ui, sans-serif !important;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1080px;
}

/* Hide sidebar & default chrome */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"] {
    display: none !important;
}

#MainMenu, footer, header[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
}

h1, h2, h3, h4, p, label, span, .stMarkdown {
    color: var(--text);
}

.stCaption, small {
    color: var(--muted) !important;
}

/* Top bar */
.top-bar {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-bottom: 0.5rem;
    min-height: 2rem;
}

.gh-link {
    font-size: 0.8rem;
    color: var(--muted) !important;
    text-decoration: none;
    border: 1px solid var(--border);
    padding: 0.35rem 0.75rem;
    border-radius: 8px;
    transition: all 0.15s ease;
}
.gh-link:hover {
    color: var(--accent) !important;
    border-color: var(--accent);
}

/* Hero */
.hero-wrap {
    background: linear-gradient(145deg, #0b1220 0%, #111827 50%, #0c1929 100%);
    border-radius: 20px;
    padding: 2.75rem 2.25rem 2.25rem;
    margin-bottom: 1.5rem;
    border: 1px solid var(--border);
    box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.05), 0 24px 48px -24px rgba(0,0,0,0.6);
    position: relative;
    overflow: hidden;
    text-align: center;
}

.hero-wrap::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(34, 211, 238, 0.12) 0%, transparent 55%);
    pointer-events: none;
}

.hero-badge {
    display: inline-block;
    background: var(--accent-dim);
    border: 1px solid rgba(34, 211, 238, 0.35);
    color: var(--accent);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    margin-bottom: 1rem;
}

.hero-title {
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 700;
    line-height: 1.12;
    color: var(--text);
    margin: 0 0 0.85rem 0;
}

.hero-title span {
    background: linear-gradient(90deg, #22d3ee, #67e8f9, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 1.05rem;
    color: var(--muted);
    line-height: 1.65;
    max-width: 620px;
    margin: 0 auto;
}

/* Center CTA */
.cta-center-block {
    display: flex;
    justify-content: center;
    margin: 1.75rem 0 0.5rem;
}

.cta-center-block a {
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    padding: 0.85rem 2.5rem !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #0891b2, #0284c7) !important;
    color: #fff !important;
    border: 1px solid rgba(34, 211, 238, 0.4) !important;
    box-shadow: 0 8px 24px -8px rgba(34, 211, 238, 0.45) !important;
    text-decoration: none !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}

.cta-center-block a:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px -8px rgba(34, 211, 238, 0.55) !important;
}

/* Feedback highlight banner */
.feedback-banner {
    background: linear-gradient(90deg, rgba(52, 211, 153, 0.08), rgba(34, 211, 238, 0.08));
    border: 1px solid rgba(52, 211, 153, 0.25);
    border-radius: 14px;
    padding: 1rem 1.25rem;
    margin: 1.5rem 0;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.feedback-banner .fb-count {
    font-size: 2rem;
    font-weight: 700;
    color: var(--success);
    line-height: 1;
}

.feedback-banner .fb-text {
    color: var(--muted);
    font-size: 0.9rem;
    line-height: 1.5;
}

.feedback-banner .fb-text strong {
    color: var(--text);
}

/* Metrics */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.85rem;
    margin: 1.5rem 0;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.1rem 0.85rem;
    text-align: center;
    transition: border-color 0.2s ease, transform 0.2s ease;
}

.metric-card:hover {
    border-color: rgba(34, 211, 238, 0.35);
    transform: translateY(-2px);
}

.metric-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text);
    font-variant-numeric: tabular-nums;
}

.metric-value.accent { color: var(--accent); }
.metric-value.green { color: var(--success); }

.metric-label {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.3rem;
}

/* Feature cards */
.feature-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.1rem;
    height: 100%;
}

.feature-card h4 {
    color: var(--accent-2);
    font-size: 0.95rem;
    font-weight: 600;
    margin: 0 0 0.45rem 0;
}

.feature-card p {
    color: var(--muted);
    font-size: 0.85rem;
    line-height: 1.55;
    margin: 0;
}

.section-title {
    color: var(--text) !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    margin: 1.75rem 0 0.85rem !important;
}

.pipeline-box {
    background: #070b12;
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    color: var(--muted);
    line-height: 1.75;
    border: 1px solid var(--border);
}

.pipeline-box .step { color: var(--accent); }
.pipeline-box .arrow { color: #475569; }

.footnote {
    text-align: center;
    color: #5c6b80;
    font-size: 0.72rem;
    margin-top: 2rem;
}

/* Chat page */
.chat-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}

.back-btn a {
    font-size: 0.85rem !important;
    color: var(--muted) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 0.35rem 0.75rem !important;
    background: var(--surface) !important;
}

.feedback-callout {
    background: var(--surface-2);
    border: 1px dashed rgba(34, 211, 238, 0.35);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0 1rem;
    font-size: 0.88rem;
    color: var(--muted);
}

.feedback-callout strong { color: var(--accent); }

.feedback-thanks {
    background: rgba(52, 211, 153, 0.1);
    border: 1px solid rgba(52, 211, 153, 0.35);
    border-radius: 10px;
    padding: 0.65rem 0.9rem;
    color: var(--success);
    font-size: 0.9rem;
    margin-top: 0.35rem;
}

/* Streamlit widgets dark */
.stButton > button {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

div[data-testid="stChatInput"] {
    border-color: var(--border) !important;
}

.stAlert {
    background: var(--surface) !important;
    border-color: var(--border) !important;
}
</style>
"""

LANDING_CSS = DARK_THEME_CSS

CHAT_CSS = DARK_THEME_CSS
