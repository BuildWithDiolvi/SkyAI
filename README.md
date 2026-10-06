# SkyAI

Aplicación web de inteligencia meteorológica para República Dominicana. SkyAI consulta datos climáticos en tiempo real, muestra pronósticos interactivos y utiliza un modelo de aprendizaje automático para estimar la temperatura.

## Aplicación en línea

Puedes ver la aplicación publicada aquí: [SkyAI](https://buildwithdiolvi-skyai-app-dpn3pb.streamlit.app/)

## Funciones principales

- Consulta del clima actual para provincias, municipios y destinos turísticos de República Dominicana.
- Pronóstico meteorológico de los próximos días.
- Mapa interactivo con condiciones climáticas.
- Alertas de lluvia, viento fuerte y temperatura.
- Sistema de ubicaciones favoritas.
- Predicción de temperatura con un modelo de Machine Learning.

## Tecnologías utilizadas

- Python
- Streamlit
- Pandas
- Scikit-learn
- PyDeck
- Open-Meteo API

## Ejecutar el proyecto localmente

1. Clona este repositorio.
2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Inicia la aplicación:

   ```bash
   streamlit run app.py
   ```

## Estructura principal

- `app.py`: interfaz principal de SkyAI.
- `datos_clima.py`: consulta de datos meteorológicos.
- `modelo_ml.py`: entrenamiento del modelo de aprendizaje automático.
- `modelo_skyai.pkl`: modelo entrenado.
- `requirements.txt`: dependencias del proyecto.

---

Proyecto académico desarrollado para el ITLA.
