import streamlit as st
import pandas as pd
import pickle
import requests
import os

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
    # Calculamos similitudes
    scores = list(enumerate(similitud[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    
    movie_indices = [i[0] for i in scores]
    
    # Devolvemos el DataFrame con las películas recomendadas
    return df_peliculas.iloc[movie_indices]

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
def recomendar(movie_id, top_n=15):
    idx = indices[movie_id]
    scores = list(enumerate(similitud[idx]))
    # Guardamos el score (distancia de similitud)
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    
    movie_indices = [i[0] for i in scores]
    movie_scores = [i[1] for i in scores] # Extraemos los valores de similitud
    
    recs = df_peliculas.iloc[movie_indices].copy()
    recs['similarity_score'] = movie_scores
    return recs

# ---------------- DENTRO DEL BOTON RECOMENDAR ----------------
if st.button("🚀 Recomendar"):
    if movie_name:
        movie_id = df_peliculas[df_peliculas['titulo'] == movie_name]['movie_id'].values[0]
        
        # Obtenemos el DataFrame de recomendadas
        df_recs = recomendar(movie_id)

        st.subheader("🔥 Recomendaciones")
        cols = st.columns(5) 
        idx_col = 0 

        for _, row in df_recs.iterrows():
            titulo = row['titulo']
            
            # --- CAMBIO AQUÍ: Usar la columna de calificación de tu CSV ---
            # Si tu columna se llama diferente, cámbiala aquí (ej. row['vote_average'])
            rating = row.get('puntuacion', 0) 

            if genero_select != "Todos":
                if row[genero_select] != 1:
                    continue

            poster = get_poster(titulo)
            
            with cols[idx_col % 5]:
                # Estructura HTML con la estrella y la nota real
                st.markdown(f"""
                <div class="movie-container">
                    {f'<img src="{poster}" class="movie-img"/>' if poster else '<div class="no-image">🎬</div>'}
                    <div class="movie-overlay">
                        <div class="movie-title">{titulo[:30]}</div>
                        <div class="movie-score">⭐ {round(rating, 1)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            idx_col += 1
