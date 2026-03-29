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
            delta_positive=True,
            card_type="success"
        ), unsafe_allow_html=True
    )
with col2:
    st.markdown(
        Components.metric_card(
            title="Avg Vote Score",
            value=f"{avg_vote_average:.2f}",
            delta=f"{delta_avg_vote}",
            delta_positive=True,
            card_type="success"
        ), unsafe_allow_html=True
    )
with col3:
    st.markdown(
        Components.metric_card(
            title="Avg Popularity",
            value=f"{avg_popularity:.1f}",
            delta=f"{delta_avg_pop}",
            delta_positive=True,
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

trend_df = filtered_df.groupby('release_year').agg(
    avg_popularity=('popularity', 'mean'),
    avg_vote_average=('vote_average', 'mean'),
    movie_count=('id', 'nunique')
).reset_index()

fig_pop_trend = px.line(
    trend_df,
    x='release_year',
    y='avg_popularity',
    title='Average Movie Popularity by Release Year',
    labels={'avg_popularity': 'Average Popularity', 'release_year': 'Release Year'},
    markers=True,
    line_shape='spline',
    color_discrete_sequence=['#FFA07A']
)
st.plotly_chart(fig_pop_trend, width="stretch")
st.markdown("   ")

fig_vote_trend = px.line(
        trend_df,
        x='release_year',
        y='avg_vote_average',
        title='Average Vote Average by Release Year',
        labels={'avg_vote_average': 'Average Vote Average', 'release_year': 'Release Year'},
        markers=True,
        line_shape="spline",
        color_discrete_sequence=['#20B2AA']
    )
st.plotly_chart(fig_vote_trend, width="stretch")
st.markdown("   ")

fig_movie_count_trend = px.area(
        trend_df,
        x='release_year',
        y='movie_count',
        title='Number of Unique Movies Released by Year',
        labels={'movie_count': 'Number of Movies', 'release_year': 'Release Year'},
        color_discrete_sequence=['#ADD8E6'],
        line_shape="spline"
    )
st.plotly_chart(fig_movie_count_trend, width="stretch")
st.markdown("   ")

st.subheader(":orange[Relationships & Correlations]", divider="orange")
st.markdown("   ")
st.markdown("Explore the relationship between a movie's popularity and its average vote score.", text_alignment="center")

fig_scatter_pop_vote = px.scatter(
        filtered_df,
        x='popularity',
        y='vote_average',
        size='vote_count', # Use vote_count to represent reliability of vote_average
        color='original_language',
        hover_name='title',
        title='Popularity vs. Vote Average by Original Language',
        labels={'popularity': 'Popularity Score', 'vote_average': 'Vote Average'},
        height=600,
        log_x=True, # Popularity can have a wide range, log scale helps
        template="plotly_white"
    )
st.plotly_chart(fig_scatter_pop_vote, width="stretch")
st.markdown("   ")
st.markdown("This plot shows the relationship, with points colored by the primary genre.",  text_alignment="center")

fig_scatter_pop_vote_genre = px.scatter(
        filtered_df, # Use filtered_df as it now has 'primary_genre'
        x='popularity',
        y='vote_average',
        size='vote_count',
        color='primary_genre',
        hover_name='title',
        title='Popularity vs. Vote Average by Primary Genre',
        labels={'popularity': 'Popularity Score', 'vote_average': 'Vote Average'},
        height=600,
        log_x=True,
        template="plotly_white"
    )
st.plotly_chart(fig_scatter_pop_vote_genre, width="stretch")
st.markdown("   ")

st.subheader(":violet[Detailed Category Analysis]", divider="violet")
st.markdown("   ")
fig_box_pop_genre = px.box(
            filtered_df_exploded_genres,
            x='popularity',
            y='genre_name',
            orientation='h',
            title='Popularity Distribution by Genre',
            labels={'popularity': 'Popularity Score', 'genre_name': 'Genre'},
            color='genre_name',
            height=600
        )
fig_box_pop_genre.update_layout(yaxis={'categoryorder':'mean ascending'})
st.plotly_chart(fig_box_pop_genre,  width="stretch")
st.markdown("   ")

fig_box_vote_genre = px.box(
            filtered_df_exploded_genres,
            x='vote_average',
            y='genre_name',
            orientation='h',
            title='Vote Average Distribution by Genre',
            labels={'vote_average': 'Vote Average', 'genre_name': 'Genre'},
            color='genre_name',
            height=600
        )
fig_box_vote_genre.update_layout(yaxis={'categoryorder':'mean ascending'})
st.plotly_chart(fig_box_vote_genre, width="stretch")
st.markdown("   ")

fig_box_pop_lang = px.box(
            filtered_df,
            x='popularity',
            y='original_language',
            orientation='h',
            title='Popularity Distribution by Language',
            labels={'popularity': 'Popularity Score', 'original_language': 'Language'},
            color='original_language',
            height=600
        )
fig_box_pop_lang.update_layout(yaxis={'categoryorder':'mean ascending'})
st.plotly_chart(fig_box_pop_lang, width="stretch")
st.markdown("   ")

fig_box_vote_lang = px.box(
            filtered_df,
            x='vote_average',
            y='original_language',
            orientation='h',
            title='Vote Average Distribution by Language',
            labels={'vote_average': 'Vote Average', 'original_language': 'Language'},
            color='original_language',
            height=600
        )
fig_box_vote_lang.update_layout(yaxis={'categoryorder':'mean ascending'})
st.plotly_chart(fig_box_vote_lang, width="stretch")
st.markdown("   ")

min_vote_count_threshold = 5000 # Adjustable threshold for reliable ratings
top_movies_df = filtered_df[filtered_df['vote_count'] >= min_vote_count_threshold].copy()

if not top_movies_df.empty:
    top_popular = top_movies_df.sort_values('popularity', ascending=False).head(10)
    fig_top_popular = px.bar(
                top_popular,
                x='popularity',
                y='title',
                orientation='h',
                title='Top 10 Most Popular Movies (Filtered)',
                labels={'popularity': 'Popularity Score', 'title': 'Movie Title'},
                color='popularity',
                color_continuous_scale=px.colors.sequential.YlGnBu
            )
    fig_top_popular.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_popular, width="stretch")

    st.markdown("   ")
    top_rated = top_movies_df.sort_values('vote_average', ascending=False).head(10)
    fig_top_rated = px.bar(
                top_rated,
                x='vote_average',
                y='title',
                orientation='h',
                title='Top 10 Highest Rated Movies (Filtered)',
                labels={'vote_average': 'Vote Average', 'title': 'Movie Title'},
                color='vote_average',
                color_continuous_scale=px.colors.sequential.YlOrRd
        )
    fig_top_rated.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_rated,  width="stretch")
else:
    st.info(f"No movies meet the criteria of having at least {min_vote_count_threshold} votes within the selected filters.")
    
# Group by language and genre, count unique movies
lang_genre_composition = filtered_df_exploded_genres.groupby(['original_language', 'genre_name'])['id'].nunique().reset_index()
lang_genre_composition.columns = ['original_language', 'genre_name', 'movie_count']

fig_treemap = px.treemap(
        lang_genre_composition,
        path=[px.Constant("All Movies"), 'original_language', 'genre_name'],
        values='movie_count',
        color='movie_count',
        hover_data=['original_language', 'genre_name'],
        title='Hierarchical Composition of Movies by Language and Genre',
        height=600,
        color_continuous_scale='Rainbow'
    )
fig_treemap.update_layout(margin = dict(t=50, l=25, r=25, b=25))
st.plotly_chart(fig_treemap, width="stretch")
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