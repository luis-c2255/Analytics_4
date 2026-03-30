import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    df = pd.read_csv("global_suicide_rates.csv")
    df['year'] = df['year'].astype(int)
    df['suicide_rate'] = df['suicide_rate'].astype(float)
    df.dropna(subset=['suicide_rate'], inplace=True)
    return df
df = load_data()

df_filtered_demographics = df[(df['age_group'] != 'ALL') & (df['sex'] != 'both')]
df_global_trends = df[(df['sex'] == 'both') & (df['age_group'] == 'ALL')]

st.sidebar.header("Filter Options")
all_countries = ["All"] + sorted(df['country'].unique().tolist())
all_sexes = ["Both"] + sorted(df['sex'].unique().tolist())
all_age_groups = ["All"] + sorted(df['age_group'].unique().tolist())
min_year, max_year = int(df['year'].min()), int(df['year'].max())

selected_country = st.sidebar.selectbox("Select Country", all_countries)
year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))
selected_sex = st.sidebar.selectbox("Select Sex", all_sexes)
selected_age_group = st.sidebar.selectbox("Select Age Group", all_age_groups)

filtered_df = df.copy()
if selected_country != "All":
    filtered_df = filtered_df[filtered_df['country'] == selected_country]
filtered_df = filtered_df[(filtered_df['year'] >= year_range[0]) & (filtered_df['year'] <= year_range[1])]
if selected_sex != "Both":
    filtered_df = filtered_df[filtered_df['sex'] == selected_sex.lower()]
if selected_age_group != "All":
    filtered_df = filtered_df[filtered_df['age_group'] == selected_age_group]
    
st.subheader(":rainbow[Key Metrics]", divider="rainbow")
def compute_delta(current, previous, fmt="{:.2f}"):
    if pd.isna(current) or pd.isna(previous):
        return "N/A", "info"

    delta = current - previous
    delta_str = fmt.format(delta)

    # Generic card type logic
    if delta > 0:
        card = "error"
    elif delta < 0:
        card = "success"
    else:
        card = "info"

    return delta_str, card

def safe_mean(df, col):
    return df[col].mean() if not df.empty else float("nan")

metrics = []

if filtered_df.empty:
    metrics = [
        {"title": "Overall Avg. Suicide Rate", "value": "N/A", "delta": "N/A", "card_type": "info"},
        {"title": "Highest Single Rate Observed", "value": "N/A", "delta": "N/A", "card_type": "error"},
        {"title": "Top Avg. Country Rate", "value": "N/A", "delta": "N/A", "card_type": "warning"},
        {"title": "Gender Suicide Rate Gap", "value": "N/A", "delta": "N/A", "card_type": "info"},
    ]
else:
    # --- 1. Overall Average Suicide Rate ---
    overall_avg = safe_mean(filtered_df, "suicide_rate")

    latest = filtered_df[filtered_df["year"] == filtered_df["year"].max()]
    prev = filtered_df[filtered_df["year"] == filtered_df["year"].max() - 1]

    delta_avg, card_avg = compute_delta(
        safe_mean(latest, "suicide_rate"),
        safe_mean(prev, "suicide_rate")
    )

    metrics.append({
        "title": "Overall Avg. Suicide Rate",
        "value": f"{overall_avg:.2f}",
        "delta": delta_avg,
        "card_type": card_avg
    })

    # --- 2. Highest Single Rate Observed ---
    max_rate = filtered_df["suicide_rate"].max()
    metrics.append({
        "title": "Highest Single Rate",
        "value": f"{max_rate:.2f}",
        "delta": "Absolute Peak",
        "card_type": "info"
    })

    # --- 3. Top Avg. Country Rate ---
    if selected_country == "All":
        country_means = df_global_trends.groupby("country")["suicide_rate"].mean()
        top_country = country_means.idxmax()
        top_rate = country_means.max()

        global_avg = df_global_trends["suicide_rate"].mean()
        delta_pct = ((top_rate - global_avg) / global_avg) * 100 if global_avg > 0 else float("nan")

        metrics.append({
            "title": "Top Avg. Country Rate",
            "value": f"{top_country}: {top_rate:.2f}",
            "delta": f"{delta_pct:+.1f}% vs Global Avg" if not pd.isna(delta_pct) else "N/A",
            "card_type": "info" if delta_pct > 20 else "warning"
        })
    else:
        country_avg = safe_mean(filtered_df, "suicide_rate")
        prev_avg = safe_mean(
            df[(df["country"] == selected_country) & (df["year"] == filtered_df["year"].max() - 1)],
            "suicide_rate"
        )

        delta_country, card_country = compute_delta(country_avg, prev_avg)

        metrics.append({
            "title": f"Avg. Rate in {selected_country}",
            "value": f"{country_avg:.2f}",
            "delta": delta_country,
            "card_type": card_country
        })

    # --- 4. Gender Suicide Rate Gap ---
    male = safe_mean(filtered_df[filtered_df["sex"] == "male"], "suicide_rate")
    female = safe_mean(filtered_df[filtered_df["sex"] == "female"], "suicide_rate")

    if pd.isna(male) or pd.isna(female):
        gender_value = "N/A"
        gender_type = "info"
    else:
        if male > female:
            pct = ((male - female) / female) * 100 if female > 0 else float("nan")
            gender_value = f"{pct:.1f}% (Male > Female)"
            gender_type = "info" if pct > 50 else "warning"
        else:
            pct = ((female - male) / male) * 100 if male > 0 else float("nan")
            gender_value = f"{pct:.1f}% (Female > Male)"
            gender_type = "warning" if pct > 50 else "success"

    metrics.append({
        "title": "Gender Suicide Rate Gap",
        "value": gender_value,
        "delta": "Comparison",
        "card_type": gender_type
    })
cols = st.columns(len(metrics))

for col, m in zip(cols, metrics):
    with col:
        st.markdown(
            Components.metric_card(
                title=m["title"],
                value=m["value"],
                delta=m["delta"],
                card_type=m["card_type"]
            ), unsafe_allow_html=True
        )        

st.subheader("📊 :green[Overview & Trends]", divider="green")
st.markdown("   ")

global_yearly_avg = df_global_trends.groupby('year')['suicide_rate'].mean().reset_index()

fig_global_trend = px.line(
            global_yearly_avg.sort_values('year'),
            x='year',
            y='suicide_rate',
            title='Global Average Suicide Rate Over Time (All Ages, Both Sexes)',
            labels={'year': 'Year', 'suicide_rate': 'Suicide Rate (per 100k)'},
            markers=True
        )
st.plotly_chart(fig_global_trend, width="stretch")
st.markdown("   ")

fig_hist = px.histogram(
            filtered_df,
            x='suicide_rate',
            nbins=50,
            title='Distribution of Suicide Rates Across All Records',
            labels={'suicide_rate': 'Suicide Rate (per 100k)', 'count': 'Number of Records'},
            color_discrete_sequence=['#1f77b4']
        )
st.plotly_chart(fig_hist, width="stretch")

st.subheader("👤 :violet[Demographic Breakdown]", divider="violet")
st.markdown("   ")

avg_rate_by_sex_data = filtered_df[filtered_df['age_group'] == 'ALL'].groupby('sex')['suicide_rate'].mean().reset_index()
fig_sex = px.bar(
                avg_rate_by_sex_data,
                x='sex',
                y='suicide_rate',
                title='Average Suicide Rate by Sex',
                labels={'sex': 'Sex', 'suicide_rate': 'Average Suicide Rate (per 100k)'},
                color='sex',
                color_discrete_map={'male': '#636efa', 'female': '#ef553b', 'both': '#00cc96'} # Custom colors
            )
st.plotly_chart(fig_sex, width="stretch")
st.markdown("   ")
df_filtered_demographics_for_charts = df[(df['age_group'] != 'ALL') & (df['sex'] != 'both')]
age_group_order = ['5-14', '15-24', '25-34', '35-54', '55-74', '75+']
df_filtered_demographics_for_charts['age_group'] = pd.Categorical(
            df_filtered_demographics_for_charts['age_group'], categories=age_group_order, ordered=True
        )
fig_violin_sex = px.violin(
            df_filtered_demographics_for_charts,
            y='suicide_rate',
            x='sex',
            color='sex',
            box=True, # show box plots inside violins
            points='outliers', # show actual outlier points
            title='Suicide Rate Distribution by Sex (Excluding "ALL" Age Group)',
            labels={'sex': 'Sex', 'suicide_rate': 'Suicide Rate (per 100k)'}
        )
st.plotly_chart(fig_violin_sex, width="stretch")
st.markdown("   ")
avg_rate_by_age_data = filtered_df[(filtered_df['sex'] != 'both') & (filtered_df['age_group'] != 'ALL')]
avg_rate_by_age_data = avg_rate_by_age_data.groupby('age_group')['suicide_rate'].mean().reset_index()
age_group_order = ['5-14', '15-24', '25-34', '35-54', '55-74', '75+']
avg_rate_by_age_data['age_group'] = pd.Categorical(avg_rate_by_age_data['age_group'], categories=age_group_order, ordered=True)
avg_rate_by_age_data.sort_values('age_group', inplace=True)

fig_age = px.bar(
                avg_rate_by_age_data,
                x='age_group',
                y='suicide_rate',
                title='Average Suicide Rate by Age Group',
                labels={'age_group': 'Age Group', 'suicide_rate': 'Average Suicide Rate (per 100k)'},
                color='age_group',
            )
st.plotly_chart(fig_age, width="stretch")
st.markdown("   ")
df_filtered_demographics_for_charts = df[(df['age_group'] != 'ALL') & (df['sex'] != 'both')]
df_filtered_demographics_for_charts['age_group'] = pd.Categorical(
            df_filtered_demographics_for_charts['age_group'], categories=age_group_order, ordered=True
        )
fig_violin_age = px.violin(
            df_filtered_demographics_for_charts.sort_values('age_group'),
            y='suicide_rate',
            x='age_group',
            color='age_group',
            box=True,
            points='outliers',
            title='Suicide Rate Distribution by Age Group (Excluding "ALL" Sex)',
            labels={'age_group': 'Age Group', 'suicide_rate': 'Suicide Rate (per 100k)'}
        )
st.plotly_chart(fig_violin_age, width="stretch")
st.markdown("   ")

st.subheader("🗺️ :blue[Country Comparison]", divider="blue")
st.markdown("   ")
country_avg_rates_all = df_global_trends.groupby('country')['suicide_rate'].mean().sort_values(ascending=False).reset_index()
top_n_countries = country_avg_rates_all.head(20)

fig_top_countries = px.bar(
                top_n_countries,
                x='suicide_rate',
                y='country',
                orientation='h',
                title='Top 20 Countries by Average Suicide Rate (All Ages, Both Sexes)',
                labels={'suicide_rate': 'Average Suicide Rate (per 100k)', 'country': 'Country'},
                color='suicide_rate', # Color by rate
                color_continuous_scale=px.colors.sequential.Plasma
            )
fig_top_countries.update_layout(yaxis={'categoryorder':'total ascending'}) # Make highest bar at top
st.plotly_chart(fig_top_countries, width="stretch")
st.markdown("   ")

country_detailed_trend = filtered_df[(filtered_df['country'] == selected_country) & (filtered_df['age_group'] != 'ALL')]
fig_country_trend = px.line(
                country_detailed_trend.sort_values('year'),
                x='year',
                y='suicide_rate',
                color='sex',
                line_dash='age_group', # Differentiate by age_group
                title=f'Suicide Rate Trend in {selected_country} by Sex and Age Group',
                labels={'year': 'Year', 'suicide_rate': 'Suicide Rate (per 100k)', 'sex': 'Sex', 'age_group': 'Age Group'}
            )
st.plotly_chart(fig_country_trend, width="stretch")
st.markdown("   ")

pivot_df = df_global_trends.pivot_table(index='country', columns='year', values='suicide_rate')
country_overall_avg = df_global_trends.groupby('country')['suicide_rate'].mean().sort_values(ascending=False)
top_countries_for_heatmap = country_overall_avg.head(25).index.tolist() # Top 25 countries
pivot_df_final = pivot_df.loc[pivot_df.index.intersection(top_countries_for_heatmap)]
pivot_df_final = pivot_df_final.reindex(index=top_countries_for_heatmap)

fig_heatmap = px.heatmap(
                    pivot_df_final,
                    title='Suicide Rate Heatmap by Country and Year (Top Countries, All Ages, Both Sexes)',
                    labels={'country': 'Country', 'year': 'Year', 'value': 'Suicide Rate (per 100k)'},
                    color_continuous_scale=px.colors.sequential.Plasma # Good for showing intensity
                )
st.plotly_chart(fig_heatmap, width="stretch")
st.markdown("   ")
treemap_data = df_filtered_demographics_for_charts.groupby(['country', 'age_group'])['suicide_rate'].mean().reset_index()
top_countries_for_treemap = treemap_data.groupby('country')['suicide_rate'].mean().nlargest(15).index
treemap_data_filtered = treemap_data[treemap_data['country'].isin(top_countries_for_treemap)]

fig_treemap = px.treemap(
                treemap_data_filtered,
                path=[px.Constant("Global Average Rate"), 'country', 'age_group'],
                values='suicide_rate',
                color='suicide_rate',
                color_continuous_scale='RdYlBu_r', # Red-Yellow-Blue reversed, higher rates are red
                title='Hierarchical Average Suicide Rate by Country and Age Group (Top 15 Countries)'
            )
st.plotly_chart(fig_treemap, width="stretch")
st.markdown("   ")

st.subheader("🌍 :orange[Geospatial Insights]", divider="orange")

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