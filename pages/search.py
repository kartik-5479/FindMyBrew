import html

import streamlit as st

from components.cafe_card import render_cafe_card
from components.filter_panel import render_filter_panel
from services.gemini_service import get_ai_recommendations
from services.places_service import discover_cafes
from services.recommendation_service import hydrate_recommendations


def _sync_search_state(location: str, query: str) -> None:
    st.session_state["search_location"] = location.strip()
    st.session_state["search_query"] = query.strip()


def render_search() -> None:
    """Render the FindMyBrew cafe discovery page."""

    st.markdown(
        """
        <div class="search-header">
            <div class="search-eyebrow">FIND YOUR BREW</div>
            <h1 class="search-title">Discover your next <span>favorite cafe.</span></h1>
            <p class="search-description">
                Search by city, sector, landmark, or natural language, like quiet coffee shop in Patiala.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="search-section-label">&#128205; Location</div>', unsafe_allow_html=True)
    location_col, button_col = st.columns([3.5, 1], gap="medium")

    with location_col:
        location = st.text_input(
            "Location",
            value=st.session_state.get("search_location", ""),
            placeholder="City, town, sector, area, or landmark...",
            label_visibility="collapsed",
            key="search_location_input",
        ) or ""
    with button_col:
        search_clicked = st.button("Search Cafes", type="primary", use_container_width=True, key="search_cafes_button")

    st.markdown('<div class="search-section-label">Natural-language search</div>', unsafe_allow_html=True)
    query = st.text_input(
        "Natural-language search",
        value=st.session_state.get("search_query", ""),
        placeholder="Example: quiet cafe for studying, cheap coffee near me, late night lounge...",
        label_visibility="collapsed",
        key="search_query_input",
    ) or ""

    if search_clicked:
        _sync_search_state(location, query)
        st.rerun()

    render_filter_panel("search")

    current_location = st.session_state.get("search_location", "")
    current_query = st.session_state.get("search_query", "")
    current_category = st.session_state.get("selected_category", "All")
    signature = (current_query, current_location, current_category)

    if st.session_state.get("search_signature") != signature:
        with st.spinner("Searching verified places..."):
            intent, search_result = discover_cafes(current_query, current_location, current_category)
        st.session_state["search_signature"] = signature
        st.session_state["search_intent"] = intent
        st.session_state["search_result"] = search_result

    intent = st.session_state.get("search_intent")
    search_result = st.session_state.get("search_result")
    if intent is None or search_result is None:
        intent, search_result = discover_cafes(current_query, current_location, current_category)
        st.session_state["search_signature"] = signature
        st.session_state["search_intent"] = intent
        st.session_state["search_result"] = search_result
    results = search_result.cafes or search_result.alternatives

    sort_options = ["Relevance", "Rating", "Name"]
    if any(cafe.distance_meters is not None for cafe in results):
        sort_options.append("Distance")
    sort_col, open_col = st.columns([1, 2], gap="medium")
    with sort_col:
        sort_by = st.selectbox("Sort by", sort_options, key="search_sort_by")
    with open_col:
        show_open_only = st.checkbox(
            "Open now",
            disabled=not any(cafe.is_open is not None for cafe in results),
            key="search_open_only",
        )
    if show_open_only:
        results = [cafe for cafe in results if cafe.is_open is True]
    if sort_by == "Rating":
        results = sorted(results, key=lambda cafe: cafe.rating or 0, reverse=True)
    elif sort_by == "Name":
        results = sorted(results, key=lambda cafe: cafe.name.casefold())
    elif sort_by == "Distance":
        results = sorted(results, key=lambda cafe: cafe.distance_meters if cafe.distance_meters is not None else float("inf"))

    heading_source = current_location or intent.location or current_query or "Popular places"
    heading = html.escape(heading_source)
    eyebrow = "PLACES FOUND" if search_result.exact_location else "SEARCH RESULTS"
    category_suffix = "" if intent.category == "All" else f" in {html.escape(intent.category)}"

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

    if search_result.message:
        st.info(search_result.message)

    if not results:
        st.markdown(
            """
            <div class="empty-state">
                <h3>No places found</h3>
                <p>Try a nearby neighborhood, landmark, or broader location. Search results are only shown when verified by a connected place provider.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    recommendations, ai_status = get_ai_recommendations(
        results,
        intent,
        enabled=st.session_state.get("enable_ai_recommendations", True),
    )
    ai_picks = hydrate_recommendations(results, recommendations)
    if ai_picks:
        st.markdown(
            f"""
            <section class="ai-picks">
                <div class="search-eyebrow">PERSONALIZED PICKS</div>
                    <h2>Recommended from verified place information</h2>
                <p>{html.escape(ai_status)}</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        for cafe, reason in ai_picks[:4]:
            st.markdown(
                f"""
                <div class="ai-pick-row">
                    <strong>{html.escape(cafe.name)}</strong>
                    <span>{html.escape(reason)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    card_columns = st.columns(2, gap="medium")
    for index, cafe in enumerate(results):
        with card_columns[index % 2]:
            render_cafe_card(
                cafe,
                key_prefix="search",
                show_ratings=st.session_state.get("show_ratings", True),
                show_prices=st.session_state.get("show_prices", True),
            )
