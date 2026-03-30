# 🍿 Movie Recommender AI - Netflix Style

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)
![Machine Learning](https://img.shields.io/badge/ML-Content--Based-green)

Esta aplicación es un sistema de recomendación de películas con una interfaz moderna inspirada en Netflix. Utiliza **Machine Learning** para sugerir títulos basados en la similitud de contenido y se integra con la API de **TMDB** para ofrecer una experiencia visual enriquecida con pósters, sinopsis y tráilers oficiales.

🚀 **App en vivo:** [Tu Enlace de Streamlit](https://movierecommenderappnetflixstyle-geroge-1902.streamlit.app/)

---

## 🛠️ Arquitectura del Proyecto

El sistema funciona mediante un flujo de tres capas:

1.  **Capa de Datos (Local):** Uso de un dataset de películas (`peliculas.csv`) preprocesado.
2.  **Capa de Inteligencia (ML):** Los modelos (`similitud.pkl` e `indices.pkl`) calculan la **Similitud del Coseno** entre vectores de características (géneros, palabras clave, etc.).
3.  **Capa de Presentación (API + UI):** Streamlit actúa como frontend, consultando la API de **The Movie Database (TMDB)** en tiempo real para obtener metadatos multimedia.



[Image of Content-based filtering recommendation system diagram]


---

## ✨ Características

* **Motor de Recomendación:** Basado en contenido (Content-Based Filtering).
* **Interfaz Interactiva:** Diseño responsive con efectos *hover* tipo tarjeta.
* **Detalles Extendidos:** Ventanas modales con director, reparto y puntuación.
* **Multimedia:** Reproducción de tráilers de YouTube directamente en la app.
* **Filtros Inteligentes:** Capacidad de filtrar las recomendaciones por género.

---

## 💻 Instalación y Uso Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
   cd TU_REPOSITORIO
