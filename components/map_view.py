import html

import streamlit as st

from database.models import Cafe
from services.maps_service import coordinates_label, has_coordinates


def render_map_view(cafe: Cafe) -> None:
    """Render verified address and coordinate details when supplied."""

    address = cafe.address or cafe.location
    if not has_coordinates(cafe):
        st.markdown(
            f"""
            <div class="map-panel">
                <div class="map-pin">&#128205;</div>
                <div>
                    <div class="map-title">Location</div>
                    <div class="map-address">{html.escape(address) if address else "No verified address was supplied."}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if cafe.directions_url:
            st.link_button("Get directions", cafe.directions_url, use_container_width=True)
        return

    st.markdown(
        f"""
        <div class="map-panel">
            <div class="map-pin">&#128205;</div>
            <div>
                <div class="map-title">Location</div>
                <div class="map-address">{html.escape(address)}</div>
                <div class="map-coordinates">{html.escape(coordinates_label(cafe))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if cafe.directions_url:
        st.link_button("Get directions", cafe.directions_url, use_container_width=True)
