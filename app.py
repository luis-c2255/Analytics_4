import streamlit as st
from utils.theme import Components

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title(":green[Multiple Dataset Analysis]", text_alignment="center")

with st.container(height="content", width="stretch", horizontal_alignment="center"):    
    st.image("utils/image.svg")
   
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
    st.link_button("Global Population per Country 1950-2024",
    "https:",
    icon="🌎", icon_position="left", width="stretch"
    )
with col5:
    st.link_button("Amazon Sales Dataset",
    "https:",
    icon="🛒", icon_position="left", width="stretch"
    )
with col6:
    st.link_button("Global Suicide Rates per Country 2000-2021",
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
