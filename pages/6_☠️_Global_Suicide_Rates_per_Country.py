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
    
    def strip_dots(value):
        if pd.isna(value):
            return np.nan
        return float(str(value).replace('.', ''))
    def normalize_to_range(raw, low, high):
        """Find the right power-of-10 divisor so the value falls in [low, high]"""
        if pd.isna(raw) or raw == 0:
            return raw
        for exp in range(25):
            result = raw / (10 ** exp)
            if low <= result <= high:
                return result
        return np.nan
    
    df['suicide_rate'] = df['suicide_rate'].apply(strip_dots).apply(lambda x: normalize_to_range(x, 0, 500))
    df['latitude'] = df['latitude'].apply(strip_dots).apply(lambda x: normalize_to_range(x, -90, 90))
    df['longitude'] = df['longitude'].apply(strip_dots).apply(lambda x: normalize_to_range(x, -180, 180))
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
    ['country', 'iso_a3']
)['suicide_rate'].mean().reset_index()

fig_map = px.choropleth(
    map_data,
    locations='iso_a3',
    hover_name='country',
    color='suicide_rate',
    color_continuous_scale='Reds',
    title='Global Suicide Rates Heat Map',
    projection='natural earth',
    labels={'suicide_rate': 'Rate per 100k'}
)
fig_map.update_layout(height=700, geo=dict(showframe=False, showcoastlines=True))
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
fig_top.update_layout(height=700, showlegend=False, xaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_top, width="stretch")
st.markdown("   ")

st.subheader("👥 :violet[Demographic Patterns]", divider="violet")
st.markdown("   ")

sex_data = df_filtered[
    (df_filtered['age_group'] == 'ALL') &
    (df_filtered['sex'].isin(['male', 'female']))
].groupby('sex')['suicide_rate'].mean().reset_index()

fig_sex = px.bar(
    sex_data,
    x='sex',
    y='suicide_rate',
    title='Average Suicide Rate by Sex',
    labels={'suicide_rate': 'Rate per 100k', 'sex': 'Sex'},
    text_auto=True,
    color='sex',
    color_discrete_map={'male': '#3498db', 'female': '#e74c3c'}
)
fig_sex.update_layout(showlegend=False)
st.plotly_chart(fig_sex, width="stretch")
st.markdown("   ")

if len(sex_data) == 2:
    male_rate = sex_data[sex_data['sex'] == 'male']['suicide_rate'].values[0]
    female_rate = sex_data[sex_data['sex'] == 'female']['suicide_rate'].values[0]
    ratio = male_rate / female_rate if female_rate > 0 else 0
    st.info(f"💡 Insight: Female suicide rate is {ratio:.1f}x higher than female rate")
st.markdown("   ")

   # Age group analysis
age_data = df_filtered[df_filtered['sex'] == 'both'].groupby('age_group')['suicide_rate'].mean().sort_values(ascending=False).reset_index()

fig_age = px.bar(
    age_data,
    x='age_group',
    y='suicide_rate',
    title='Suicide Rates by Age Group',
    labels={'suicide_rate': 'Rate per 100k', 'age_group': 'Age Group'},
    text_auto=True,
    color='suicide_rate',
    color_continuous_scale='Oranges'
)
fig_age.update_layout(showlegend=False)
st.plotly_chart(fig_age, width="stretch")

# Most vulnerable age group
if len(age_data) > 0:
    most_vulnerable = age_data.iloc[0]
    st.warning(f"⚠️ Most Vulnerable: Age group {most_vulnerable['age_group']} with rate of {most_vulnerable['suicide_rate']:.2f} per 100k")
    
# Heatmap: Sex vs Age Group
st.markdown("##### :violet[Sex vs Age Group Heatmap]")

heatmap_data = df_filtered[df_filtered['sex'].isin(['male', 'female'])].pivot_table(
    values='suicide_rate',
    index='age_group',
    columns='sex',
    aggfunc='mean'
)
fig_heatmap = px.imshow(
    heatmap_data,
    title='Suicide Rates: Sex vs Age Group',
    labels={'x': 'Sex', 'y': 'Age Group', 'color': 'Rate per 100k'},
    color_continuous_scale='RdYlBu_r',
    aspect='auto'
)
st.plotly_chart(fig_heatmap, width="stretch")
st.markdown("   ")

st.subheader("📅 :yellow[Temporal Trends]", divider="yellow")
st.markdown("   ")

yearly_trend = df_filtered[df_filtered['age_group'] == 'ALL'].groupby('year')['suicide_rate'].mean().reset_index()

fig_trend = px.line(
    yearly_trend,
    x='year',
    y='suicide_rate',
    title='Global Average Suicide Rate Over Time',
    labels={'suicide_rate': 'Rate per 100k', 'year': 'Year'},
    markers=True
)
fig_trend.update_traces(line_color='#e74c3c', line_width=3)
st.plotly_chart(fig_trend, width="stretch")

st.markdown("   ")
st.markdown("##### :violet[Trends by Sex]")

sex_yearly = df_filtered[(df_filtered['age_group'] == 'ALL') &
(df_filtered['sex'].isin(['male', 'female']))].groupby(['year', 'sex'])['suicide_rate'].mean().reset_index()

fig_sex_trend = px.line(
    sex_yearly,
    x='year',
    y='suicide_rate',
    color='sex',
    title='Suicide Rate Trends by Sex',
    labels={'suicide_rate': 'Rate per 100k', 'year': 'Year'},
    color_discrete_map={'male': '#3498db', 'female': '#e74c3c'}
)
st.plotly_chart(fig_sex_trend, width="stretch")
st.markdown("   ")

# Country comparison (if countries selected)
if countries:
    st.markdown("##### :violet[Selected Countries Comparison Over Time]")
    country_trends = df_filtered[df_filtered['age_group'] == 'ALL'].groupby(['year', 'country'])['suicide_rate'].mean().reset_index()
    fig_country_trends = px.line(
        country_trends,
        x='year',
        y='suicide_rate',
        color='country',
        title='Suicide Rate Trends by Selected Countries',
        labels={'suicide_rate': 'Rate per 100k', 'year': 'Year'},
        markers=True
    )
    st.plotly_chart(fig_country_trends, width="stretch")
else:
    st.info("💡 Select specific countries in the sidebar to compare their trends")

st.subheader("🔝 :green[Country Rankings]", divider="green")
st.markdown("   ")
col1, col2 = st.columns(2)
with col1:
    st.markdown("🔴 :green[Highest Suicide Rates]")
    top_20 = df_filtered[df_filtered['age_group'] == 'ALL'].groupby('country')['suicide_rate'].mean().sort_values(ascending=False).head(20).reset_index()
    top_20.index = range(1, len(top_20) + 1)
    top_20.columns = ['Country', 'Rate per 100k']
    top_20['Rate per 100k'] = top_20['Rate per 100k'].round(2)

    st.dataframe(top_20, width="stretch", height=600)

with col2:
    st.markdown("🟢 :green[Lowest Suicide Rates]")
    bottom_20 = df_filtered[df_filtered['age_group'] == 'ALL'].groupby('country')['suicide_rate'].mean().sort_values(ascending=True).head(20).reset_index()
    bottom_20.index = range(1, len(bottom_20) + 1)
    bottom_20.columns = ['Country', 'Rate per 100k']
    bottom_20['Rate per 100k'] = bottom_20['Rate per 100k'].round(2)
    
    st.dataframe(bottom_20, width="stretch", height=600)

# Regional comparison
st.markdown("##### :green[Regional Patterns]")
st.markdown("*Countries grouped by latitude regions*")

df_regional = df_filtered[df_filtered['age_group'] == 'ALL'].copy()
df_regional['region'] = pd.cut(
    df_regional['latitude'],
    bins=[-90, -23.5, 23.5, 90],
    labels=['Southern Hemisphere', 'Tropical', 'Northern Hemisphere']
)

regional_rates = df_regional.groupby('region')['suicide_rate'].mean().reset_index()

fig_regional = px.bar(
    regional_rates,
    x='region',
    y='suicide_rate',
    title='Average Suicide Rates by Geographic Region',
    labels={'suicide_rate': 'Rate per 100k', 'region': 'Region'},
    color='suicide_rate',
    color_continuous_scale='Viridis'
)
st.plotly_chart(fig_regional, width="stretch")
st.markdown("   ")

st.subheader("📊 :red[Filtered Raw Data]", divider="red")
st.markdown("   ")
st.markdown(f":red[Total Records: {len(df_filtered):,}]")

# Display options
col1, col2 = st.columns([3, 1])
with col1:
    search_country = st.text_input("🔍 Search by country name", "")
with col2:
    rows_to_show = st.selectbox("Rows per page", [10, 25, 50, 100, 500], index=2)
    
# Apply search
df_display = df_filtered.copy()
if search_country:
    df_display = df_display[df_display['country'].str.contains(search_country, case=False, na=False)]
    
# Sort options
sort_col = st.selectbox(
    "Sort by column",
    options=df_display.columns.tolist(),
    index=df_display.columns.tolist().index('suicide_rate')
)
sort_order = st.radio("Sort order", ['Descending', 'Ascending'], horizontal=True)

df_display = df_display.sort_values(
    by=sort_col,
    ascending=(sort_order == 'Ascending')
).head(rows_to_show)

# Format the display
df_display_formatted = df_display.copy()
df_display_formatted['suicide_rate'] = df_display_formatted['suicide_rate'].round(2)
df_display_formatted['latitude'] = df_display_formatted['latitude'].round(4)
df_display_formatted['longitude'] = df_display_formatted['longitude'].round(4)

st.dataframe(df_display_formatted, width="stretch", height=600)

st.markdown("#####📥 :red[Download Data]")

csv = df_filtered.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name=f"suicide_rates-filtered_{year_range[0]}_{year_range[1]}.csv",
    mime='text/csv'
)
st.markdown("   ")

st.subheader("🔑 :yellow[Key Takeaways]")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 👥 :violet[Demographics]")
    male_avg = df_filtered[(df_filtered['sex'] == 'male') & (df_filtered['age_group'] == 'ALL')]['suicide_rate'].mean()
    female_avg = df_filtered[(df_filtered['sex'] == 'female') & (df_filtered['age_group'] == 'ALL')]['suicide_rate'].mean()
    
    if not pd.isna(male_avg) and not pd.isna(female_avg):
        st.metric("Male Rate", f"{male_avg:.2f} per 100k")
        st.metric("Female Rate", f"{female_avg:.2f} per 100k")
        st.metric("Gender Gap", f"{(male_avg - female_avg):.2f}")
        
with col2:
    st.markdown("### 🌍 :green[Geographic]")
    if len(df_filtered) > 0:
        highest_country_data = df_filtered[df_filtered['age_group'] == 'ALL'].groupby('country')['suicide_rate'].mean().sort_values(ascending=False)
    if len(highest_country_data) > 0:
        highest_country = highest_country_data.index[0]
        highest_rate = highest_country_data.values[0]
        st.metric("Highest Rate Country", highest_country)
        st.metric("Rate", f"{highest_rate:.2f} per 100k")

with col3:
    st.markdown("### 📅 :blue[Temporal]")
    if len(yearly_trend) > 1:
        first_year_rate = yearly_trend.iloc[0]['suicide_rate']
        last_year_rate = yearly_trend.iloc[-1]['suicide_rate']
        change = last_year_rate - first_year_rate
        pct_change = (change / first_year_rate * 100) if first_year_rate > 0 else 0
        st.metric("Rate Change", f"{change:+.2f} per 100k", f"{pct_change:+.1f}%")
        st.metric("First Year", f"{first_year_rate:.2f} per 100k")
        st.metric("Last Year", f"{last_year_rate:.2f} per 100k")
        
st.markdown("   ")
st.subheader("💡 :orange[Analytical Insights]")

insights_col1, insights_col2 = st.columns(2)

with insights_col1:
    st.markdown("### :red[Risk Factors Identified]")
    if len(df_filtered) > 0:
        age_vulnerability = df_filtered[df_filtered['sex'] == 'both'].groupby('age_group')['suicide_rate'].mean().sort_values(ascending=False)
    if len(age_vulnerability) > 0:
        st.write(f"🎯 Most Vulnerable Age Group: {age_vulnerability.index[0]} ({age_vulnerability.values[0]:.2f} per 100k)")
    if not pd.isna(male_avg) and not pd.isna(female_avg) and female_avg > 0:
        gender_ratio = male_avg / female_avg
        st.write(f"⚖️ Gender Disparity: Males are {gender_ratio:.1f}x more likely")
        

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