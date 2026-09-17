import html

import streamlit as st

from database.models import Cafe


def render_map_view(cafe: Cafe) -> None:
    """Render a simple map panel when coordinates are available."""

    if cafe.latitude is None or cafe.longitude is None:
        return

    st.markdown(
        f"""
        <div class="map-panel">
            <div class="map-pin">&#128205;</div>
            <div>
                <div class="map-title">Map preview</div>
                <div class="map-address">{html.escape(cafe.address)}</div>
                <div class="map-coordinates">{cafe.latitude:.4f}, {cafe.longitude:.4f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
