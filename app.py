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

def get_movie_details(title):
    try:
        title = title.split('(')[0]
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                movie_data = data["results"][0]
                poster_path = movie_data.get("poster_path")
                vote_average = movie_data.get("vote_average", 0) # Obtenemos la nota
                
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                return poster_url, vote_average
    except:
        return None, 0
    return None, 0
    
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
if st.button("🚀 Recomendar"):
    if movie_name:
        # 1. Obtener ID de la película seleccionada
        movie_selected = df_peliculas[df_peliculas['titulo'] == movie_name]
        
        if movie_selected.empty:
            st.error("No se encontró la película.")
        else:
            movie_id = movie_selected['movie_id'].values[0]
            
            # 2. Obtener el DataFrame de recomendaciones
            df_recs = recomendar(movie_id)

            st.subheader("🔥 Recomendaciones")
            cols = st.columns(5) 
            idx_col = 0 

            # 3. Bucle principal (iteramos sobre los IDs de las recomendadas)
            for movie_id_rec in df_recs['movie_id'].values:
                
                # Buscamos los datos de cada película recomendada en el CSV original
                datos_pelicula = df_peliculas[df_peliculas['movie_id'] == movie_id_rec]
                
                if datos_pelicula.empty:
                    continue
                
                row = datos_pelicula.iloc[0]
                titulo = row['titulo']

                # --- FILTRO DE GÉNERO ---
                if genero_select != "Todos":
                    if genero_select in row.index:
                        if row[genero_select] != 1:
                            continue

                # 4. Obtener detalles de TMDB (Poster y Rating 0-10)
                poster, rating = get_movie_details(titulo)

                # --- LÓGICA DE 5 ESTRELLAS ---
                rating_5 = rating / 2  # Convertimos escala 10 a escala 5
                num_stars = int(round(rating_5))
                stars_html = "★" * num_stars
                stars_empty_html = "☆" * (5 - num_stars)

                # 5. Dibujar en la columna correspondiente
                with cols[idx_col % 5]:
                    if poster:
                        st.markdown(f"""
                        <div class="movie-container">
                            <img src="{poster}" class="movie-img"/>
                            <div class="movie-overlay">
                                <div class="movie-title">{titulo[:30]}</div>
                                <div class="movie-score" style="color: #FFD700; font-size: 16px;">
                                    {stars_html}{stars_empty_html} 
                                    <span style="color: white; font-size: 12px;">({round(rating_5, 1)})</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="movie-container">
                            <div class="no-image">🎬</div>
                            <div class="movie-overlay">
                                <div class="movie-title">{titulo[:30]}</div>
                                <div class="movie-score" style="color: #FFD700; font-size: 16px;">
                                    {stars_html}{stars_empty_html}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                idx_col += 1
                
                # Limitamos a 15 recomendaciones máximo
                if idx_col >= 15:
                    break

            # Si el filtro de género fue muy estricto y no dejó pasar nada
            if idx_col == 0:
                st.info(f"No se encontraron recomendaciones de tipo '{genero_select}'.")
