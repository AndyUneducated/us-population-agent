"""CSS for the marketing landing page."""

LANDING_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', system-ui, sans-serif;
}

#MainMenu, footer, header[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

.hero-wrap {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 45%, #0c4a6e 100%);
    border-radius: 24px;
    padding: 3rem 2.5rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(56, 189, 248, 0.25);
    box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.5);
}

.hero-wrap::before {
    content: "";
    position: absolute;
    top: -40%;
    right: -10%;
    width: 420px;
    height: 420px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.35) 0%, transparent 70%);
    pointer-events: none;
}

.hero-badge {
    display: inline-block;
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #7dd3fc;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    margin-bottom: 1.25rem;
}

.hero-title {
    font-size: clamp(2rem, 5vw, 3.25rem);
    font-weight: 700;
    line-height: 1.1;
    color: #f8fafc;
    margin: 0 0 1rem 0;
}

.hero-title span {
    background: linear-gradient(90deg, #38bdf8, #a5f3fc, #38bdf8);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 1.15rem;
    color: #94a3b8;
    line-height: 1.6;
    max-width: 640px;
    margin-bottom: 0;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.metric-card {
    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.25rem 1rem;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 24px -8px rgba(15, 23, 42, 0.12);
}

.metric-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
}

.metric-value.accent {
    color: #0284c7;
}

.metric-label {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.35rem;
    font-weight: 500;
}

.feature-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.35rem 1.25rem;
    height: 100%;
}

.feature-card h4 {
    color: #0f172a;
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
}

.feature-card p {
    color: #64748b;
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 0;
}

.pipeline-box {
    background: #0f172a;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #94a3b8;
    line-height: 1.7;
    border: 1px solid #334155;
    overflow-x: auto;
}

.pipeline-box .step { color: #38bdf8; font-weight: 500; }
.pipeline-box .arrow { color: #475569; }

.cta-section {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    border-radius: 20px;
    padding: 2rem 2rem;
    text-align: center;
    margin: 2rem 0 1rem;
    border: 1px solid rgba(255,255,255,0.1);
}

.cta-section h3 {
    color: #fff;
    font-size: 1.5rem;
    margin: 0 0 0.5rem 0;
}

.cta-section p {
    color: #bae6fd;
    margin: 0 0 1.25rem 0;
    font-size: 1rem;
}

.footnote {
    text-align: center;
    color: #94a3b8;
    font-size: 0.75rem;
    margin-top: 2rem;
}

div[data-testid="stPageLink-NavLink"] a {
    font-weight: 600;
}
</style>
"""
