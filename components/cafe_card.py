import html

import streamlit as st

from database.database import is_favorite, toggle_favorite
from database.models import Cafe
from services.places_service import get_cafe_image


def render_cafe_card(cafe: Cafe, key_prefix: str, show_ratings: bool = True, show_prices: bool = True) -> None:
    """Render a cafe summary card with favorite and details actions."""

    favorite = is_favorite(cafe.id)
    safe_id = "".join(character if character.isalnum() else "-" for character in cafe.id)
    with st.container(key=f"cafe-card-{key_prefix}-{safe_id}"):
        photo_credit = ", ".join(cafe.photo_attributions)
        st.image(
            get_cafe_image(cafe),
            caption=f"Photo: {photo_credit}" if photo_credit else None,
            use_container_width=True,
        )
        rating_html = ""
        if show_ratings and cafe.rating is not None:
            review_count = f" ({cafe.review_count:,})" if cafe.review_count is not None else ""
            rating_html = f'<span class="cafe-rating">&#9733; {cafe.rating:.1f}{review_count}</span>'
        price_html = f'<span class="cafe-price">{html.escape(cafe.price)}</span>' if show_prices and cafe.price else ""
        status_html = ""
        if cafe.is_open is not None:
            status_class = "is-open" if cafe.is_open else "is-closed"
            status_text = "Open now" if cafe.is_open else "Closed"
            status_html = f'<span class="place-status {status_class}">{status_text}</span>'
        distance_html = f"<span>{cafe.distance_meters / 1000:.1f} km</span>" if cafe.distance_meters is not None else ""
        location = cafe.location or cafe.address
        location_html = f'<div class="cafe-location">&#128205; {html.escape(location)}</div>' if location else ""
        description = cafe.description or "Verified place listing"
        st.markdown(
            f"""
            <div class="cafe-card-content">
                <div class="cafe-card-top">
                    <div>
                        <div class="cafe-type">{html.escape(cafe.category)}</div>
                        <h3 class="cafe-name">{html.escape(cafe.name)}</h3>
                    </div>
                    {rating_html}
                </div>
                {location_html}
                <div class="cafe-badges">{status_html}{distance_html}</div>
                <p class="cafe-description">{html.escape(description)}</p>
                <div class="cafe-card-footer">
                    {price_html}
                    <span class="view-details">View details</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        action_cols = st.columns(2, gap="small")
        with action_cols[0]:
            if st.button(
                "Remove favorite" if favorite else "Add favorite",
                key=f"{key_prefix}_favorite_{safe_id}",
                use_container_width=True,
            ):
                toggle_favorite(cafe.id)
                st.rerun()
        with action_cols[1]:
            if st.button("View Details", key=f"{key_prefix}_details_{safe_id}", use_container_width=True):
                st.session_state["selected_cafe_id"] = cafe.id
                st.session_state["previous_page"] = st.session_state.get("current_page", "Search")
                st.session_state["current_page"] = "Cafe Details"
                st.rerun()
