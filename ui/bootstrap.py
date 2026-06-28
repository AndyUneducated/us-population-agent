"""Shared path bootstrap for Streamlit entrypoints."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ensure_src_on_path() -> Path:
    root_str = str(ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    src_str = str(ROOT / "src")
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
    return ROOT


def configure_streamlit_client() -> None:
    """Disable default multipage sidebar nav before first paint (avoids flash)."""
    import streamlit as st

    st.set_option("client.showSidebarNavigation", False)
