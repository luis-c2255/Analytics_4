import streamlit as st
import pandas as pd
import plotly.express as px
import ast # For literal_eval
import numpy as np # For numerical operations
from utils.theme import Components

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    df = pd.read_csv("global_movie_trends.csv")
    
    if df.columns[0].startswith('Unnamed'):
        df = df.iloc[:, 1:]
        
    # Convert release date to datetime and extract year
    df['release_date'] = pd.to_datetime(df["release_date"], errors='coerce')
    df["release_year"] = df["release_date"].dt.year
    
    # Handle genre_ids: convert string representation of list to actual list, then explode
    df['genre_ids'] = df["genre_ids"].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
    
    # Add a simple mapping to genre
    genre_mapping = {
        18: 'Drama', 80: 'Crime', 36: 'Historical', 10752: 'War', 16: 'Animation', 10751: 'Family', 37: 'Western',
        28: 'Action', 53: 'Thriller', 35: 'Comedy', 10749: 'Romance', 12: 'Adventure', 878: 'Science Fiction', 99: 'Documentary',
        27: 'Horror', 10402: 'Music', 9648: 'Mystery', 10770: 'TV Movie'
    }
    
    # Create a primary_genre column for the original df
    df['primary_genre'] = df['genre_ids'].apply(lambda x: genre_mapping.get(x[0], 'Unknown') if x else 'No Genre')
    
    # Explode genre_ids for genre_based analysis
    temp_df = df.copy()
    temp_df['genre_id'] = temp_df['genre_ids']
    df_exploded_genres = temp_df.explode('genre_id')
    df_exploded_genres['genre_name'] = df_exploded_genres['genre_id'].map(genre_mapping)
    df_exploded_genres.fillna({'genre_name': 'Unknown'}, inplace=True)
    
    # Drop rows with missing crucial values after processing
    df.dropna(subset=['title', 'release_year', 'popularity', 'vote_average', 'vote_count'], inplace=True)
    df_exploded_genres.dropna(subset=['title', 'release_year', 'popularity', 'vote_average', 'vote_count', 'genre_name'], inplace=True)
    
    # Remove duplicate movie entries based on id
    df.drop_duplicates(subset=['id'], inplace=True)
    df_exploded_genres.drop_duplicates(subset=['id', 'genre_name'], inplace=True)
    
    return df, df_exploded_genres, genre_mapping

# Load data
df, df_exploded_genres, genre_mapping = load_data()

st.title("📽️ :blue[Global Movie Trends (2026) Analysis]", text_alignment="center")
st.markdown("""
            Explore key metrics, trends, and distribution of movies based on popularity, vote average, genres, and languages.
            This expanded dashboard includes detailed categorical analysis for deeper insights.
            """, text_alignment="center")
# Sidebar filters
st.sidebar.header("Filter Options")

# Year Range Slider
min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())
selected_years = st.sidebar.slider(
    "Select Release Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Language Multi-Select
all_languages = sorted(df['original_language'].unique().tolist())
selected_languages = st.sidebar.multiselect(
    "Select Original Languages",
    options=all_languages,
    default=all_languages[:min(5, len(all_languages))]
)

# Genre Multi-Select
all_genres = sorted(df_exploded_genres['genre_name'].unique().tolist())
selected_genres = st.sidebar.multiselect(
    "Select Genres",
    options=all_genres,
    default=all_genres[:min(5, len(all_genres))]
)

# Apply filters
filtered_df = df[
    (df['release_year'] >= selected_years[0]) &
    (df['release_year'] <= selected_years[1]) &
    (df['original_language'].isin(selected_languages)) &
    (df['primary_genre'].isin(selected_genres))
]

# Further fitler for genres on exploded df
filtered_df_exploded_genres = df_exploded_genres[
    (df_exploded_genres['release_year'] >= selected_years[0]) &
    (df_exploded_genres['release_year'] <= selected_years[1]) &
    (df_exploded_genres['original_language'].isin(selected_languages)) &
    (df_exploded_genres['genre_name'].isin(selected_genres))
]

# Handle cases where filters result empty dataframes
if filtered_df.empty or filtered_df_exploded_genres.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
    st.stop()
    
# Metrics
st.subheader(":rainbow[Key Metrics]", divider="rainbow")

# calculate metrics for the filtered data
total_movies = filtered_df['id'].nunique()
avg_vote_average = filtered_df['vote_average'].mean()
avg_popularity = filtered_df['popularity'].mean()
avg_vote_count = filtered_df['vote_count'].mean()

# calculate delta
overall_total_movies = df['id'].nunique()
overall_avg_vote_average = df['vote_average'].mean()
overall_avg_popularity = df['popularity'].mean()

delta_total_movies = f"{int(total_movies - overall_avg_vote_average):+}"
delta_avg_vote = f"{(avg_vote_average - overall_avg_vote_average) / overall_avg_vote_average * 100:.1f}%"
delta_avg_pop = f"{(avg_popularity - overall_avg_popularity) / overall_avg_popularity * 100:.1f}%"

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        Components.metric_card(
            title="Total Movies",
            value=f"{total_movies:,}",
            delta=f"{delta_total_movies}",
            card_type="info"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Avg Vote Score",
            value=f"{avg_vote_average:.2f}",
            delta=f"{delta_avg_vote}",
            card_type="success"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Avg Popularity",
            value=f"{avg_popularity:.1f}",
            delta=f"{delta_avg_pop}",
            card_type="success"
        ), unsafe_allow_html=True
    )
st.markdown("   ")

st.subheader(":blue[Overview & Distributions]", divider="blue")
st.markdown("   ")
lang_counts = filtered_df['original_language'].value_counts().head(10).reset_index()
lang_counts.columns = ['Language', 'Count']
fig_lang_count = px.bar(
    lang_counts,
    x='Count',
    y='Language',
    orientation='h',
    title='Top 10 Languages by Movie Count',
    labels={'Count': 'Number of Movies', 'Language': 'Original Language'},
    color='Count',
    color_continuous_scale=px.colors.sequential.Viridis
)
fig_lang_count.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig_lang_count, width="stretch")
st.markdown("   ")

genre_counts = filtered_df_exploded_genres['genre_name'].value_counts().head(10).reset_index()
genre_counts.columns = ['Genre', 'Count']
fig_genre_count = px.bar(
    genre_counts,
    x='Count',
    y='Genre',
    orientation='h',
    title='Top 10 Genres by Movie Count',
    labels={'Count': 'Number of Movies', 'Genre': 'Movie Genre'},
    color='Count',
    color_continuous_scale=px.colors.sequential.Plasma
)
fig_genre_count.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig_genre_count, width="stretch")
st.markdown("   ")

fig_vote_dist = px.histogram(
    filtered_df,
    x='vote_average',
    nbins=20,
    title='Distribution of Movie Vote Average',
    labels={'vote_average': 'Vote Average'},
    color_discrete_sequence=['#0083B8']
)
fig_vote_dist.update_layout(xaxis_title="Vote Average", yaxis_title="Number of Movies")
st.plotly_chart(fig_vote_dist, width="stretch")
st.markdown("   ")
fig_pop_dist = px.histogram(
    filtered_df,
    x='popularity',
    nbins=20,
    title='Distribution of Movie Popularity',
    labels={'popularity': 'Popularity Score'},
    color_discrete_sequence=['#ff97ff']
)
fig_pop_dist.update_layout(xaxis_title='Popularity Score', yaxis_title='Number of Movies')
st.plotly_chart(fig_pop_dist, width="stretch")
st.markdown("   ")
st.subheader(":green[Trends Over Time]", divider="green")
st.markdown("   ")

st.subheader(":orange[Relationships]", divider="orange")
st.markdown("   ")

st.subheader(":violet[Detailed Category Analysis]", divider="violet")
st.markdown("   ")


# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>📽️ Global Movie Trends (2026) Analysis</strong></p>
    <p>Explore key metrics, trends, and distribution of movies based on popularity, vote average, genres, and languages.</p>
    <p style='font-size: 0.9rem;'>Navigate using the sidebar to explore different datasets</p>
</div>
""", unsafe_allow_html=True)