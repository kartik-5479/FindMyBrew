import html

import streamlit as st

from components.cafe_card import render_cafe_card
from components.filter_panel import render_filter_panel
from services.places_service import search_cafes


def render_search() -> None:
    """Render the FindMyBrew cafe discovery page."""

    st.markdown(
        """
        <div class="search-header">
            <div class="search-eyebrow">FIND YOUR BREW</div>
            <h1 class="search-title">Discover your next <span>favorite cafe.</span></h1>
            <p class="search-description">
                Search cafes, coffee shops, restaurants and hidden gems around your favorite places.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="search-section-label">&#128205; Where are you looking?</div>', unsafe_allow_html=True)
    location_col, button_col = st.columns([3.5, 1], gap="medium")

    with location_col:
        location = st.text_input(
            "Location",
            value=st.session_state.get("search_location", ""),
            placeholder="Enter a city, area, or landmark...",
            label_visibility="collapsed",
            key="search_location_input",
        )
    with button_col:
        if st.button("Search Cafes", type="primary", use_container_width=True, key="search_cafes_button"):
            st.session_state["search_location"] = location.strip()
            st.rerun()

    render_filter_panel("search")

    current_location = st.session_state.get("search_location", "")
    current_category = st.session_state.get("selected_category", "All")
    results = search_cafes(current_location, current_category)
    heading = html.escape(current_location) if current_location else "Popular places"
    eyebrow = "RESULTS NEAR" if current_location else "EXPLORE"
    category_suffix = "" if current_category == "All" else f" in {html.escape(current_category)}"

    st.markdown(
        f"""
        <div class="search-results-heading">
            <div>
                <span class="results-eyebrow">{eyebrow}</span>
                <h2>{heading}</h2>
            </div>
            <span class="results-count">{len(results)} places{category_suffix}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not results:
        st.markdown(
            """
            <div class="empty-state">
                <h3>No cafes found</h3>
                <p>Try a broader location or switch the category filter.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    card_columns = st.columns(2, gap="medium")
    for index, cafe in enumerate(results):
        with card_columns[index % 2]:
            render_cafe_card(
                cafe,
                key_prefix="search",
                show_ratings=st.session_state.get("show_ratings", True),
                show_prices=st.session_state.get("show_prices", True),
            )
