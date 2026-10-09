import streamlit as st

from services.places_service import CATEGORIES


def render_settings() -> None:
    """Render the FindMyBrew settings page."""

    st.markdown(
        """
        <div class="search-header">
            <div class="search-eyebrow">PREFERENCES</div>
            <h1 class="search-title">App <span>settings.</span></h1>
            <p class="search-description">
                Customize your default search behavior, card details, and AI recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<div class="search-section-label">Search defaults</div>', unsafe_allow_html=True)

        st.session_state["default_location"] = (
            st.text_input(
                "Default location",
                value=st.session_state.get("default_location", ""),
                placeholder="Example: Chandigarh",
                key="settings_default_location_input",
            )
            or ""
        ).strip()

        current_category = st.session_state.get("default_category", "All")
        category_index = CATEGORIES.index(current_category) if current_category in CATEGORIES else 0
        st.session_state["default_category"] = st.selectbox(
            "Default category",
            CATEGORIES,
            index=category_index,
            key="settings_default_category_input",
        )

        st.markdown('<div class="search-section-label filter-label">Card display</div>', unsafe_allow_html=True)
        st.session_state["show_ratings"] = st.checkbox(
            "Show ratings",
            value=st.session_state.get("show_ratings", True),
            key="settings_show_ratings_input",
        )
        st.session_state["show_prices"] = st.checkbox(
            "Show prices",
            value=st.session_state.get("show_prices", True),
            key="settings_show_prices_input",
        )

        st.markdown('<div class="search-section-label filter-label">AI recommendations</div>', unsafe_allow_html=True)
        st.session_state["enable_ai_recommendations"] = st.checkbox(
            "Enable AI recommendations",
            value=st.session_state.get("enable_ai_recommendations", True),
            key="settings_enable_ai_input",
        )

        reset_col, search_col = st.columns([1, 1], gap="small")
        with reset_col:
            if st.button("Reset settings", key="settings_reset", use_container_width=True):
                st.session_state["default_location"] = ""
                st.session_state["default_category"] = "All"
                st.session_state["show_ratings"] = True
                st.session_state["show_prices"] = True
                st.session_state["enable_ai_recommendations"] = True
                for widget_key in (
                    "settings_default_location_input",
                    "settings_default_category_input",
                    "settings_show_ratings_input",
                    "settings_show_prices_input",
                    "settings_enable_ai_input",
                ):
                    st.session_state.pop(widget_key, None)
                st.rerun()
        with search_col:
            if st.button("Use defaults in Search", key="settings_apply_search", type="primary", use_container_width=True):
                st.session_state["search_location"] = st.session_state.get("default_location", "")
                st.session_state["search_query"] = ""
                st.session_state["selected_category"] = st.session_state.get("default_category", "All")
                st.session_state["current_page"] = "Search"
                st.rerun()

        st.success("Settings saved automatically. Favorites are kept separately.")
