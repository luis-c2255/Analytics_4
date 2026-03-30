import streamlit as st
from utils.theme import Components


st.set_page_config(
        page_title=f"Multiple Dataset Analysis",
        page_icon= "📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    Components.page_header("📊 Multiple Dataset Analysis"), unsafe_allow_html=True
)

with st.container(height="content", width="stretch", horizontal_alignment="center"):    
    st.image("utils/1.svg")
   
col1,  col2, col3 = st.columns(3)
with col1:
    st.link_button("Global Movie Trends (2026)",
    "https:",
    icon="📽️", icon_position="left", width="stretch"
    )
with col2:
    st.link_button("Supply Chain Data",
    "https:",
    icon="🚚", icon_position="left", width="stretch"
    )
with col3:
    st.link_button("Hospital Patient Readmission",
    "https:",
    icon="🏥", icon_position="left", width="stretch"
    )
col4, col5, col6, col7 = st.columns(4)
with col4:
    st.link_button("Global Population per Country",
    "https:",
    icon="🌎", icon_position="left", width="stretch"
    )
with col5:
    st.link_button("Amazon Sales Dataset",
    "https:",
    icon="🛒", icon_position="left", width="stretch"
    )
with col6:
    st.link_button("Global Suicide Rates",
    "https:",
    icon="☠️", icon_position="left", width="stretch"
    )
with col7:
    st.link_button("Spam Email Detection",
    "https:",
    icon="📧", icon_position="left", width="stretch"
    )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>📊 Multiple Analysis Dashboard</strong></p>
    <p>Multiple Dashboards from several datasets analyzed</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)
