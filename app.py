import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Filter 1 - Content Type
type_options = ["All"] + list(df['type'].unique())
selected_type = st.sidebar.selectbox("Content Type", type_options)

# Filter 2 - Country
country_options = ["All"] + list(df['country'].value_counts().head(20).index)
selected_country = st.sidebar.selectbox("Country", country_options)

# Filter 3 - Rating
rating_options = ["All"] + list(df['rating'].unique())
selected_rating = st.sidebar.selectbox("Age Rating", rating_options)

# Filter 4 - Year Range
min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())
year_range = st.sidebar.slider("Release Year Range", 
                                min_year, max_year, 
                                (2000, max_year))

# Filter 5 - Search
search = st.sidebar.text_input("Search Title")

# Filter 6 - Reset button
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
    type_counts = filtered_df['type'].value_counts()
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%',
           colors=['#E50914', '#221F1F'], startangle=90)
    ax.legend()
    st.pyplot(fig)
    plt.close()

with col2:
    # Chart 2 — Bar Chart
    st.subheader("Top 10 Countries")
    top_countries = filtered_df['country'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(top_countries.index, top_countries.values, color='#E50914')
    ax.set_xlabel("Country")
    ax.set_ylabel("Number of Titles")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── Charts Row 2 ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # Chart 3 — Histogram
    st.subheader("Release Year Distribution")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(filtered_df['release_year'], bins=30, 
            color='#E50914', edgecolor='black')
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Titles")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    # Chart 4 — Line Chart
    st.subheader("Content Added Per Year")
    content_per_year = filtered_df['year_added'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(content_per_year.index, content_per_year.values,
            color='#E50914', marker='o', linewidth=2)
    ax.set_xlabel("Year")
    ax.set_ylabel("Titles Added")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── Charts Row 3 ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # Chart 5 — Count Plot
    st.subheader("Content by Age Rating")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.countplot(data=filtered_df, x='rating',
                  order=filtered_df['rating'].value_counts().index,
                  palette='Reds_r', ax=ax)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    # Chart 6 — Box Plot
    st.subheader("Release Year by Type")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=filtered_df, x='type', y='release_year',
                hue='type', palette='Reds', legend=False, ax=ax)
    ax.set_xlabel("Type")
    ax.set_ylabel("Release Year")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── Charts Row 4 ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # Chart 7 — Heatmap
    st.subheader("Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(6, 4))
    numeric_df = filtered_df[['release_year', 'year_added', 'month_added']]
    sns.heatmap(numeric_df.corr(), annot=True, 
                cmap='Reds', fmt='.2f', ax=ax)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    # Chart 8 — Area Chart
    st.subheader("Cumulative Content Growth")
    cumulative = filtered_df['year_added'].value_counts().sort_index().cumsum()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.fill_between(cumulative.index, cumulative.values,
                    color='#E50914', alpha=0.6)
    ax.plot(cumulative.index, cumulative.values, 
            color='#221F1F', linewidth=2)
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Titles")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── Charts Row 5 ──────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    # Chart 9 — Scatter Plot
    st.subheader("Release Year vs Year Added")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(filtered_df['release_year'], filtered_df['year_added'],
               color='#E50914', alpha=0.3)
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Year Added to Netflix")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    # Chart 10 — Violin Plot
    st.subheader("Release Year Distribution by Type")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.violinplot(data=filtered_df, x='type', y='release_year',
                   hue='type', palette='Reds', legend=False, ax=ax)
    ax.set_xlabel("Type")
    ax.set_ylabel("Release Year")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── Data Table ────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Filtered Data Table")
st.dataframe(filtered_df[['title', 'type', 'country', 
                           'release_year', 'rating', 
                           'listed_in']].reset_index(drop=True))
