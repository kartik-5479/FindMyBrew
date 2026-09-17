import html

import streamlit as st

from database.database import is_favorite, toggle_favorite
from database.models import Cafe


CATEGORY_ICONS = {
    "Coffee": "&#9749;",
    "Cafe": "&#127856;",
    "Restaurant": "&#127869;",
    "Lounge": "&#127769;",
}


def render_cafe_card(cafe: Cafe, key_prefix: str, show_ratings: bool = True, show_prices: bool = True) -> None:
    """Render a cafe summary card with favorite and details actions."""

    favorite = is_favorite(cafe.id)
    icon = CATEGORY_ICONS.get(cafe.category, "&#9749;")
    rating_html = f'<div class="cafe-rating">&#9733; {cafe.rating:.1f}</div>' if show_ratings else ""
    price_html = f"<span>{html.escape(cafe.price)}</span>" if show_prices else "<span></span>"

    st.markdown(
        f"""
        <div class="cafe-card">
            <div class="cafe-card-image">
                <span class="cafe-image-icon">{icon}</span>
                <span class="cafe-favorite {'is-favorite' if favorite else ''}">{'&#9829;' if favorite else '&#9825;'}</span>
            </div>
            <div class="cafe-card-content">
                <div class="cafe-card-top">
                    <div>
                        <div class="cafe-type">{html.escape(cafe.category)}</div>
                        <h3 class="cafe-name">{html.escape(cafe.name)}</h3>
                    </div>
                    {rating_html}
                </div>
                <div class="cafe-location">&#128205; {html.escape(cafe.location)}</div>
                <p class="cafe-description">{html.escape(cafe.description)}</p>
                <div class="cafe-card-footer">
                    {price_html}
                    <span class="view-details">View details</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    action_cols = st.columns(2, gap="small")
    with action_cols[0]:
        if st.button(
            "Remove favorite" if favorite else "Add favorite",
            key=f"{key_prefix}_favorite_{cafe.id}",
            use_container_width=True,
        ):
            toggle_favorite(cafe.id)
            st.rerun()
    with action_cols[1]:
        if st.button("View Details", key=f"{key_prefix}_details_{cafe.id}", use_container_width=True):
            st.session_state["selected_cafe_id"] = cafe.id
            st.session_state["previous_page"] = st.session_state.get("current_page", "Search")
            st.session_state["current_page"] = "Cafe Details"
            st.rerun()
