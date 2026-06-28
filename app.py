"""Streamlit chat UI for the US Census agent."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from census_agent.agent.orchestrator import CensusAgent
from census_agent.agent.rewriter import Message
from census_agent.config import get_settings

st.set_page_config(page_title="US Census Chat Agent", page_icon="📊", layout="centered")
st.title("US Census Population Agent")
st.caption("Ask questions about US population, income, housing, and demographics (ACS block-group data).")

settings = get_settings()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback" not in st.session_state:
    st.session_state.feedback = {}


@st.cache_resource
def get_agent() -> CensusAgent:
    return CensusAgent(settings=settings)


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


# Render history
for i, msg in enumerate(st.session_state.messages):
    render_message(
        msg["role"],
        msg["content"],
        msg.get("sql"),
        msg.get("rows"),
    )
    if msg["role"] == "assistant":
        cols = st.columns(2)
        with cols[0]:
            if st.button("👍", key=f"up_{i}"):
                st.session_state.feedback[i] = "up"
        with cols[1]:
            if st.button("👎", key=f"down_{i}"):
                st.session_state.feedback[i] = "down"

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

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resp.answer,
            "sql": resp.sql,
            "rows": resp.rows,
        }
    )
    st.rerun()

with st.sidebar:
    st.header("About")
    st.write(f"Data vintage: **{settings.census_year}** ACS")
    st.write(f"Backend: `{settings.data_backend}`")
    st.write(f"LLM: `{settings.llm_provider}`")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()
