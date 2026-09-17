import html

import streamlit as st

from components.map_view import render_map_view
from components.review_card import render_review_card
from database.database import is_favorite, toggle_favorite
from services.places_service import get_cafe_by_id


def _return_page() -> str:
    previous_page = st.session_state.get("previous_page", "Search")
    return previous_page if previous_page in {"Home", "Search", "Favorites"} else "Search"


def render_cafe_details() -> None:
    """Render details for the selected cafe."""

    cafe = get_cafe_by_id(st.session_state.get("selected_cafe_id"))
    if cafe is None:
        st.markdown(
            """
            <div class="empty-state">
                <h3>Cafe not found</h3>
                <p>The selected cafe is unavailable. Go back to search and choose another place.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Back to Search", key="details_invalid_back"):
            st.session_state["current_page"] = "Search"
            st.session_state["selected_cafe_id"] = None
            st.rerun()
        return

    favorite = is_favorite(cafe.id)
    rating_html = f'<span>&#9733; {cafe.rating:.1f}</span>' if st.session_state.get("show_ratings", True) else ""
    price_html = f'<span>{html.escape(cafe.price)}</span>' if st.session_state.get("show_prices", True) else ""

    st.markdown(
        f"""
        <section class="details-hero">
            <div>
                <div class="search-eyebrow">{html.escape(cafe.category)}</div>
                <h1>{html.escape(cafe.name)}</h1>
                <p>{html.escape(cafe.description)}</p>
                <div class="details-meta">
                    {rating_html}
                    {price_html}
                    <span>&#128205; {html.escape(cafe.location)}</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    action_cols = st.columns([1, 1, 3], gap="small")
    with action_cols[0]:
        if st.button("Back", key="details_back", use_container_width=True):
            st.session_state["current_page"] = _return_page()
            st.rerun()
    with action_cols[1]:
        if st.button(
            "Remove favorite" if favorite else "Add favorite",
            key=f"details_favorite_{cafe.id}",
            use_container_width=True,
        ):
            toggle_favorite(cafe.id)
            st.rerun()

    info_col, map_col = st.columns([1.15, 0.85], gap="large")
    with info_col:
        st.markdown(
            f"""
            <div class="detail-panel">
                <h3>About this place</h3>
                <p><strong>Address:</strong> {html.escape(cafe.address)}</p>
                <p><strong>Opening hours:</strong> {html.escape(cafe.opening_hours)}</p>
                <div class="amenities-list">
                    {''.join(f'<span>{html.escape(item)}</span>' for item in cafe.amenities)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with map_col:
        render_map_view(cafe)

    st.markdown('<div class="search-section-label filter-label">Reviews</div>', unsafe_allow_html=True)
    if cafe.reviews:
        for index, review in enumerate(cafe.reviews):
            render_review_card(review, f"review_{cafe.id}_{index}")
    else:
        st.markdown(
            """
            <div class="empty-state small-empty">
                <h3>No reviews yet</h3>
                <p>This cafe does not have local reviews in the mock dataset.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
