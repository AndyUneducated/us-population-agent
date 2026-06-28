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
    padding-top: 1.1rem;
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
    margin-bottom: 0.75rem;
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
    background:
        linear-gradient(145deg, rgba(15, 23, 42, 0.95) 0%, rgba(17, 24, 39, 0.96) 48%, rgba(8, 47, 73, 0.92) 100%),
        radial-gradient(circle at 50% 0%, rgba(34, 211, 238, 0.25), transparent 45%);
    border-radius: 20px;
    padding: 2.65rem 2.25rem 2.4rem;
    margin-bottom: 1.25rem;
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
    font-size: clamp(2.15rem, 5vw, 3.2rem);
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
    font-size: 1rem;
    color: #a7f3d0;
    line-height: 1.5;
    max-width: 560px;
    margin: 0 auto;
    text-align: center;
    letter-spacing: 0.01em;
}

/* All page links: no underline by default */
div[data-testid="stPageLink"] a {
    text-decoration: none !important;
}

.primary-cta-note {
    color: var(--muted);
    font-size: 0.78rem;
    text-align: center;
    margin: 0.9rem 0 0.5rem;
}

/* Primary CTA (landing) — scoped to keyed container */
.st-key-bigcta div[data-testid="stPageLink"] {
    justify-content: center !important;
}

.st-key-bigcta div[data-testid="stPageLink"] a {
    background: linear-gradient(135deg, #06b6d4, #0284c7) !important;
    color: #fff !important;
    border: 1px solid rgba(34, 211, 238, 0.45) !important;
    border-radius: 12px !important;
    padding: 0.9rem 2rem !important;
    box-shadow: 0 12px 32px -14px rgba(34, 211, 238, 0.7) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.5rem !important;
    width: 100% !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}

.st-key-bigcta div[data-testid="stPageLink"] a:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 40px -12px rgba(34, 211, 238, 0.8) !important;
}

.st-key-bigcta div[data-testid="stPageLink"] a p,
.st-key-bigcta div[data-testid="stPageLink"] a span {
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: #fff !important;
    margin: 0 !important;
}

/* Home button (chat) — small, scoped to keyed container */
.st-key-homebtn div[data-testid="stPageLink"] a {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 0.4rem 0.8rem !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 0.35rem !important;
}

.st-key-homebtn div[data-testid="stPageLink"] a:hover {
    border-color: var(--accent) !important;
}

.st-key-homebtn div[data-testid="stPageLink"] a p,
.st-key-homebtn div[data-testid="stPageLink"] a span {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    margin: 0 !important;
}

.chat-title {
    text-align: center;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text);
    padding-top: 0.35rem;
}

/* Feedback highlight banner */
.feedback-hero {
    background:
        linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(34, 211, 238, 0.08)),
        var(--surface);
    border: 1px solid rgba(52, 211, 153, 0.28);
    border-radius: 18px;
    padding: 1.35rem 1.45rem;
    margin: 1.75rem 0 1.35rem;
    display: grid;
    grid-template-columns: minmax(160px, 0.8fr) 1.6fr;
    gap: 1rem;
    align-items: center;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}

.fb-kicker {
    color: var(--muted);
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}

.fb-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--success);
    line-height: 1.05;
    font-variant-numeric: tabular-nums;
}

.fb-copy {
    color: var(--muted);
    font-size: 1rem;
    line-height: 1.45;
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

.metric-card:first-child {
    border-color: rgba(34, 211, 238, 0.45);
    background: linear-gradient(180deg, rgba(34, 211, 238, 0.1), rgba(17, 24, 39, 0.96));
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

/* Example cards */
.example-card {
    background: linear-gradient(180deg, rgba(34, 211, 238, 0.06), rgba(17, 24, 39, 0.96));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem;
    min-height: 150px;
    margin-bottom: 0.65rem;
}

.example-title {
    color: var(--accent);
    font-size: 0.86rem;
    font-weight: 700;
    margin-bottom: 0.45rem;
}

.example-copy {
    color: var(--muted);
    font-size: 0.82rem;
    line-height: 1.45;
}

.section-title {
    color: var(--text) !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    margin: 1.75rem 0 0.85rem !important;
}

/* Section header (eyebrow kicker + title + sub) */
.section-head {
    margin: 2.25rem 0 1.05rem;
}

.sh-kicker {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--accent);
    background: var(--accent-dim);
    border: 1px solid rgba(34, 211, 238, 0.28);
    border-radius: 999px;
    padding: 0.22rem 0.7rem;
}

.sh-title {
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    margin: 0.6rem 0 0.2rem !important;
    line-height: 1.2 !important;
}

.sh-sub {
    color: var(--muted) !important;
    font-size: 0.9rem !important;
    line-height: 1.5 !important;
    margin: 0 !important;
    max-width: 640px;
}

/* Conversation preview (flagship multi-turn comparison) */
.convo {
    background: linear-gradient(180deg, rgba(34, 211, 238, 0.06), rgba(17, 24, 39, 0.97));
    border: 1px solid rgba(34, 211, 238, 0.22);
    border-radius: 18px;
    padding: 1.2rem 1.3rem 1.05rem;
    box-shadow: 0 20px 44px -28px rgba(34, 211, 238, 0.5);
}

.convo-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.85rem;
}

.convo-tag::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.18);
}

.bubble {
    display: flex;
    gap: 0.55rem;
    margin: 0.5rem 0;
    align-items: flex-start;
}

.bubble.bot { flex-direction: row-reverse; }

.bubble .who {
    flex: 0 0 auto;
    width: 26px;
    height: 26px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    background: var(--surface-2);
    border: 1px solid var(--border);
}

.bubble .msg {
    border-radius: 12px;
    padding: 0.55rem 0.8rem;
    font-size: 0.88rem;
    line-height: 1.45;
    max-width: 82%;
}

.bubble.user .msg {
    background: var(--surface-2);
    color: var(--text);
    border: 1px solid var(--border);
    border-top-left-radius: 4px;
}

.bubble.bot .msg {
    background: rgba(34, 211, 238, 0.1);
    border: 1px solid rgba(34, 211, 238, 0.25);
    color: #d6f4fb;
    border-top-right-radius: 4px;
}

.bubble .msg b { color: var(--accent); font-variant-numeric: tabular-nums; }
.bubble .msg .mem { color: var(--success); font-size: 0.78rem; }

.convo-note {
    color: var(--muted);
    font-size: 0.8rem;
    line-height: 1.5;
    margin-top: 0.75rem;
    padding-top: 0.7rem;
    border-top: 1px dashed var(--border);
}

.convo-note b { color: var(--accent); }

/* Quick-launch chips (clickable buttons) */
.chips-intro {
    color: var(--muted);
    font-size: 0.82rem;
    margin: 1.15rem 0 0.5rem;
}

.st-key-chips .stButton > button {
    width: 100%;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 999px !important;
    color: var(--muted) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.55rem 0.7rem !important;
    transition: transform 0.14s ease, border-color 0.14s ease, color 0.14s ease, background 0.14s ease !important;
}

.st-key-chips .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--accent-dim) !important;
    transform: translateY(-1px);
}

/* Run-conversation CTA — scoped */
.st-key-convocta .stButton > button {
    width: 100%;
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.18), rgba(2, 132, 199, 0.14)) !important;
    border: 1px solid rgba(34, 211, 238, 0.45) !important;
    border-radius: 12px !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1rem !important;
    margin-top: 0.85rem !important;
    transition: transform 0.14s ease, box-shadow 0.14s ease !important;
}

.st-key-convocta .stButton > button:hover {
    transform: translateY(-1px);
    color: #fff !important;
    box-shadow: 0 12px 30px -16px rgba(34, 211, 238, 0.8) !important;
}

.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 0.85rem;
}

.pipeline-card {
    background: #070b12;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem;
    min-height: 120px;
}

.pipeline-card span {
    color: #475569;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
}

.pipeline-card strong {
    display: block;
    color: var(--accent);
    font-size: 1rem;
    margin: 0.4rem 0 0.35rem;
}

.pipeline-card p {
    color: var(--muted);
    font-size: 0.82rem;
    line-height: 1.45;
    margin: 0;
}

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
