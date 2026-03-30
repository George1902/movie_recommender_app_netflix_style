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

# ---------------- TMDB API ----------------
API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

def get_movie_full_details(title):
    try:
        title_clean = title.split('(')[0].strip()
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title_clean}&language=es-ES"
        res = requests.get(search_url).json()
        
        if res.get("results"):
            movie_data = res["results"][0]
            m_id = movie_data["id"]
            
            detail_url = f"https://api.themoviedb.org/3/movie/{m_id}?api_key={API_KEY}&append_to_response=videos,credits&language=es-ES"
            details = requests.get(detail_url).json()
            
            trailer_url = None
            for v in details.get("videos", {}).get("results", []):
                if v["site"] == "YouTube" and v["type"] in ["Trailer", "Teaser"]:
                    trailer_url = f"https://www.youtube.com/watch?v={v['key']}"
                    break
            
            director = next((m["name"] for m in details.get("credits", {}).get("crew", []) if m["job"] == "Director"), "Desconocido")
            actores = ", ".join([m["name"] for m in details.get("credits", {}).get("cast", [])[:5]])
            
            return {
                "poster": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}",
                "rating": movie_data.get("vote_average", 0),
                "overview": movie_data.get("overview", "Sin descripción disponible."),
                "year": movie_data.get("release_date", "")[:4],
                "trailer": trailer_url,
                "director": director,
                "actores": actores
            }
    except:
        return None
    return None

# ---------------- RECOMENDADOR ----------------
def recomendar(movie_id, top_n=15):
    idx = indices[movie_id]
    scores = list(enumerate(similitud[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    movie_indices = [i[0] for i in scores]
    return df_peliculas.iloc[movie_indices]

# ---------------- VENTANA MODAL ----------------
@st.dialog("Detalles de la Película", width="large")
def mostrar_detalles(info, titulo):
    col1, col2 = st.columns([1, 2])
    with col1:
        if info['poster']:
            st.image(info['poster'])
    with col2:
        st.title(titulo)
        st.write(f"**📅 Año:** {info['year']} | **⭐ Nota:** {round(info['rating']/2, 1)}/5")
        st.write(f"**🎬 Director:** {info['director']}")
        st.write(f"**👥 Reparto:** {info['actores']}")
        st.write("---")
        st.write("**Sinopsis:**")
        st.write(info['overview'])
        if info['trailer']:
            st.write("---")
            st.video(info['trailer'])

# ---------------- CSS ----------------
st.markdown("""
<style>
.movie-container {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    background-color: #1c1c1c;
}
.movie-img {
    width: 100%;
    border-radius: 12px;
    transition: transform 0.4s ease;
    display: block;
}
.movie-container:hover .movie-img {
    transform: scale(1.1);
}
.movie-overlay {
    position: absolute;
    bottom: 0;
    width: 100%;
    height: 100%;
    padding: 15px;
    background: linear-gradient(to top, rgba(0,0,0,1) 10%, rgba(0,0,0,0.5) 50%, rgba(0,0,0,0) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    pointer-events: none; /* Permite que el clic pase al botón de abajo */
}
.movie-container:hover .movie-overlay {
    opacity: 1;
}
.movie-title-card {
    color: white;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 5px;
}
.movie-desc-card {
    color: #ccc;
    font-size: 11px;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
/* Estilo del botón Recomendar (Original) */
div.stButton > button:first-child {
    background-color: #1c1c1c;
    color: white;
    border: 1px solid #333;
}
/* Estilo invisible para el botón Ver Más sobre la imagen */
.overlay-button {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: transparent;
    border: none;
    cursor: pointer;
    z-index: 10;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🍿 Movie Recommender AI</h1>", unsafe_allow_html=True)

# ---------------- UI ----------------
st.title("🎬 Películas")
col1, col2 = st.columns(2)
with col1:
    movie_name = st.selectbox("🔎 Buscar película", df_peliculas['titulo'].sort_values(), index=None)
with col2:
    genero_select = st.selectbox("🎭 Género", ["Todos"] + list(df_peliculas.columns[2:]))

if st.button("🚀 Recomendar"):
    if movie_name:
        movie_id = df_peliculas[df_peliculas['titulo'] == movie_name]['movie_id'].values[0]
        df_recs = recomendar(movie_id)
        
        st.subheader("🔥 Recomendaciones")
        cols = st.columns(5)
        idx_col = 0
        
        for movie_id_rec in df_recs['movie_id'].values:
            row = df_peliculas[df_peliculas['movie_id'] == movie_id_rec].iloc[0]
            if genero_select != "Todos" and row[genero_select] != 1:
                continue
            
            info = get_movie_full_details(row['titulo'])
            if info:
                with cols[idx_col % 5]:
                    # Contenedor Visual
                    st.markdown(f"""
                    <div class="movie-container">
                        <img src="{info['poster']}" class="movie-img"/>
                        <div class="movie-overlay">
                            <div class="movie-title-card">{row['titulo'][:30]}</div>
                            <div class="movie-score" style="color:#FFD700">★ {round(info['rating']/2,1)}</div>
                            <div class="movie-desc-card">{info['overview']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # El botón ahora está debajo pero lo usaremos para disparar el modal
                    if st.button(f"Ver detalle", key=f"btn_{movie_id_rec}"):
                        mostrar_detalles(info, row['titulo'])
                idx_col += 1
            if idx_col >= 15: break
