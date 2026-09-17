import streamlit as st

from services.places_service import CATEGORIES


def render_filter_panel(key_prefix: str = "search") -> None:
    """Render category filter buttons backed by session state."""

    st.markdown('<div class="search-section-label filter-label">Explore by category</div>', unsafe_allow_html=True)
    columns = st.columns(len(CATEGORIES), gap="small")

    for column, category in zip(columns, CATEGORIES):
        with column:
            active = st.session_state.get("selected_category", "All") == category
            if st.button(
                category,
                key=f"{key_prefix}_category_{category.lower()}",
                type="primary" if active else "secondary",
                use_container_width=True,
            ):
                st.session_state["selected_category"] = category
                st.session_state["current_page"] = "Search"
                st.rerun()
