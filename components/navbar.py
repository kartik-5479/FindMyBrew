import streamlit as st


NAV_PAGES = (
    ("Home", "Home"),
    ("Search", "Search"),
    ("Favorites", "Favorites"),
    ("Settings", "Settings"),
)


def render_navbar(active_page: str = "Home", on_navigate=None) -> None:
    """Render the FindMyBrew navigation bar once."""

    st.markdown(
        """
        <div class="brew-navbar-brand">
            <span class="brew-brand-icon">&#9749;</span>
            <span class="brew-brand-name">FindMyBrew</span>
        </div>
        <div class="brew-navbar-divider"></div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(len(NAV_PAGES), gap="medium")
    for index, (page_name, label) in enumerate(NAV_PAGES):
        with columns[index]:
            button_type = "primary" if page_name == active_page else "secondary"
            if st.button(
                label,
                key=f"navbar_{page_name.lower()}",
                type=button_type,
                use_container_width=True,
            ):
                if on_navigate is not None:
                    on_navigate(page_name)
                st.rerun()
