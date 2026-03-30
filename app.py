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
    # Asegúrate de que la ruta sea correcta según tu estructura de carpetas
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
        # 1. Buscar la película básica
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title_clean}&language=es-ES"
        res = requests.get(search_url).json()
        
        if res.get("results"):
            movie_data = res["results"][0]
            m_id = movie_data["id"]
            
            # 2. Obtener detalles extendidos (Videos y Créditos)
            detail_url = f"https://api.themoviedb.org/3/movie/{m_id}?api_key={API_KEY}&append_to_response=videos,credits&language=es-ES"
            details = requests.get(detail_url).json()
            
            # Extraer Tráiler de YouTube
            trailer_url = None
            videos = details.get("videos", {}).get("results", [])
            for v in videos:
                if v["site"] == "YouTube" and (v["type"] == "Trailer" or v["type"] == "Teaser"):
                    trailer_url = f"https://www.youtube.com/watch?v={v['key']}"
                    break
            
            # Extraer Director y Actores
            crew = details.get("credits", {}).get("crew", [])
            director = next((m["name"] for m in crew if m["job"] == "Director"), "Desconocido")
            
            cast = details.get("credits", {}).get("cast", [])
            actores = ", ".join([m["name"] for m in cast[:5]]) # Top 5 actores
            
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

# ---------------- VENTANA MODAL (DETALLES) ----------------
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
        else:
            st.info("Tráiler no disponible en este momento.")

# ---------------- CSS ESTILO NETFLIX ----------------
st.markdown("""
<style>
.movie-container {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    background-color: #1c1c1c;
    margin-bottom: 10px;
}
.movie-img {
    width: 100%;
    border-radius: 12px;
    transition: transform 0.4s ease;
    display: block;
}
.movie-container:hover .movie-img {
    transform: scale(1.05);
}
.movie-overlay {
    position: absolute;
    bottom: 0;
    width: 100%;
    height: 100%;
    padding: 15px;
    background: linear-gradient(to top, rgba(0,0,0,1) 20%, rgba(0,0,0,0) 80%);
    opacity: 0;
    transition: opacity 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}
.movie-container:hover .movie-overlay {
    opacity: 1;
}
.movie-title-card {
    color: white;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 5px;
}
/* Estilo para los botones Ver Más */
.stButton>button {
    width: 100%;
    background-color: #e50914;
    color: white;
    border: none;
    border-radius: 4px;
}
.stButton>button:hover {
    background-color: #b20710;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🍿 Movie Recommender AI</h1>", unsafe_allow_html=True)

# ---------------- UI PRINCIPAL ----------------
st.title("🎬 Películas")

col_search, col_genre = st.columns(2)

with col_search:
    movie_name = st.selectbox(
        "🔎 Buscar película",
        df_peliculas['titulo'].sort_values(),
        index=None,
        placeholder="Escribe para buscar..."
    )

with col_genre:
    generos_cols = df_peliculas.columns[2:]
    genero_select = st.selectbox(
        "🎭 Filtrar por género",
        ["Todos"] + list(generos_cols)
    )

# ---------------- LÓGICA DE RECOMENDACIÓN ----------------
if st.button("🚀 Recomendar"):
    if movie_name:
        movie_selected = df_peliculas[df_peliculas['titulo'] == movie_name]
        
        if not movie_selected.empty:
            movie_id = movie_selected['movie_id'].values[0]
            df_recs = recomendar(movie_id)

            st.subheader(f"🔥 Si te gustó '{movie_name}', te recomendamos:")
            
            # Crear cuadrícula de 5 columnas
            idx_col = 0
            cols = st.columns(5)

            for movie_id_rec in df_recs['movie_id'].values:
                datos = df_peliculas[df_peliculas['movie_id'] == movie_id_rec].iloc[0]
                titulo_rec = datos['titulo']

                # Filtro de género
                if genero_select != "Todos" and datos[genero_select] != 1:
                    continue

                # Obtener info completa de la API
                info = get_movie_full_details(titulo_rec)

                if info:
                    with cols[idx_col % 5]:
                        # Card visual
                        st.markdown(f"""
                        <div class="movie-container">
                            <img src="{info['poster']}" class="movie-img"/>
                            <div class="movie-overlay">
                                <div class="movie-title-card">{titulo_rec[:40]}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botón de detalles (usa el session_state implícito de st.dialog)
                        if st.button(f"ℹ️ Ver más", key=f"details_{movie_id_rec}"):
                            mostrar_detalles(info, titulo_rec)
                        
                    idx_col += 1
                
                if idx_col >= 15: # Límite de resultados
                    break

            if idx_col == 0:
                st.info(f"No hay recomendaciones de '{genero_select}' para esta película.")
    else:
        st.warning("Por favor, selecciona una película primero.")
