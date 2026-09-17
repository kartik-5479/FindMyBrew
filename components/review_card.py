import html

import streamlit as st


def render_review_card(review: dict[str, str], key_prefix: str = "review") -> None:
    """Render a single cafe review."""

    st.markdown(
        f"""
        <div class="review-card" id="{html.escape(key_prefix)}">
            <div class="review-top">
                <strong>{html.escape(review.get('author', 'Guest'))}</strong>
                <span>&#9733; {html.escape(review.get('rating', ''))}</span>
            </div>
            <p>{html.escape(review.get('text', ''))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
