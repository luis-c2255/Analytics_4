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
        "title": "Highest Single Rate Observed",
        "value": f"{max_rate:.2f}",
        "delta": "Absolute Peak",
        "card_type": "error"
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
            "card_type": "error" if delta_pct > 20 else "warning"
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
            gender_type = "error" if pct > 50 else "warning"
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
            ),
            unsafe_allow_html=True
        )
