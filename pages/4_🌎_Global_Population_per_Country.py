import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.theme import Components, Colors, init_page

init_page("Global Population per Country 1950-2024 Analysis", "🌎")

try:
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown(
    Components.page_header("🌎  Global Population per Country 1950-2024 Analysis"), unsafe_allow_html=True
)

@st.cache_data
def load_data():
    df = pd.read_csv("global_population_country.csv")
    
    # convert 'year' to integer
    df['year'] = df['year'].astype(int)
    # ensure population is numeric, coercing error to Nan
    df['population'] = pd.to_numeric(df['population'], errors='coerce')
    df.dropna(subset=['population'], inplace=True)
    df.drop_duplicates(subset=['country', 'year'], inplace=True)
    return df

df = load_data()

# sidebar filters
st.sidebar.header('Filter Options')

# Year Slider
min_year = int(df['year'].min())
max_year = int(df['year'].max())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)
# Country Multi-select
all_countries = sorted(df['country'].unique())
selected_countries = st.sidebar.multiselect(
    "Select Countries (for detailed view)",
    all_countries,
    default=['China', 'India', 'United States', 'Indonesia'] # Example defaults
)
# Apply year filter
df_filtered_year = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]

# --- Main Metrics Section (Visible on all tabs) ---
st.subheader(":rainbow[Key Global Metrics]", divider="rainbow")

latest_year_data = df_filtered_year[df_filtered_year['year'] == df_filtered_year['year'].max()]
previous_year_for_delta = df_filtered_year['year'].max() - 10
if previous_year_for_delta < df_filtered_year['year'].min():
    previous_year_for_delta = df_filtered_year['year'].min()
previous_year_data = df_filtered_year[df_filtered_year['year'] == previous_year_for_delta]

col1, col2, col3 = st.columns(3)
with col1:
    total_pop_latest = latest_year_data['population'].sum()
    total_pop_previous = previous_year_data['population'].sum() if not previous_year_data.empty else 0
    delta_pop_percent = ((total_pop_latest - total_pop_previous) / total_pop_previous * 100) if total_pop_previous else 0
    st.markdown(
        Components.metric_card(
            title=f"Global Pop. ({latest_year_data['year'].max()})",
            value=f"{total_pop_latest:,.0f}",
            delta=f"{'+' if delta_pop_percent > 0 else ''}{delta_pop_percent:,.1f}% (vs {previous_year_for_delta})",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    start_pop_growth = df_filtered_year[df_filtered_year['year'] == selected_years[0]].set_index('country')['population']
    end_pop_growth = df_filtered_year[df_filtered_year['year'] == selected_years[1]].set_index('country')['population']
    pop_change_analysis = pd.DataFrame({
    'start_pop': start_pop_growth,
    'end_pop': end_pop_growth
}).dropna()
    if not pop_change_analysis.empty:
        pop_change_analysis['percentage_change'] = ((pop_change_analysis['end_pop'] - pop_change_analysis['start_pop']) / pop_change_analysis['start_pop']) * 100
        fastest_growth_country = pop_change_analysis.sort_values(by='percentage_change', ascending=False).iloc[0]
    st.markdown(
        Components.metric_card(
            title=f"Highest % Growth ({selected_years[0]}-{selected_years[1]})",
            value=f"{fastest_growth_country.name}",
            delta=f"{fastest_growth_country['percentage_change']:,.1f}%",
            card_type="success"
        ), unsafe_allow_html=True
    )
with col3:
    num_countries_latest = latest_year_data['country'].nunique()
    num_countries_previous = previous_year_data['country'].nunique() if not previous_year_data.empty else 0
    delta_countries = num_countries_latest - num_countries_previous
    st.markdown(
        Components.metric_card(
            title="Countries with Data",
            value=f"{num_countries_latest:,}",
            delta=f"{'+' if delta_countries > 0 else ''}{delta_countries:,} (vs {previous_year_for_delta})",
            card_type="info"
        ), unsafe_allow_html=True
    )
st.markdown("   ")
st.subheader(":blue[Population Trends]", divider="blue")
st.markdown("   ")
if 'World' in selected_countries:
    global_pop_trend = df_filtered_year[df_filtered_year['country'] == 'World']
    fig_global_pop = px.line(
            global_pop_trend,
            x='year',
            y='population',
            title='Global Population Trend (from "World" entry)',
            labels={'year': 'Year', 'population': 'Population'},
            hover_data={'population': ':,.0f'}
        )
else:
    global_pop_trend = df_filtered_year[df_filtered_year['country'] != 'World'].groupby('year')['population'].sum().reset_index()
    fig_global_pop = px.line(
            global_pop_trend,
            x='year',
            y='population',
            title='Global Population Trend (Sum of Countries)',
            labels={'year': 'Year', 'population': 'Population'},
            hover_data={'population': ':,.0f'}
    )
    fig_global_pop.update_traces(mode='lines+markers')
    st.plotly_chart(fig_global_pop, width="stretch")
    st.markdown("   ")
if selected_countries:
    df_selected_countries_plot = df_filtered_year[df_filtered_year['country'].isin(selected_countries)]
    fig_country_pop = px.line(
            df_selected_countries_plot,
            x='year',
            y='population',
            color='country',
            title='Population Trend by Country',
            labels={'year': 'Year', 'population': 'Population'},
            hover_data={'population': ':,.0f'},
            height=500
        )
    fig_country_pop.update_traces(mode='lines+markers')
    st.plotly_chart(fig_country_pop, width="stretch")
else:
    st.info("Please select countries in the sidebar to see their population trends.")
    st.markdown("   ")
    
st.subheader(":red[Distribution & Absolute Growth]", divider="red")
st.markdown("   ")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Median Pop. (Year End)",
            value=f"{df_filtered_year['population'].median():,.0f}",
            delta="",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Top Populated Country",
            value=f"{latest_year_data.loc[latest_year_data['population'].idxmax()]['country']}",
            delta="",
            card_type="success"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Bottom Populated Country",
            value=f"{latest_year_data.loc[latest_year_data['population'].idxmin()]['country']}",
            delta="",
            card_type="warning"
        ), unsafe_allow_html=True
    )
st.markdown("   ")
year_for_bar = st.slider(
        "Select Year for Top Population Chart",
        min_value=selected_years[0],
        max_value=selected_years[1],
        value=selected_years[1],
        key="year_for_bar_top_pop"
    )
df_year_for_bar = df[ (df['year'] == year_for_bar) & (df['country'] != 'World') ].sort_values(by='population', ascending=False).head(15)
fig_top_pop = px.bar(
        df_year_for_bar,
        x='population',
        y='country',
        orientation='h',
        title=f'Top 15 Countries by Population ({year_for_bar})',
        labels={'population': 'Population', 'country': 'Country'},
        hover_data={'population': ':,.0f'},
        height=500
    )
fig_top_pop.update_yaxes(categoryorder='total ascending')
st.plotly_chart(fig_top_pop, width="stretch")
st.markdown("   ")

start_year_pop_abs = df_filtered_year[df_filtered_year['year'] == selected_years[0]].set_index('country')['population']
end_year_pop_abs = df_filtered_year[df_filtered_year['year'] == selected_years[1]].set_index('country')['population']

# Merge to calculate growth
pop_change_abs = pd.DataFrame({
    'start_pop': start_year_pop_abs,
    'end_pop': end_year_pop_abs
}).dropna()

if not pop_change_abs.empty:
    pop_change_abs['absolute_change'] = pop_change_abs['end_pop'] - pop_change_abs['start_pop']
    pop_change_abs = pop_change_abs[pop_change_abs.index != 'World'].sort_values(by='absolute_change', ascending=False).reset_index()

    st.write(f"Absolute population change from {selected_years[0]} to {selected_years[1]}.")
    num_countries_growth_abs = st.slider("Number of Countries to Display (Absolute Change)", 5, 50, 15, key="num_countries_abs_growth")

    # Top Growth Countries (Absolute)
    st.markdown(f"Top {num_countries_growth_abs} Countries by Absolute Population Increase")
    fig_growth_abs = px.bar(
        pop_change_abs.head(num_countries_growth_abs),
        x='absolute_change',
        y='country',
        orientation='h',
        title=f'Top Countries by Population Increase ({selected_years[0]}-{selected_years[1]})',
        labels={'absolute_change': 'Absolute Population Change', 'country': 'Country'},
        hover_data={'absolute_change': ':,.0f'},
        color_discrete_sequence=px.colors.sequential.Greens_r,
        height=500
    )
    fig_growth_abs.update_yaxes(categoryorder='total ascending')
    st.plotly_chart(fig_growth_abs, width="stretch")
    
    st.markdown(f"Top {num_countries_growth_abs} Countries by Absolute Population Decrease")
    fig_decline_abs = px.bar(
            pop_change_abs.tail(num_countries_growth_abs).sort_values(by='absolute_change', ascending=True),
            x='absolute_change',
            y='country',
            orientation='h',
            title=f'Top Countries by Population Decrease ({selected_years[0]}-{selected_years[1]})',
            labels={'absolute_change': 'Absolute Population Change', 'country': 'Country'},
            hover_data={'absolute_change': ':,.0f'},
            color_discrete_sequence=px.colors.sequential.Reds_r,
            height=500
        )
    fig_decline_abs.update_yaxes(categoryorder='total ascending')
    st.plotly_chart(fig_decline_abs, width="stretch")
else:
    st.info("Not enough data to calculate population change for the selected period.")
st.markdown("   ")
   
st.subheader(":orange[Composition & Relative Growth]", divider="orange")
st.markdown("   ")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Highest Share (Year End)",
            value="China",
            delta="-0.1% (last yr)",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Avg. % Growth (Range)",
            value=f"{pop_change_analysis['percentage_change'].mean():,.1f}%",
            delta="🟢",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Countries with Negative Growth",
            value=f"{pop_change_analysis[pop_change_analysis['percentage_change'] < 0].shape[0]}",
            delta="🔴",
            card_type="warning"
        ), unsafe_allow_html=True
    )


df_year_share = df_filtered_year[(df_filtered_year['year'] == selected_years[1]) & (df_filtered_year['country'] != 'World')]
total_pop_for_share = df_year_share['population'].sum()
df_year_share['share'] = (df_year_share['population'] / total_pop_for_share) * 100

fig_treemap = px.treemap(
            df_year_share,
            path=[px.Constant("Global"), 'country'],
            values='population',
            title=f'Global Population Share by Country ({selected_years[1]})',
            hover_data={'population': ':,.0f', 'share': ':.2f%'},
            height=600
        )
fig_treemap.update_layout(margin = dict(t=50, l=25, r=25, b=25))
st.plotly_chart(fig_treemap, width="stretch")

pop_change_analysis = pop_change_analysis[pop_change_analysis.index != 'World'].sort_values(by='percentage_change', ascending=False).reset_index()
st.write(f"Percentage population change from {selected_years[0]} to {selected_years[1]}.")
num_countries_growth_perc = st.slider("Number of Countries to Display (Percentage Change)", 5, 50, 15, key="num_countries_perc_growth")

st.markdown(f"Top {num_countries_growth_perc} Countries by Percentage Population Increase")
fig_growth_perc = px.bar(
            pop_change_analysis.head(num_countries_growth_perc),
            x='percentage_change',
            y='country',
            orientation='h',
            title=f'Top Countries by Percentage Population Increase ({selected_years[0]}-{selected_years[1]})',
            labels={'percentage_change': 'Percentage Population Change', 'country': 'Country'},
            hover_data={'percentage_change': ':.2f%'},
            color_discrete_sequence=px.colors.sequential.Greens_r,
            height=500
        )
fig_growth_perc.update_yaxes(categoryorder='total ascending')
st.plotly_chart(fig_growth_perc, width="stretch")
st.markdown("   ")

st.markdown(f"Top {num_countries_growth_perc} Countries by Percentage Population Decrease")
fig_decline_perc = px.bar(
    pop_change_analysis.tail(num_countries_growth_perc).sort_values(by='percentage_change', ascending=True),
    x='percentage_change',
    y='country',
    orientation='h',
    title=f'Top Countries by Percentage Population Decrease ({selected_years[0]}-{selected_years[1]})',
    labels={'percentage_change': 'Percentage Population Change', 'country': 'Country'},
    hover_data={'percentage_change': ':.2f%'},
    color_discrete_sequence=px.colors.sequential.Reds_r,
     height=500
)
fig_decline_perc.update_yaxes(categoryorder='total ascending')
st.plotly_chart(fig_decline_perc, width="stretch")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>🌎 Global Population per Country 1950-2024 Analysis</strong></p>
    <p>Explore key metrics, population trends, distribution, composition and growth.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)