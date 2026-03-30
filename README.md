# 🍿 Movie Recommender AI - Evolution (Netflix Style)

Esta aplicación es la versión orientada a producto del sistema de recomendación desarrollado originalmente en el proyecto [Movie Recommender AI V1](https://github.com/TU_USUARIO/PROYECTO_ANTERIOR). Mientras que la V1 se centró en la experimentación con algoritmos (SVD, TF-IDF), esta versión se enfoca en la **escalabilidad, persistencia y UI/UX de alto nivel**.

🚀 **Demo en vivo:** [Probar la App aquí](https://movierecommenderappnetflixstyle-geroge-1902.streamlit.app/)

---

## 🧠 De la Experimentación al Producto (V1 vs V2)

Este proyecto representa un salto técnico desde un entorno de análisis (Jupyter) hacia una aplicación web funcional:

| Característica | Versión Anterior (V1) | Versión Actual (V2) |
| :--- | :--- | :--- |
| **Enfoque** | Análisis y Evaluación (SVD/TF-IDF) | Producción y UX (Content-Based) |
| **Interfaz** | Básica / Experimental | Estilo Netflix (Hover Effects & Cards) |
| **Multimedia** | Solo Pósters | **Tráilers de YouTube**, Reparto y Director |
| **Persistencia** | Recarga de página estándar | **Streamlit Session State** para navegación fluida |
| **Arquitectura** | Ejecución en Notebook | Modular (Models + Data + App) |

---

## 🛠️ Arquitectura y Tecnologías

El motor de recomendación utiliza **Similitud del Coseno** calculada sobre vectores de características extraídos del dataset **MovieLens**.

### Stack Tecnológico:
* **Frontend:** Streamlit (Custom CSS para Look & Feel de Netflix).
* **Machine Learning:** Scikit-Learn (Matriz de similitud).
* **API:** The Movie Database (TMDB) para metadatos dinámicos.
* **Serialización:** Pickle/Joblib para carga rápida de modelos de 20MB+.

---

## ✨ Nuevas Funcionalidades

* **Ventanas Modales (Modals):** Implementación de `st.dialog` para ver detalles sin perder el contexto de búsqueda.
* **Reproductor de Tráiler:** Integración nativa de videos de YouTube.
* **Buscador con Autocompletado:** Filtrado rápido por título y género simultáneamente.
* **Diseño Visual:** Tarjetas con efectos de escala y superposición de información (Rating, Sinopsis).

---

## 📁 Estructura del Repositorio

```text
├── app.py              # Aplicación principal
├── data/
│   └── peliculas.csv   # Dataset procesado
├── assets              # Visualización app anterior
├── models/
│   ├── similitud.pkl   # Matriz de similitud (21.5 MB)
│   └── indices.pkl     # Mapeo de IDs de películas
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Documentación

👨‍💻 Autor

Jorge Ojeda Oracle Next Education (ONE) — Alura LATAM 📅 2026

📄 Licencia

Proyecto de uso educativo. Datos proporcionados por MovieLens. Pósters obtenidos vía TMDB API.
