import streamlit as st


def initialize_session_defaults() -> None:
    """Create stable session keys used by routing, preferences, and favorites."""

    defaults = {
        "current_page": "Home",
        "previous_page": "Home",
        "selected_cafe_id": None,
        "search_location": "",
        "search_query": "",
        "selected_category": "All",
        "favorites": set(),
        "default_location": "",
        "default_category": "All",
        "show_ratings": True,
        "show_prices": True,
        "enable_ai_recommendations": True,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, set) else value


def get_favorites() -> set[str]:
    initialize_session_defaults()
    favorites = st.session_state.get("favorites", set())
    if not isinstance(favorites, set):
        favorites = set(favorites)
        st.session_state["favorites"] = favorites
    return favorites


def is_favorite(cafe_id: str) -> bool:
    return cafe_id in get_favorites()


def add_favorite(cafe_id: str) -> None:
    favorites = get_favorites()
    favorites.add(cafe_id)
    st.session_state["favorites"] = favorites


def remove_favorite(cafe_id: str) -> None:
    favorites = get_favorites()
    favorites.discard(cafe_id)
    st.session_state["favorites"] = favorites


def toggle_favorite(cafe_id: str) -> None:
    if is_favorite(cafe_id):
        remove_favorite(cafe_id)
    else:
        add_favorite(cafe_id)
