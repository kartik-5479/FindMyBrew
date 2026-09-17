import streamlit as st

from components.cafe_card import render_cafe_card
from services.places_service import CATEGORIES, get_popular_cafes


def _go_to_search(location: str = "", category: str = "All") -> None:
    st.session_state["search_location"] = location.strip()
    st.session_state["selected_category"] = category if category in CATEGORIES else "All"
    st.session_state["current_page"] = "Search"
    st.rerun()


def render_home() -> None:
    """Render the FindMyBrew home page."""

    st.markdown(
        """
        <section class="brew-hero">
            <div class="brew-hero-content">
                <div class="brew-hero-eyebrow">YOUR LOCAL CAFE DISCOVERY GUIDE</div>
                <h1 class="brew-hero-title">
                    Find your next
                    <span class="brew-hero-highlight">favorite brew.</span>
                </h1>
                <p class="brew-hero-description">
                    Discover cafes, coffee shops, restaurants, lounges, and hidden gems around you, all in one place.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="brew-search-label">&#128205; Where are you looking?</div>', unsafe_allow_html=True)

    location_col, button_col = st.columns([3.5, 1], gap="medium")
    with location_col:
        location = st.text_input(
            "Location",
            value=st.session_state.get("default_location", ""),
            placeholder="Enter a city, area, or landmark...",
            label_visibility="collapsed",
            key="home_location_input",
        )
    with button_col:
        if st.button("Find Cafes", type="primary", use_container_width=True, key="home_find_cafes"):
            _go_to_search(location, st.session_state.get("default_category", "All"))

    st.markdown(
        """
        <div class="brew-hero-meta">
            <span>&#9749; Cafes &amp; Coffee Shops</span>
            <span>&bull;</span>
            <span>&#127869; Restaurants</span>
            <span>&bull;</span>
            <span>&#127769; Lounges</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="search-section-label filter-label">Browse by mood</div>', unsafe_allow_html=True)
    category_cols = st.columns(4, gap="small")
    for column, category in zip(category_cols, ("Coffee", "Cafe", "Restaurant", "Lounge")):
        with column:
            if st.button(category, key=f"home_category_{category.lower()}", use_container_width=True):
                _go_to_search(location, category)

    st.markdown(
        """
        <div class="search-results-heading home-popular-heading">
            <div>
                <span class="results-eyebrow">POPULAR NEARBY</span>
                <h2>Popular places</h2>
            </div>
            <span class="results-count">Top picks</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    card_columns = st.columns(2, gap="medium")
    for index, cafe in enumerate(get_popular_cafes(4)):
        with card_columns[index % 2]:
            render_cafe_card(
                cafe,
                key_prefix="home",
                show_ratings=st.session_state.get("show_ratings", True),
                show_prices=st.session_state.get("show_prices", True),
            )
