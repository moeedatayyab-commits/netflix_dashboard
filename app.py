import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Netflix Dashboard",
                   page_icon="🎬", layout="wide")

# ── Title ─────────────────────────────────────────────────────
st.title("🎬 Netflix Content Dashboard")
st.markdown("**Exploratory Data Analysis — by Moeeda Khan**")

# ── Load data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df = df.fillna({
        'director': 'Unknown',
        'cast': 'Unknown',
        'country': 'Unknown',
        'rating': 'Not Rated',
        'duration': 'Unknown'
    })
    df = df.dropna(subset=['date_added'])
    df['date_added'] = pd.to_datetime(df['date_added'].str.strip())
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month
    return df

df = load_data()

# ── Sidebar Filters ───────────────────────────────────────────
st.sidebar.header("🔍 Filters")

type_options = ["All"] + list(df['type'].unique())
selected_type = st.sidebar.selectbox("Content Type", type_options)

country_options = ["All"] + list(df['country'].value_counts().head(20).index)
selected_country = st.sidebar.selectbox("Country", country_options)

rating_options = ["All"] + list(df['rating'].unique())
selected_rating = st.sidebar.selectbox("Age Rating", rating_options)

min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())
year_range = st.sidebar.slider("Release Year Range",
                                min_year, max_year,
                                (2000, max_year))

search = st.sidebar.text_input("Search Title")

if st.sidebar.button("🔄 Reset Filters"):
    st.rerun()

# ── Apply Filters ─────────────────────────────────────────────
filtered_df = df.copy()
if selected_type != "All":
    filtered_df = filtered_df[filtered_df['type'] == selected_type]
if selected_country != "All":
    filtered_df = filtered_df[filtered_df['country'] == selected_country]
if selected_rating != "All":
    filtered_df = filtered_df[filtered_df['rating'] == selected_rating]
filtered_df = filtered_df[
    (filtered_df['release_year'] >= year_range[0]) &
    (filtered_df['release_year'] <= year_range[1])
]
if search:
    filtered_df = filtered_df[
        filtered_df['title'].str.contains(search, case=False, na=False)
    ]

# ── KPI Cards ─────────────────────────────────────────────────
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Titles", len(filtered_df))
col2.metric("Movies", len(filtered_df[filtered_df['type'] == 'Movie']))
col3.metric("TV Shows", len(filtered_df[filtered_df['type'] == 'TV Show']))
col4.metric("Countries", filtered_df['country'].nunique())

st.markdown("---")

# ── Charts Row 1 ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # Chart 1 — Pie Chart
    st.subheader("Movies vs TV Shows")
    fig = px.pie(filtered_df, names='type',
                 color_discrete_sequence=['#E50914', '#221F1F'])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Chart 2 — Bar Chart
    st.subheader("Top 10 Countries")
    top_countries = filtered_df['country'].value_counts().head(10).reset_index()
    top_countries.columns = ['country', 'count']
    fig = px.bar(top_countries, x='country', y='count',
                 color_discrete_sequence=['#E50914'])
    st.plotly_chart(fig, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # Chart 3 — Histogram
    st.subheader("Release Year Distribution")
    fig = px.histogram(filtered_df, x='release_year', nbins=30,
                       color_discrete_sequence=['#E50914'])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Chart 4 — Line Chart
    st.subheader("Content Added Per Year")
    content_per_year = filtered_df['year_added'].value_counts().sort_index().reset_index()
    content_per_year.columns = ['year', 'count']
    fig = px.line(content_per_year, x='year', y='count',
                  markers=True, color_discrete_sequence=['#E50914'])
    st.plotly_chart(fig, use_container_width=True)

# ── Charts Row 3 ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # Chart 5 — Count Plot
    st.subheader("Content by Age Rating")
    rating_counts = filtered_df['rating'].value_counts().reset_index()
    rating_counts.columns = ['rating', 'count']
    fig = px.bar(rating_counts, x='rating', y='count',
                 color_discrete_sequence=['#E50914'])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Chart 6 — Box Plot
    st.subheader("Release Year by Type")
    fig = px.box(filtered_df, x='type', y='release_year',
                 color='type',
                 color_discrete_sequence=['#E50914', '#221F1F'])
    st.plotly_chart(fig, use_container_width=True)

# ── Charts Row 4 ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # Chart 7 — Heatmap
    st.subheader("Correlation Heatmap")
    numeric_df = filtered_df[['release_year', 'year_added', 'month_added']]
    corr = numeric_df.corr().round(2)
    fig = px.imshow(corr, text_auto=True, color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Chart 8 — Area Chart
    st.subheader("Cumulative Content Growth")
    cumulative = filtered_df['year_added'].value_counts().sort_index().cumsum().reset_index()
    cumulative.columns = ['year', 'total']
    fig = px.area(cumulative, x='year', y='total',
                  color_discrete_sequence=['#E50914'])
    st.plotly_chart(fig, use_container_width=True)

# ── Charts Row 5 ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # Chart 9 — Scatter Plot
    st.subheader("Release Year vs Year Added")
    fig = px.scatter(filtered_df, x='release_year', y='year_added',
                     color='type',
                     color_discrete_sequence=['#E50914', '#221F1F'],
                     opacity=0.4)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Chart 10 — Violin Plot
    st.subheader("Release Year Distribution by Type")
    fig = px.violin(filtered_df, x='type', y='release_year',
                    color='type',
                    color_discrete_sequence=['#E50914', '#221F1F'])
    st.plotly_chart(fig, use_container_width=True)

# ── Data Table ────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Filtered Data Table")
st.dataframe(filtered_df[['title', 'type', 'country',
                           'release_year', 'rating',
                           'listed_in']].reset_index(drop=True))
