"""Interactive census chat — main agent experience."""

from __future__ import annotations

import streamlit as st

from ui.bootstrap import ensure_src_on_path

ensure_src_on_path()

from census_agent.agent.orchestrator import CensusAgent
from census_agent.agent.rewriter import Message
from census_agent.config import get_settings
from census_agent.feedback import save_feedback

st.set_page_config(
    page_title="Chat · US Census Agent",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded",
)

settings = get_settings()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}


@st.cache_resource
def get_agent() -> CensusAgent:
    return CensusAgent(settings=settings)


def _user_question_for_assistant(assistant_index: int) -> str:
    if assistant_index > 0:
        prev = st.session_state.messages[assistant_index - 1]
        if prev.get("role") == "user":
            return str(prev.get("content", ""))
    return ""


def _record_feedback(assistant_index: int, rating: str) -> None:
    msg = st.session_state.messages[assistant_index]
    st.session_state.feedback[assistant_index] = rating
    save_feedback(
        message_index=assistant_index,
        rating=rating,
        question=_user_question_for_assistant(assistant_index),
        answer=str(msg.get("content", "")),
        sql=msg.get("sql"),
        trace_id=msg.get("trace_id"),
        settings=settings,
    )


def _render_feedback_controls(assistant_index: int) -> None:
    rating = st.session_state.feedback.get(assistant_index)
    if rating == "up":
        st.success("Thanks — marked as helpful.")
        return
    if rating == "down":
        st.info("Thanks — feedback recorded. We'll use this to improve answers.")
        return

    st.caption("Was this answer helpful?")
    cols = st.columns(2)
    with cols[0]:
        if st.button("👍 Helpful", key=f"up_{assistant_index}", use_container_width=True):
            _record_feedback(assistant_index, "up")
            st.toast("Thanks for your feedback!", icon="👍")
            st.rerun()
    with cols[1]:
        if st.button("👎 Not helpful", key=f"down_{assistant_index}", use_container_width=True):
            _record_feedback(assistant_index, "down")
            st.toast("Feedback saved — thank you.", icon="👎")
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


with st.sidebar:
    st.page_link("app.py", label="← Back to overview", icon="🏠")
    st.divider()
    st.header("Session")
    st.caption(f"**{settings.census_year}** ACS · `{settings.data_backend}` · `{settings.llm_provider}`")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.feedback = {}
        st.rerun()

st.title("US Census Chat Agent")
st.caption("Ask about population, income, housing, employment, and demographics — grounded in live Snowflake data.")

# Seed question from landing page example buttons
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
    st.rerun()

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
