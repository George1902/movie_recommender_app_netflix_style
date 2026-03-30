import streamlit as st
import pandas as pd
import numpy as np
import requests
import os

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    page_title="Movie Recommender Netflix Style",
    page_icon="🎬",
    layout="wide"
)

# -------------------------------
# 🎨 ESTILO NETFLIX
# -------------------------------
st.markdown("""
<style>
.movie-container {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    cursor: pointer;
}

.movie-img {
    width: 100%;
    border-radius: 12px;
    transition: transform 0.4s ease;
}

.movie-container:hover .movie-img {
    transform: scale(1.1);
}

.movie-overlay {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 10px;
    background: linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0));
    opacity: 0;
    transition: opacity 0.3s ease;
}

.movie-container:hover .movie-overlay {
    opacity: 1;
}

.movie-title {
    color: white;
    font-size: 16px;
    font-weight: 700;
}

.movie-score {
    color: #e50914;
    font-size: 14px;
}

.no-image {
    height: 250px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#1c1c1c;
    color:white;
    border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🎬 Netflix Style Recommender</h1>", unsafe_allow_html=True)

# -------------------------------
# 🔐 API
# -------------------------------
API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

if not API_KEY:
    st.error("⚠️ Falta configurar TMDB API KEY")
    st.stop()

# -------------------------------
# 🎬 POSTER
# -------------------------------
def get_poster(title):
    try:
        title = title.split('(')[0]
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
        data = requests.get(url).json()

        if data.get("results"):
            poster = data["results"][0].get("poster_path")
            if poster:
                return f"https://image.tmdb.org/t/p/w500{poster}"
    except:
        return None
    return None

# -------------------------------
# 📂 DATA
# -------------------------------
@st.cache_data
def load_data():
    df_movies = pd.read_csv(
        "data/u.item",
        sep="|",
        encoding="latin-1",
        header=None
    )

    df_movies = df_movies[[0,1] + list(range(5,24))]
    df_movies.columns = ['movie_id','title'] + [
        'unknown','Action','Adventure','Animation','Childrens','Comedy',
        'Crime','Documentary','Drama','Fantasy','Film-Noir','Horror',
        'Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western'
    ]

    genres = df_movies.columns[2:]

    return df_movies, genres

df_movies, genres = load_data()

# -------------------------------
# 🧠 MODELO (CONTENIDO)
# -------------------------------
@st.cache_data
def build_similarity(df_movies, genres):

    df_movies['genres_str'] = df_movies.apply(
        lambda x: ' '.join([g for g in genres if x[g]==1]), axis=1
    )

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df_movies['genres_str'])

    sim = cosine_similarity(tfidf_matrix)

    return sim

similarity = build_similarity(df_movies, genres)

# -------------------------------
# 🔍 BUSCADOR
# -------------------------------
search = st.text_input("🔎 Buscar película")

# 🎭 FILTRO
genre_selected = st.selectbox("🎭 Género", ["Todos"] + list(genres))

filtered = df_movies.copy()

if genre_selected != "Todos":
    filtered = filtered[filtered[genre_selected] == 1]

if search:
    filtered = filtered[filtered['title'].str.contains(search, case=False)]

st.write(f"🎬 {len(filtered)} películas encontradas")

# -------------------------------
# 🎬 RECOMENDAR
# -------------------------------
def recommend(title, n=15):

    idx = df_movies[df_movies['title'] == title].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:n+1]

    movie_indices = [i[0] for i in scores]
    return df_movies.iloc[movie_indices]

# -------------------------------
# UI GRID
# -------------------------------
cols = st.columns(5)

for i, row in filtered.head(20).iterrows():

    col = cols[i % 5]
    poster = get_poster(row['title'])

    with col:
        if poster:
            st.image(poster, use_container_width=True)
        else:
            st.markdown("<div class='no-image'>🎬</div>", unsafe_allow_html=True)

        if st.button(f"Ver similares {i}"):
            recs = recommend(row['title'])

            st.subheader(f"🔥 Porque viste {row['title']}")

            rec_cols = st.columns(5)

            for j, rec in recs.iterrows():
                poster2 = get_poster(rec['title'])
                col2 = rec_cols[j % 5]

                with col2:
                    if poster2:
                        st.image(poster2, use_container_width=True)
                    else:
                        st.markdown("<div class='no-image'>🎬</div>", unsafe_allow_html=True)