import html

import streamlit as st

from components.map_view import render_map_view
from components.review_card import render_review_card
from database.database import is_favorite, toggle_favorite
from services.gemini_service import get_ai_recommendations, get_ai_vibe
from services.places_service import get_cafe_by_id, get_cafe_image
from utils.location import parse_search_intent
from services.review_service import get_reviews


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
    photo_credit = ", ".join(cafe.photo_attributions)
    with st.container(key="cafe-detail-photo"):
        st.image(get_cafe_image(cafe), caption=f"Photo: {photo_credit}" if photo_credit else None, use_container_width=True)
    review_count = f" ({cafe.review_count:,} reviews)" if cafe.review_count is not None else ""
    rating_html = f'<span>&#9733; {cafe.rating:.1f}{review_count}</span>' if st.session_state.get("show_ratings", True) and cafe.rating is not None else ""
    price_html = f'<span>{html.escape(cafe.price)}</span>' if st.session_state.get("show_prices", True) and cafe.price else ""
    status_html = ""
    if cafe.is_open is not None:
        status_html = '<span class="place-status is-open">Open now</span>' if cafe.is_open else '<span class="place-status is-closed">Closed</span>'
    location = cafe.location or cafe.address
    location_html = f'<span>&#128205; {html.escape(location)}</span>' if location else ""
    description_html = f'<p>{html.escape(cafe.description)}</p>' if cafe.description else ""

    st.markdown(
        f"""
        <section class="details-hero image-details-hero">
            <div class="details-hero-copy">
                <div class="search-eyebrow">{html.escape(cafe.category)}</div>
                <h1>{html.escape(cafe.name)}</h1>
                {description_html}
                <div class="details-meta">
                    {rating_html}
                    {price_html}
                    {status_html}
                    {location_html}
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
        address_html = f'<p><strong>Address:</strong> {html.escape(cafe.address)}</p>' if cafe.address else ""
        hours_html = f'<p><strong>Opening hours:</strong><br>{html.escape(cafe.opening_hours).replace(chr(10), "<br>")}</p>' if cafe.opening_hours else ""
        phone_html = f'<p><strong>Phone:</strong> <a href="tel:{html.escape(cafe.phone, quote=True)}">{html.escape(cafe.phone)}</a></p>' if cafe.phone else ""
        website_html = f'<p><strong>Website:</strong> <a href="{html.escape(cafe.website, quote=True)}" target="_blank" rel="noopener noreferrer">Visit website</a></p>' if cafe.website else ""
        amenities_html = "".join(f"<span>{html.escape(item)}</span>" for item in cafe.amenities)
        st.markdown(
            f"""
            <div class="detail-panel">
                <h3>About this place</h3>
                {address_html}
                {hours_html}
                {phone_html}
                {website_html}
                {f'<div class="amenities-list">{amenities_html}</div>' if amenities_html else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with map_col:
        render_map_view(cafe)

    intent = st.session_state.get("search_intent") or parse_search_intent(
        st.session_state.get("search_query", ""),
        st.session_state.get("search_location", ""),
        st.session_state.get("selected_category", "All"),
    )
    insights_cache = st.session_state.setdefault("cafe_ai_insights", {})
    insight_key = (cafe.id, intent.raw_query, intent.location)
    if insight_key not in insights_cache:
        recommendations, ai_status = get_ai_recommendations(
            [cafe], intent, enabled=st.session_state.get("enable_ai_recommendations", True)
        )
        why = recommendations[0]["reason"] if recommendations else "There is not enough verified information for a personalized match."
        vibe = get_ai_vibe(cafe)
        insights_cache[insight_key] = (why, vibe, ai_status)
    why, vibe, ai_status = insights_cache[insight_key]
    st.markdown(
        f"""
        <section class="detail-panel ai-insight-panel">
            <div class="search-eyebrow">PERSONALIZED MATCH</div>
            <h3>Why you may like this place</h3>
            <p>{html.escape(why)}</p>
            <small>{html.escape(ai_status)}</small>
            <h3>AI-generated vibe inference</h3>
            <p>{html.escape(vibe)}</p>
            <small>Inferred from verified listing text and review excerpts; not a verified amenity or fact.</small>
        </section>
        """,
        unsafe_allow_html=True,
    )

    review_heading = f"Reviews{f' ({cafe.review_count:,})' if cafe.review_count is not None else ''}"
    st.markdown(f'<div class="search-section-label filter-label">{review_heading}</div>', unsafe_allow_html=True)
    reviews = get_reviews(cafe)
    if reviews:
        for index, review in enumerate(reviews):
            render_review_card(review, f"review_{cafe.id}_{index}")
    else:
        st.markdown(
            """
            <div class="empty-state small-empty">
                <h3>No reviews yet</h3>
                <p>No review excerpts were supplied by the place provider.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
