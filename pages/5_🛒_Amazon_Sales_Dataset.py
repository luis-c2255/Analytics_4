import streamlit as st
from utils.theme import Components

st.set_page_config(
        page_title=f"Amazon Sales Dataset Analysis",
        page_icon= "🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    Components.page_header("🛒  Amazon Sales Dataset Analysis"), unsafe_allow_html=True
)

