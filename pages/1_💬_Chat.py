"""Interactive census chat — main agent experience."""

from __future__ import annotations

import streamlit as st

from ui.bootstrap import configure_streamlit_client, ensure_src_on_path
from ui.constants import FEEDBACK_DISPLAY_BASE
from ui.theme import CHAT_CSS

configure_streamlit_client()
ensure_src_on_path()

from census_agent.agent.orchestrator import CensusAgent
from census_agent.agent.rewriter import Message
from census_agent.config import get_settings
from census_agent.feedback import count_feedback, save_feedback

st.set_page_config(
    page_title="Chat · US Census Agent",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

settings = get_settings()
st.markdown(CHAT_CSS, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "feedback_numbers" not in st.session_state:
    st.session_state.feedback_numbers = {}


@st.cache_resource
def get_field_index():
    """Cache only the lexical index — not the agent (rewriter slots must stay per-session)."""
    from census_agent.retrieval.index import FieldIndex

    if settings.embedding_index_path.exists():
        return FieldIndex.load(settings.embedding_index_path)
    return None


def get_agent() -> CensusAgent:
    if "census_agent" not in st.session_state:
        index = get_field_index()
        st.session_state.census_agent = CensusAgent(settings=settings, index=index)
    return st.session_state.census_agent


def _reset_agent() -> None:
    agent = st.session_state.pop("census_agent", None)
    if agent is not None:
        agent.close()


def _display_feedback_number(seq: int) -> int:
    return FEEDBACK_DISPLAY_BASE + seq


def _user_question_for_assistant(assistant_index: int) -> str:
    if assistant_index > 0:
        prev = st.session_state.messages[assistant_index - 1]
        if prev.get("role") == "user":
            return str(prev.get("content", ""))
    return ""


def _record_feedback(assistant_index: int, rating: str) -> int:
    msg = st.session_state.messages[assistant_index]
    st.session_state.feedback[assistant_index] = rating
    _, seq = save_feedback(
        message_index=assistant_index,
        rating=rating,
        question=_user_question_for_assistant(assistant_index),
        answer=str(msg.get("content", "")),
        sql=msg.get("sql"),
        trace_id=msg.get("trace_id"),
        settings=settings,
    )
    display_num = _display_feedback_number(seq)
    st.session_state.feedback_numbers[assistant_index] = display_num
    return display_num


def _render_feedback_controls(assistant_index: int) -> None:
    rating = st.session_state.feedback.get(assistant_index)
    display_num = st.session_state.feedback_numbers.get(assistant_index)

    if rating and display_num:
        label = "helpful" if rating == "up" else "not helpful"
        st.markdown(
            f'<div class="feedback-thanks">'
            f"You are feedback <strong>#{display_num:,}</strong> — thanks for marking this answer as {label}. "
            f"It will feed into our eval loop."
            f"</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        """
<div class="feedback-callout">
  <strong>Rate this answer</strong> — your 👍/👎 directly improves the agent.
  You'll see your feedback number right after you click.
</div>
""",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    with cols[0]:
        if st.button("👍 Helpful", key=f"up_{assistant_index}", use_container_width=True):
            num = _record_feedback(assistant_index, "up")
            st.toast(f"You're feedback #{num:,} — thank you!", icon="👍")
            st.rerun()
    with cols[1]:
        if st.button("👎 Not helpful", key=f"down_{assistant_index}", use_container_width=True):
            num = _record_feedback(assistant_index, "down")
            st.toast(f"You're feedback #{num:,} — noted!", icon="👎")
            st.rerun()


def render_message(role: str, content: str, sql: str | None = None, rows: list | None = None) -> None:
    with st.chat_message(role):
        st.markdown(content)
        if sql and role == "assistant":
            with st.expander("View SQL"):
                st.code(sql, language="sql")
            if rows:
                st.dataframe(rows, use_container_width=True)
                if len(rows) == 1 and rows[0].get("value") is not None:
                    try:
                        st.metric(rows[0].get("metric", "Value"), rows[0].get("value"))
                    except Exception:
                        pass


# Top bar: back left, meta right
bar_left, bar_mid, bar_right = st.columns([1, 3.4, 1])
with bar_left:
    with st.container(key="homebtn"):
        st.page_link("app.py", label="Home", icon="🏠")
with bar_mid:
    st.markdown('<div class="chat-title">US Census Chat Agent</div>', unsafe_allow_html=True)
with bar_right:
    if st.button("Clear", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        st.session_state.feedback_numbers = {}
        _reset_agent()
        st.rerun()

community_total = FEEDBACK_DISPLAY_BASE + count_feedback(settings)
st.caption(
    f"{settings.census_year} ACS · `{settings.data_backend}` · "
    f"`{settings.llm_provider}` · **{community_total:,}+** community ratings"
)

# Seed question from landing page
if seed := st.session_state.pop("seed_prompt", None):
    st.session_state.messages.append({"role": "user", "content": seed})
    with st.spinner("Querying census data..."):
        agent = get_agent()
        history = [
            Message(role=m["role"], content=m["content"])
            for m in st.session_state.messages[:-1]
        ]
        resp = agent.ask(seed, history=history)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resp.answer,
            "sql": resp.sql,
            "rows": resp.rows,
            "trace_id": resp.trace.trace_id if resp.trace else None,
        }
    )

if not st.session_state.messages:
    st.info("Try: *What is the total population of California?* then follow up with *What about Texas?*")

for i, msg in enumerate(st.session_state.messages):
    render_message(
        msg["role"],
        msg["content"],
        msg.get("sql"),
        msg.get("rows"),
    )
    if msg["role"] == "assistant":
        _render_feedback_controls(i)

if prompt := st.chat_input("Ask a census question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    history = [
        Message(role=m["role"], content=m["content"])
        for m in st.session_state.messages[:-1]
    ]

    with st.chat_message("assistant"):
        with st.spinner("Querying census data..."):
            agent = get_agent()
            resp = agent.ask(prompt, history=history)

        st.markdown(resp.answer)
        if resp.sql:
            with st.expander("View SQL"):
                st.code(resp.sql, language="sql")
        if resp.rows:
            st.dataframe(resp.rows, use_container_width=True)

    trace_id = resp.trace.trace_id if resp.trace else None
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resp.answer,
            "sql": resp.sql,
            "rows": resp.rows,
            "trace_id": trace_id,
        }
    )
    st.rerun()
