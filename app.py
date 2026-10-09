from pathlib import Path

import streamlit as st

from components.footer import render_footer
from components.navbar import render_navbar
from database.database import initialize_session_defaults
from pages.cafe_details import render_cafe_details
from pages.favorites import render_favorites
from pages.home import render_home
from pages.search import render_search
from pages.settings import render_settings

st.set_page_config(
    page_title="FindMyBrew",
    page_icon="coffee",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "styles" / "main.css"


def load_css() -> None:
    """Load the global FindMyBrew stylesheet."""

    if CSS_PATH.exists():
        st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def navigate_to(page: str) -> None:
    """Change the active page while keeping detail back-navigation context."""

    if page != st.session_state.get("current_page"):
        st.session_state["previous_page"] = st.session_state.get("current_page", "Home")
    st.session_state["current_page"] = page
    if page != "Cafe Details":
        st.session_state["selected_cafe_id"] = st.session_state.get("selected_cafe_id")


def render_current_page() -> None:
    pages = {
        "Home": render_home,
        "Search": render_search,
        "Favorites": render_favorites,
        "Settings": render_settings,
        "Cafe Details": render_cafe_details,
    }
    current_page = st.session_state.get("current_page", "Home")
    pages.get(current_page, render_home)()


initialize_session_defaults()
load_css()
render_navbar(active_page=st.session_state.get("current_page", "Home"), on_navigate=navigate_to)
render_current_page()
render_footer()
