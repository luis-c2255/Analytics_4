import streamlit as st
import pandas as pd
import plotly.express as px
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
    for col in ['suicide_rate', 'latitude', 'longitude', 'year']:
        df[col] = df[col].astype(str).str.replace(',', '.')
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['suicide_rate', 'latitude', 'longitude', 'year'])
    df = df.drop_duplicates()
    df['year'] = df['year'].astype(int)
    return df

df = load_data()
st.write(f"Rows loaded: {len(df)}")

st.sidebar.header("Filter Options")

all_countries = sorted(df['country'].unique())
selected_countries = st.sidebar.multiselect("Select Country(s)", all_countries, default=all_countries)

if not df.empty and df['year'].notna().any():
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
else:
    min_year, max_year = 2000, 2021

year_range = st.sidebar.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

all_sex = df['sex'].unique()
selected_sex = st.sidebar.multiselect("Select Sex", all_sex, default=all_sex)

all_age_groups = sorted(df['age_group'].unique())
selected_age_groups = st.sidebar.multiselect("Select Age Group(s)", all_age_groups, default=all_age_groups)

filtered_df = df [
    (df['country'].isin(selected_countries)) &
    (df['year'] >= year_range[0]) &
    (df['year'] <= year_range[1]) &
    (df['sex'].isin(selected_sex)) &
    (df['age_group'].isin(selected_age_groups))
]
st.write(f"Displaying data for {len(selected_countries)} countries, {len(selected_age_groups)} age groups, and years {year_range[0]} - {year_range[1]}.")

st.header(":rainbow[Overview & Trends]", divider="rainbow", text_alignment="center")
st.markdown("   ")

st.subheader(":yellow[Key Metrics]")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Total Countries",
            value=f"{filtered_df['country'].nunique()}",
            delta="+5",
            card_type="success"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Avg Suicide Rate",
            value=f"{round(filtered_df['suicide_rate'].mean(), 2)}",
            delta="+0.5",
            card_type="warning"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Max Suicide Rate",
            value=f"{round(filtered_df['suicide_rate'].max(), 2)}",
            delta="-2%",
            card_type="error"
        ), unsafe_allow_html=True
    )

st.markdown("   ")
st.subheader(":yellow[Average Suicide Rate Over Time]")
avg_rate_over_time = filtered_df.groupby('year')['suicide_rate'].mean().reset_index()

fig_time_series = px.line (
    avg_rate_over_time,
    x='year',
    y='suicide_rate',
    title='Average Suicide Rate Over Time',
    labels={'suicide_rate': 'Average Suicide Rate (per 100k)'}
    )
st.plotly_chart(fig_time_series, width="stretch")
st.markdown("   ")

st.subheader(":yellow[Suicide Rate by Sex and Age Group]")
avg_rate_sex_age = filtered_df.groupby(['sex', 'age_group'])['suicide_rate'].mean().reset_index()

fig_sex_age = px.bar(
    avg_rate_sex_age,
    x='age_group',
    y='suicide_rate',
    color='sex',
    barmode='group',
    text_auto=True,
    title="Average Suicide Rate by Sex and Age Group",
    labels={'suicide_rate': 'Average Suicide Rate (per 100k)'}
)
st.plotly_chart(fig_sex_age, width="stretch")
st.markdown("   ")

st.header(":blue[Geographical Analysis]", divider="blue", text_alignment="center")
st.markdown("   ")

st.subheader(":blue[Key Metrics]")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Total Records",
            value=f"{len(filtered_df)}",
            delta="+1000",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Countries in View",
            value=f"{filtered_df['country'].nunique()}",
            delta="+5",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Avg Lat/Lon",
            value=f"{round(filtered_df['latitude'].mean(), 2)} / {round(filtered_df['longitude'].mean(), 2)}",
            delta="0.1%",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.markdown("   ")
st.subheader(":blue[Average Suicide Rate by Country (Geographical Map)]")

country_map_data = filtered_df.groupby('country').agg(
    {'latitude': 'first', 'longitude': 'first', 'suicide_rate': 'mean'}
).reset_index()

fig_geo = px.scatter_mapbox(
    country_map_data,
    lat='latitude', lon='longitude',
    color='suicide_rate',
    size='suicide_rate',
    hover_name='country',
    color_continuous_scale=px.colors.cyclical.IceFire,
    zoom=1,
    title="Average Suicide Rate by Country",
    labels={'suicide_rate': 'Avg Suicide Rate (per 100k)'}
)
fig_geo.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_geo, width="stretch")
st.markdown("   ")

st.subheader(":blue[Top 10 Countries by Average Suicide Rate]")

top_10_countries = filtered_df.groupby('country')['suicide_rate'].mean().nlargest(10).reset_index()
fig_top_countries = px.bar(
    top_10_countries,
    x='suicide_rate',
    y='country',
    orientation='h',
    title='Top 10 Countries by Average Suicide Rate',
    labels={'suicide_rate': 'Average Suicide Rate (per 100k)'}
)
st.plotly_chart(fig_top_countries, width="stretch")
st.markdown("   ")

st.header(":orange[Distributions & Group Comparisons]", divider="orange", text_alignment="center")
st.markdown("   ")

st.subheader(":orange[Key Metrics]")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Median Rate",
            value=f"{round(filtered_df['suicide_rate'].median(), 2)}",
            delta="+0.01",
            card_type="success"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Std Dev Rate",
            value=f"{round(filtered_df['suicide_rate'].std(), 2)}",
            delta="-0.2",
            card_type="warning"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Dominant Age Group",
            value=f"{filtered_df['age_group'].mode()[0]}",
            delta="No change",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.markdown("   ")

st.subheader(":orange[Distribution of Suicide Rates]")
fig_hist = px.histogram(
    filtered_df,
    x='suicide_rate',
    nbins=50,
    title="Distribution of Suicide Rates (per 100k)",
    labels={'suicide_rate': 'Suicide Rate (per 100k)'}
)
st.plotly_chart(fig_hist, width="stretch")
st.markdown("   ")

st.subheader(":orange[Suicide Rate Distribution by Age Group]")

fig_box = px.box(
    filtered_df,
    x='age_group',
    y='suicide_rate',
    color='sex',
    title="Suicide Rate Distribution by Age Group and Sex",
    labels={'suicide_rate': 'Suicide Rate (per 100k)'}
)
st.plotly_chart(fig_box, width="stretch")
st.markdown("   ")

st.subheader(":orange[Proportional Suicide Rate by Age Group Over Time]")

rate_by_age_year = filtered_df.groupby(['year', 'age_group'])['suicide_rate'].sum().reset_index()

fig_area = px.area(
    rate_by_age_year,
    x='year',
    y='suicide_rate',
    color='age_group',
    title="Proportional Suicide Rate by Age Group Over Time",
    labels={'suicide_rate': 'Total Suicide Rate (per 100k)', 'age_group': 'Age Group'}
)
st.plotly_chart(fig_area, width="stretch")
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