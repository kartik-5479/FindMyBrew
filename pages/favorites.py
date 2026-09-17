import streamlit as st

from components.cafe_card import render_cafe_card
from database.database import get_favorites
from services.places_service import get_cafe_by_id


def render_favorites() -> None:
    """Render the user's saved cafes."""

    st.markdown(
        """
        <div class="search-header">
            <div class="search-eyebrow">SAVED PLACES</div>
            <h1 class="search-title">Your <span>favorites.</span></h1>
            <p class="search-description">
                Keep track of cafes and lounges you want to revisit.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    favorite_ids = sorted(get_favorites())
    cafes = [cafe for cafe_id in favorite_ids if (cafe := get_cafe_by_id(cafe_id)) is not None]

    st.markdown(
        f"""
        <div class="search-results-heading">
            <div>
                <span class="results-eyebrow">COLLECTION</span>
                <h2>Saved cafes</h2>
            </div>
            <span class="results-count">{len(cafes)} places</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not cafes:
        st.markdown(
            """
            <div class="empty-state">
                <h3>No favorites yet</h3>
                <p>Add cafes from Search or Cafe Details and they will appear here.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Explore cafes", key="favorites_empty_search", type="primary"):
            st.session_state["current_page"] = "Search"
            st.rerun()
        return

    card_columns = st.columns(2, gap="medium")
    for index, cafe in enumerate(cafes):
        with card_columns[index % 2]:
            render_cafe_card(
                cafe,
                key_prefix="favorites",
                show_ratings=st.session_state.get("show_ratings", True),
                show_prices=st.session_state.get("show_prices", True),
            )
