import streamlit as st
from utils.theme import Components, Colors, init_page

init_page("Spam Email Detection Analysis", "📧")

try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    Components.page_header("📧  Spam Email Detection Analysis"), unsafe_allow_html=True
)

