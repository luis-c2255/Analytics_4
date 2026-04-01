import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.theme import Components


st.set_page_config(
        page_title=f"Global Suicide Rates per Country 2000-2021 Analysis",
        page_icon= "☠️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    Components.page_header("☠️  Global Suicide Rates per Country 2000-2021 Analysis"), unsafe_allow_html=True
)

@st.cache_data
def load_data():
    df = pd.read_csv("suicide_rates_master.csv")
    
    def clean_numeric(value):
        if pd.isna(value):
            return np.nan
        return float(str(value).replace('.', ''))

    df['suicide_rate'] = df['suicide_rate'].apply(clean_numeric) / 1_000_000
    df['latitude'] = df['latitude'].apply(clean_numeric) / 1_000_000
    df['longitude'] = df['longitude'].apply(clean_numeric) / 1_000_000
    df = df.drop_duplicates()
    return df

df = load_data()
   
# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>☠️  Global Suicide Rates per Country 2000-2021 Analysis</strong></p>
    <p>Explore key metrics, population trends, distribution, composition and growth.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)