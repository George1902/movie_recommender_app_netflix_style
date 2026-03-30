import streamlit as st
import pandas as pd
import joblib
import requests
import os

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Movie Recommender AI",
    page_icon="🍿",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_resource
def load_models():
    try:
        import pickle
        # Intentamos cargar con pickle (ajusta a joblib si cambiaste el formato)
        with open("models/similitud.pkl", "rb") as f:
            similitud = pickle.load(f)
        with open("models/indices.pkl", "rb") as f:
            indices = pickle.load(f)
        return similitud, indices
    except Exception as e:
        st.error(f"Error al cargar modelos: {e}")
        return None, None

@st.cache_data
def load_csv():
    return pd.read_csv("data/peliculas.csv")

df_peliculas = load_csv()
similitud, indices = load_models()

# ---------------- TMDB API ----------------
API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

def get_movie_full_details(title):
    if not API_KEY: return None
    try:
        title_clean = title.split('(')[0].strip()
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title_clean}&language=es-ES"
        res = requests.get(search_url).json()
        
        if res.get("results"):
            movie_data = res["results"][0]
            m_id = movie_data["id"]
            
            # Buscamos detalles, videos (tráilers) y créditos (director/reparto)
            detail_url = f"https://api.themoviedb.org/3/movie/{m_id}?api_key={API_KEY}&append_to_response=videos,credits&language=es-ES"
            details = requests.get(detail_url).json()
            
            # Lógica de Tráiler
            trailer_url = None
            videos = details.get("videos", {}).get("results", [])
            for v in videos:
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
    except: return None
    return None

# ---------------- RECOMENDADOR ----------------
def recomendar(movie_id, top_n=15):
    if movie_id not in indices: return pd.DataFrame()
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
            st.image(info['poster'], use_container_width=True)
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
            st.write("**🎥 Tráiler Oficial:**")
            st.video(info['trailer'])

# ---------------- CSS ----------------
st.markdown("""
<style>
.movie-container {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    background-color: #1c1c1c;
    aspect-ratio: 2/3;
    margin-bottom: 5px;
}
.movie-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
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
    height: 100%;
    padding: 15px;
    background: linear-gradient(to top, rgba(0,0,0,1) 15%, rgba(0,0,0,0.6) 50%, rgba(0,0,0,0) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    pointer-events: none;
}
.movie-container:hover .movie-overlay {
    opacity: 1;
}
.movie-title-card {
    color: white;
    font-size: 15px;
    font-weight: 700;
}
.movie-desc-card {
    color: #ccc;
    font-size: 10px;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-top: 5px;
}
/* Estilo Botón Recomendar (Original) */
div.stButton > button {
    background-color: #333;
    color: white;
    border: 1px solid #444;
}
div.stButton > button:hover {
    border-color: #e50914;
    color: #e50914;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🍿 Movie Recommender AI</h1>", unsafe_allow_html=True)

# ---------------- UI ----------------
st.title("🎬 Películas")
c1, c2 = st.columns(2)
with c1:
    movie_name = st.selectbox("🔎 Buscar película", df_peliculas['titulo'].sort_values(), index=None)
with c2:
    genero_select = st.selectbox("🎭 Filtrar Género", ["Todos"] + list(df_peliculas.columns[2:]))

# --- GESTIÓN DE SESIÓN ---
if "recs" not in st.session_state:
    st.session_state.recs = None

if st.button("🚀 Recomendar"):
    if movie_name and similitud is not None:
        movie_selected = df_peliculas[df_peliculas['titulo'] == movie_name]
        if not movie_selected.empty:
            m_id = movie_selected['movie_id'].values[0]
            st.session_state.recs = recomendar(m_id)
        else:
            st.error("Película no encontrada.")
    else:
        st.warning("Selecciona una película válida.")

# Mostrar resultados si existen en la sesión
if st.session_state.recs is not None:
    st.subheader(f"🔥 Recomendaciones basadas en tu búsqueda")
    cols = st.columns(5)
    idx_col = 0
    
    for _, row in st.session_state.recs.iterrows():
        if genero_select != "Todos" and row[genero_select] != 1:
            continue
        
        info = get_movie_full_details(row['titulo'])
        if info:
            with cols[idx_col % 5]:
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
                
                if st.button(f"Ver detalles", key=f"details_{row['movie_id']}"):
                    mostrar_detalles(info, row['titulo'])
                
                idx_col += 1
        if idx_col >= 15: break

    if idx_col == 0:
        st.info("No se encontraron películas para este género.")
