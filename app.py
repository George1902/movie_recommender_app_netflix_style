import streamlit as st
import pandas as pd
import pickle
import requests

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Movie Recommender AI",
    page_icon="🍿",
    layout="wide"
)
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

def get_poster(title):
    try:
        title = title.split('(')[0]

        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
        response = requests.get(url)

        if response.status_code != 200:
            return None

        data = response.json()

        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except:
        return None

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

/* CONTENEDOR */
.movie-container {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    cursor: pointer;
}

/* IMAGEN */
.movie-img {
    width: 100%;
    border-radius: 12px;
    transition: transform 0.4s ease;
}

/* ZOOM */
.movie-container:hover .movie-img {
    transform: scale(1.1);
}

/* OVERLAY */
.movie-overlay {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 10px;
    background: linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0));
    opacity: 0;
    transition: opacity 0.3s ease;
}

/* MOSTRAR OVERLAY */
.movie-container:hover .movie-overlay {
    opacity: 1;
}

/* TITULO */
.movie-title {
    color: white;
    font-size: 16px;
    font-weight: 700;
    line-height: 1.2;
}

/* SCORE */
.movie-score {
    color: #e50914;
    font-size: 14px;
    font-weight: 500;
}

/* PLACEHOLDER */
.no-image {
    height: 250px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #1c1c1c;
    color: white;
    font-size: 30px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🍿 Movie Recommender AI</h1>", unsafe_allow_html=True)
# ---------------- UI ----------------
st.title("🎬 Movies")

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
# ---------------- BOTON ----------------
if st.button("🚀 Recomendar"):
    if movie_name:
        # 1. Obtener ID de la película seleccionada
        movie_selected = df_peliculas[df_peliculas['titulo'] == movie_name]
        movie_id = movie_selected['movie_id'].values[0]

        # 2. Obtener recomendaciones
        rec_ids = recomendar(movie_id)

        st.subheader("🔥 Recomendaciones")
        
        # 3. CREAR COLUMNAS (Importante para evitar el error de 'cols')
        cols = st.columns(5) 
        
        # Contador para distribuir en las 5 columnas
        idx_col = 0 

        for movie_id_rec in rec_ids:
            row = df_peliculas[df_peliculas['movie_id'] == movie_id_rec].iloc[0]
            titulo = row['titulo']

            # Filtro de género
            if genero_select != "Todos":
                if row[genero_select] != 1:
                    continue

            poster = get_poster(titulo)
            
            # Seleccionar la columna actual
            with cols[idx_col % 5]:
                if poster:
                    st.markdown(f"""
                    <div class="movie-container">
                        <img src="{poster}" class="movie-img"/>
                        <div class="movie-overlay">
                            <div class="movie-title">{titulo[:30]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="movie-container">
                        <div class="no-image">🎬</div>
                        <div class="movie-overlay">
                            <div class="movie-title">{titulo[:30]}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            idx_col += 1 # Incrementar solo si la película pasó el filtro
