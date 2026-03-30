```python
import streamlit as st
import pandas as pd
import pickle
import requests

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/peliculas.csv")

    with open("models/similitud.pkl", "rb") as f:
        similitud = pickle.load(f)

    with open("models/indices.pkl", "rb") as f:
        indices = pickle.load(f)

    return df, similitud, indices

df_peliculas, similitud, indices = load_data()

# ---------------- TMDB ----------------
API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

@st.cache_data
def get_movie_data(title):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
        data = requests.get(url).json()

        if data["results"]:
            movie = data["results"][0]

            poster = "https://image.tmdb.org/t/p/w500" + movie["poster_path"] if movie["poster_path"] else ""
            overview = movie["overview"]

            return {
                "poster": poster,
                "overview": overview
            }
    except:
        return None

# ---------------- RECOMENDADOR ----------------
def recomendar(movie_id, top_n=15):
    idx = indices[movie_id]
    scores = list(enumerate(similitud[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]

    movie_indices = [i[0] for i in scores]
    return df_peliculas.iloc[movie_indices]['movie_id'].values

# ---------------- CSS NETFLIX ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}

.scroll-container {
    display: flex;
    overflow-x: auto;
    gap: 15px;
    padding: 10px;
}

.movie-card {
    min-width: 180px;
    position: relative;
    cursor: pointer;
}

.movie-img {
    width: 100%;
    border-radius: 10px;
    transition: transform 0.3s;
}

.movie-card:hover .movie-img {
    transform: scale(1.1);
}

.movie-overlay {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 10px;
    background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
    opacity: 0;
    transition: 0.3s;
}

.movie-card:hover .movie-overlay {
    opacity: 1;
}

.movie-title {
    color: white;
    font-size: 14px;
    font-weight: bold;
}

.movie-desc {
    color: #ccc;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------
st.title("🎬 Movie Recommender AI")

# Buscador
movie_name = st.selectbox(
    "🔎 Buscar película",
    df_peliculas['titulo'].sort_values(),
    index=None,
    placeholder="Escribe para buscar..."
)

# Géneros
generos = df_peliculas.columns[2:]

genero_select = st.selectbox(
    "🎭 Filtrar por género",
    ["Todos"] + list(generos)
)

# ---------------- BOTON ----------------
if st.button("🚀 Recomendar"):

    if movie_name:

        movie_id = df_peliculas[
            df_peliculas['titulo'] == movie_name
        ]['movie_id'].values[0]

        recs = recomendar(movie_id)

        st.subheader("🔥 Recomendaciones")

        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

        for movie_id_rec in recs:

            row = df_peliculas[df_peliculas['movie_id'] == movie_id_rec].iloc[0]
            titulo = row['titulo']

            if genero_select != "Todos":
                if row[genero_select] != 1:
                    continue

            data = get_movie_data(titulo)

            poster = data["poster"] if data else ""
            overview = data["overview"][:120] if data else ""

            st.markdown(f"""
            <div class="movie-card">
                <img src="{poster}" class="movie-img"/>
                <div class="movie-overlay">
                    <div class="movie-title">{titulo}</div>
                    <div class="movie-desc">{overview}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("⚠️ Selecciona una película")
```
