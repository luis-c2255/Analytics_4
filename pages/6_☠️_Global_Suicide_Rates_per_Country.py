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
st.markdown("### Exploring patterns in suicide rates across countries, demographics, and time", text_alignment="center")

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

# Sidebar filters
st.sidebar.header("🔍 Filters")

year_range = st.sidebar.slider(
    "Select Year Range",
    int(df['year'].min()),
    int(df['year'].max()),
    (int(df['year'].min()), int(df['year'].max()))
)

countries = st.sidebar.multiselect(
    "Select Countries (leave empty for all)",
    options=sorted(df['country'].unique()),
    default=[]
)

sex_filter = st.sidebar.selectbox(
    "Select Sex",
    options=['All', 'male', 'female', 'both'],
    index=0
)

age_filter = st.sidebar.selectbox(
    "Select Age Group",
    options=['All'] + sorted(df['age_group'].unique().tolist()),
    index=0
)

df_filtered = df[
    (df['year'] >= year_range[0]) &
    (df['year'] <= year_range[1])
]

if countries:
    df_filtered = df_filtered[df_filtered['country'].isin(countries)]
    
if sex_filter != 'All':
    df_filtered = df_filtered[df_filtered['sex'] == sex_filter]

if age_filter != 'All':
    df_filtered = df_filtered[df_filtered['age_group'] == age_filter]
    
st.subheader("📈 :rainbow[Key Metrics]", divider="rainbow")

col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_rate = df_filtered['suicide_rate'].mean()
    st.markdown(
        Components.metric_card(
            title="Average Suicide Rate",
            value=f"{avg_rate:.2f} per 100k",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    total_countries = df_filtered['country'].nunique()
    st.markdown(
        Components.metric_card(
            title="Countries Analyzed",
            value=f"{total_countries}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    max_rate = df_filtered['suicide_rate'].max()
    st.markdown(
        Components.metric_card(
            title="Highest Rate",
            value=f"{max_rate:.2f} per 100k",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col4:
    years_covered = df_filtered['year'].nunique()
    st.markdown(
        Components.metric_card(
            title="Years of Data",
            value=f"{years_covered}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.markdown("   ")

st.subheader("🌍 :blue[Geographic Analysis]", divider="blue")
st.markdown("   ")

st.markdown("##### :blue[Geographic Distribution of Suicide Rates]")

map_data = df_filtered[df_filtered['age_group'] == 'ALL'].groupby(
    ['country', 'latitude', 'longitude', 'iso_a3']
)['suicide_rate'].mean().reset_index()

fig_map = px.scatter_geo(
    map_data,
    lat='latitude',
    lon='longitude',
    hover_name='country',
    size='suicide_rate',
    color='suicide_rate',
    color_continuous_scale='Reds',
    title='Global Suicide Rates Heat Map',
    projection='natural earth',
    size_max=30
)
fig_map.update_layout(height=500)
st.plotly_chart(fig_map, width="stretch")
st.markdown("   ")

top_countries = df_filtered[df_filtered['age_group'] == 'ALL'].groupby(['country'])['suicide_rate'].mean().sort_values(ascending=False).head(15)

fig_top = px.bar(
    x=top_countries.values,
    y=top_countries.index,
    orientation='h',
    title='Top 15 Countries by Average Suicide Rate',
    labels={'x': 'Rate per 100k', 'y': 'Country'},
    color=top_countries.values,
    color_continuous_scale='Reds'
)
fig_top.update_layout(height=500, showlegend=False)
st.plotly_chart(fig_top, width="stretch")
st.markdown("   ")

st.subheader("👥 :violet[Demographic Patterns]", divider="violet")
st.markdown("   ")

st.subheader("📅 :yellow[Temporal Trends]", divider="yellow")
st.markdown("   ")
st.subheader("🔝 :green[Rankings]", divider="green")
st.markdown("   ")
st.subheader("📊 :red[Raw Data]", divider="red")
st.markdown("   ")

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