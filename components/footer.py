import streamlit as st


def render_footer() -> None:
    st.markdown(
        """
        <footer class="brew-footer">
            <span>FindMyBrew</span>
            <span>Built for local cafe discovery.</span>
        </footer>
        """,
        unsafe_allow_html=True,
    )
