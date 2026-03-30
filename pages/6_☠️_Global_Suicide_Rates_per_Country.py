import streamlit as st
from utils.theme import Components, Colors, init_page

init_page("Global Suicide Rates per Country 2000-2021 Analysis", "☠️")

try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    Components.page_header("☠️  Global Suicide Rates per Country 2000-2021 Analysis"), unsafe_allow_html=True
)

