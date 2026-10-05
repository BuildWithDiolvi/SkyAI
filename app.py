"""Dashboard principal de SkyAI, sin iconos renderizados como HTML."""

from pathlib import Path

import joblib
import pandas as pd
import pydeck as pdk
import requests
import streamlit as st

from datos_clima import obtener_clima_actual, obtener_condiciones_mapa
from estado_meteorologico import interpretar_clima
from favoritos import cargar_favoritos, guardar_favoritos, nombre_corto
from ubicaciones import coordenadas_ubicacion, opciones_ubicacion


BASE_DIR = Path(__file__).resolve().parent
MODELO_PATH = BASE_DIR / "modelo_skyai.pkl"

UBICACIONES_ESPECIALES = {
    "Verón · Distrito municipal (La Altagracia)": (18.5815, -68.4054, "Verón"),
    "Punta Cana · Zona turística (La Altagracia)": (18.5601, -68.3725, "Punta Cana"),
    "Bávaro · Zona turística (La Altagracia)": (18.6853, -68.4193, "Bávaro"),
    "Cap Cana · Destino turístico (La Altagracia)": (18.4444, -68.4558, "Cap Cana"),
}

st.set_page_config(page_title="SkyAI | Clima RD", page_icon="☁️", layout="wide")


@st.cache_resource(show_spinner=False)
def cargar_modelo():
    return joblib.load(MODELO_PATH)


def crear_datos_modelo(clima: dict) -> pd.DataFrame:
    return pd.DataFrame({
        "temperature_2m": [clima["temperatura"]],
        "relative_humidity_2m": [clima["humedad"]],
        "precipitation": [clima["precipitacion"]],
        "wind_speed_10m": [clima["viento"]],
        "hora": [clima["hora"]],
        "dia_del_año": [clima["dia_del_año"]],
        "día_semana": [clima["dia_semana"]],
    })


def opciones_skyai() -> list[str]:
    """Incluye provincias, municipios y zonas importantes de La Altagracia."""
    return sorted(opciones_ubicacion() + list(UBICACIONES_ESPECIALES), key=str.casefold)


def coordenadas_skyai(opcion: str) -> tuple[float, float, str]:
    if opcion in UBICACIONES_ESPECIALES:
        return UBICACIONES_ESPECIALES[opcion]
    return coordenadas_ubicacion(opcion)


def tarjeta(titulo: str, valor: str, detalle: str) -> None:
    """Tarjeta visual reutilizable para las métricas del panel."""
    st.markdown(f'''<div class="metric-card"><p>{titulo}</p><h2>{valor}</h2><span>{detalle}</span></div>''', unsafe_allow_html=True)


def icono_clima(codigo: int) -> str:
    if codigo == 0:
        return "☀️"
    if codigo in (1, 2):
        return "🌤️"
    if codigo == 3:
        return "☁️"
    if codigo in (45, 48):
        return "🌫️"
    if codigo in (95, 96, 99):
        return "⛈️"
    if codigo >= 80:
        return "🌧️"
    if codigo >= 51:
        return "🌦️"
    return "🌡️"


def crear_alertas(clima: dict, pronostico: pd.DataFrame) -> list[tuple[str, str]]:
    """Genera alertas útiles para las siguientes 24 horas."""
    alertas = []
    lluvia = pronostico["precipitacion"].sum()
    viento = pronostico["viento"].max()
    maxima = pronostico["temperatura"].max()
    if lluvia >= 5:
        alertas.append(("⚠️ Lluvia prevista", f"Se estiman {lluvia:.1f} mm durante las próximas 24 horas."))
    if viento >= 30:
        alertas.append(("💨 Viento fuerte", f"Puede alcanzar {viento:.1f} km/h. Asegura objetos exteriores."))
    if maxima >= 34:
        alertas.append(("🌡️ Calor elevado", f"La temperatura puede subir a {maxima:.1f} °C. Mantente hidratado."))
    if clima["humedad"] >= 85:
        alertas.append(("💧 Humedad alta", "La sensación térmica puede ser mayor de lo habitual."))
    return alertas


def estilo_zona_meteorologica(codigo: int) -> tuple[str, list[int]]:
    """Convierte el código de Open-Meteo en una zona visual del mapa."""
    if codigo == 0:
        return "☀️ Soleado", [255, 190, 38, 170]
    if codigo in (1, 2):
        return "🌤️ Parcialmente nublado", [120, 195, 255, 165]
    if codigo == 3:
        return "☁️ Nublado", [148, 163, 184, 165]
    if codigo in (45, 48):
        return "🌫️ Niebla", [174, 190, 204, 160]
    if codigo in (95, 96, 99):
        return "⛈️ Tormenta", [139, 92, 246, 190]
    if codigo >= 51:
        return "🌧️ Lluvia", [45, 145, 235, 185]
    return "🌡️ Condición actual", [63, 221, 203, 165]


@st.cache_data(ttl=600, show_spinner=False)
def cargar_zonas_meteorologicas() -> pd.DataFrame:
    """Evita pedir datos otra vez durante diez minutos."""
    return obtener_condiciones_mapa()


st.markdown("""
<style>
  .stApp {
    background:
      radial-gradient(circle at 14% 18%, rgba(29, 119, 190, .26), transparent 30%),
      radial-gradient(circle at 85% 72%, rgba(63, 221, 203, .14), transparent 32%),
      linear-gradient(125deg, #070b12, #0b1525, #0a1020, #07101b);
    background-size: 180% 180%;
    animation: skyai-flow 18s ease-in-out infinite;
  }
  @keyframes skyai-flow {
    0%, 100% { background-position: 0% 40%; }
    50% { background-position: 100% 60%; }
  }
  .block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem; }
  h2, h3, h4 { color: #e7ecf5 !important; }
  .hero { background: linear-gradient(115deg, #071b3a, #1261a0, #5a3c9e, #0d8d91, #071b3a);
          background-size: 320% 320%; animation: hero-flow 12s ease-in-out infinite;
          padding: 2rem 2.2rem; border-radius: 20px; margin-bottom: 1.6rem;
          box-shadow: 0 12px 30px rgba(12, 58, 107, .18); }
  @keyframes hero-flow {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
  }
  .hero h1 { font-size: 2.15rem; margin: 0 0 .35rem; color: white !important; }
  .hero p { margin: 0; opacity: .88; font-size: 1.05rem; }
  .metric-card { background: transparent; border: 0; border-radius: 0;
                 padding: .15rem .1rem .8rem; min-height: 92px; box-shadow: none; }
  .metric-card p { color: #aebde0; font-size: .92rem; margin: 0 0 .45rem; }
  .metric-card h2 { color: #f2f6ff; margin: 0 0 .35rem; font-size: 1.65rem; }
  .metric-card span { color: #93a6c5; font-size: .8rem; }
  .prediction { background: transparent; border-radius: 0; padding: .2rem 0; border: 0; }
  .prediction h2 { margin: .25rem 0; color: #f2f6ff; font-size: 2.2rem; }
  .weather-status { background: transparent; border-left: 0; border-radius: 0;
                    padding: .25rem 0; margin: .4rem 0 1.1rem; box-shadow: none; }
  .weather-status strong { color: #f2f6ff; font-size: 1.05rem; }
  .weather-status p { color: #aebde0; margin: .35rem 0 0; }
  .weather-alert { background: transparent; border-left: 0; border-radius: 0;
                   padding: .25rem 0; margin: .7rem 0; }
  .weather-alert strong { color: #ffd166; }
  .weather-alert p { color: #aebde0; margin: .35rem 0 0; }
  .eyebrow { color: #8ebde9; font-size: .82rem; font-weight: 700; letter-spacing: .08em; }
  div[data-testid="stAlert"] { background: transparent !important; border: 0 !important; padding: .3rem 0 !important; }
  div[data-testid="stAlert"] p { color: #9ce3bb !important; }
  [data-testid="stMetric"] {
    background: #fff; border: 1px solid #e3ebf5; border-radius: 16px;
    padding: 1rem 1.1rem; box-shadow: 0 6px 18px rgba(16, 42, 67, .06);
  }
  [data-testid="stMetricLabel"] { color: #52708f; }
  [data-testid="stMetricValue"] { color: #102a43; }
  div[data-testid="stButton"] button { border-radius: 9px; font-weight: 600; }
  div[data-testid="stButton"] button[kind="primary"] {
    background: #1261a0; border-color: #1261a0;
  }
  [data-testid="stDataFrame"] { border: 1px solid #e3ebf5; border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown('''<div class="hero"><h1>☁️ SkyAI</h1>
<p>Inteligencia meteorológica para República Dominicana</p></div>''', unsafe_allow_html=True)

if "favoritos" not in st.session_state:
    st.session_state["favoritos"] = cargar_favoritos()

if st.session_state["favoritos"]:
    encabezado_favoritos, limpiar_favoritos = st.columns([5, 1])
    with encabezado_favoritos:
        st.caption(f"⭐ Ubicaciones favoritas ({len(st.session_state['favoritos'])})")
    with limpiar_favoritos:
        if st.button("Limpiar", key="limpiar_favoritos", help="Eliminar todos los favoritos"):
            st.session_state["favoritos"] = []
            guardar_favoritos([])
            st.rerun()
    columnas = st.columns(min(4, len(st.session_state["favoritos"])))
    for indice, favorito in enumerate(st.session_state["favoritos"]):
        with columnas[indice % len(columnas)]:
            elegir, quitar = st.columns([4, 1])
            with elegir:
                if st.button(f"⭐ {nombre_corto(favorito)}", key=f"favorito_{indice}"):
                    st.session_state["ubicacion_selector"] = favorito
                    st.rerun()
            with quitar:
                if st.button("✕", key=f"quitar_{indice}", help="Eliminar favorito"):
                    st.session_state["favoritos"].remove(favorito)
                    guardar_favoritos(st.session_state["favoritos"])
                    st.rerun()

selector, actualizar, guardar = st.columns([3, 1.25, 1.25], vertical_alignment="bottom")
with selector:
    provincia = st.selectbox("📍 Provincia, municipio o destino", opciones_skyai(), key="ubicacion_selector")
with actualizar:
    consultar = st.button("Actualizar clima", type="primary", use_container_width=True)
with guardar:
    guardar_favorito = st.button("⭐ Favorito", use_container_width=True)

if guardar_favorito:
    if provincia in st.session_state["favoritos"]:
        st.info("Esta ubicación ya está en tus favoritos.")
    else:
        st.session_state["favoritos"].append(provincia)
        guardar_favoritos(st.session_state["favoritos"])
        st.success("Ubicación guardada en favoritos.")
        st.rerun()

if consultar:
    latitud, longitud, nombre_ubicacion = coordenadas_skyai(provincia)
    try:
        with st.spinner("Consultando datos meteorológicos…"):
            clima = obtener_clima_actual(latitud, longitud)
            prediccion = cargar_modelo().predict(crear_datos_modelo(clima))
        st.session_state["consulta"] = {
            "provincia": nombre_ubicacion,
            "clima": clima,
            "temperatura_predicha": round(float(prediccion[0]), 2),
            "latitud": latitud,
            "longitud": longitud,
        }
    except requests.RequestException:
        st.error("No fue posible obtener los datos de Open-Meteo. Revisa tu conexión e inténtalo de nuevo.")
    except FileNotFoundError:
        st.error("No se encontró modelo_skyai.pkl junto a app.py.")
    except Exception as error:
        st.error(f"SkyAI no pudo generar la predicción: {error}")

consulta = st.session_state.get("consulta")
if not consulta:
    st.info("Selecciona una provincia y pulsa **Actualizar clima** para ver el dashboard.")
    st.stop()

clima = consulta["clima"]
estado = interpretar_clima(clima["codigo_clima"], clima["temperatura"], clima["viento"], clima["precipitacion"])
st.subheader(f"{icono_clima(clima['codigo_clima'])} {consulta['provincia']}")
st.caption(f"Actualizado: {clima['tiempo'].strftime('%d/%m/%Y · %I:%M %p')}")

metricas = st.columns(4)
with metricas[0]: tarjeta("🌡️ Temperatura", f"{clima['temperatura']:.1f} °C", "Condición actual")
with metricas[1]: tarjeta("💧 Humedad", f"{clima['humedad']:.0f} %", "Humedad relativa")
with metricas[2]: tarjeta("💨 Viento", f"{clima['viento']:.1f} km/h", "Velocidad del viento")
with metricas[3]: tarjeta("🌧️ Precipitación", f"{clima['precipitacion']:.1f} mm", "Acumulado actual")

st.markdown(f'''<div class="weather-status"><strong>{estado['estado']}</strong><p>{estado['recomendacion']}</p></div>''', unsafe_allow_html=True)

pronostico = clima["pronostico_horario"].head(24).set_index("tiempo")
st.subheader("Próximas 24 horas")
resumen = st.columns(3)
with resumen[0]: tarjeta("🌡️ Temperatura mínima", f"{pronostico['temperatura'].min():.1f} °C", "En las próximas 24 horas")
with resumen[1]: tarjeta("☀️ Temperatura máxima", f"{pronostico['temperatura'].max():.1f} °C", "En las próximas 24 horas")
with resumen[2]: tarjeta("💨 Viento máximo", f"{pronostico['viento'].max():.1f} km/h", "Ráfaga prevista")

alertas = crear_alertas(clima, pronostico)
if alertas:
    for alerta_titulo, alerta_texto in alertas:
        st.markdown(f'''<div class="weather-alert"><strong>{alerta_titulo}</strong><p>{alerta_texto}</p></div>''', unsafe_allow_html=True)
else:
    st.success("✅ Sin alertas relevantes durante las próximas 24 horas.")

grafica, prediccion_col = st.columns([2, 1])
with grafica:
    st.markdown("#### 📈 Temperatura prevista")
    st.line_chart(pronostico[["temperatura"]], color="#1261a0", height=280)
with prediccion_col:
    diferencia = consulta["temperatura_predicha"] - clima["temperatura"]
    if diferencia > 0.3:
        tendencia = f"Subirá aproximadamente {abs(diferencia):.1f} °C"
    elif diferencia < -0.3:
        tendencia = f"Bajará aproximadamente {abs(diferencia):.1f} °C"
    else:
        tendencia = "Se mantendrá prácticamente estable"
    st.markdown(f'''<div class="prediction"><div class="eyebrow">🤖 PREDICCIÓN SKYAI</div>
    <h2>{consulta['temperatura_predicha']:.2f} °C</h2>
    <p style="margin:0;color:#53708d">Temperatura estimada para la próxima hora</p>
    <p style="margin:.65rem 0 0;color:#123a64;font-weight:600">{tendencia}</p></div>''', unsafe_allow_html=True)
    st.caption("Estimación generada por el modelo Random Forest de SkyAI.")

titulo_mapa, control_mapa = st.columns([4, 1], vertical_alignment="center")
with titulo_mapa:
    st.markdown("#### 🗺️ Mapa meteorológico inteligente")
with control_mapa:
    enfocar_seleccion = st.checkbox("🎯 Enfocar selección", value=True, key="enfocar_mapa")
try:
    zonas = cargar_zonas_meteorologicas().copy()
    estilos = zonas["codigo_clima"].map(estilo_zona_meteorologica)
    zonas["condicion"] = estilos.map(lambda estilo: estilo[0])
    zonas["color"] = estilos.map(lambda estilo: estilo[1])
    zonas["aura"] = zonas["color"].map(lambda color: color[:3] + [48])
    zonas["nucleo"] = zonas["color"].map(lambda color: color[:3] + [225])

    capa_aura = pdk.Layer(
        "ScatterplotLayer",
        data=zonas,
        get_position="[lon, lat]",
        get_fill_color="aura",
        get_radius=21000,
        radius_min_pixels=16,
        radius_max_pixels=38,
        pickable=False,
        stroked=False,
    )
    capa_nucleo = pdk.Layer(
        "ScatterplotLayer",
        data=zonas,
        get_position="[lon, lat]",
        get_fill_color="nucleo",
        get_line_color=[235, 245, 255, 210],
        get_radius=5200,
        radius_min_pixels=5,
        radius_max_pixels=12,
        line_width_min_pixels=1,
        pickable=True,
        stroked=True,
    )
    condicion_seleccionada, color_seleccionada = estilo_zona_meteorologica(clima["codigo_clima"])
    seleccion = pd.DataFrame({
        "lat": [consulta.get("latitud", 18.75)],
        "lon": [consulta.get("longitud", -70.2)],
        "color": [color_seleccionada[:3] + [255]],
        "etiqueta": [f"📍 {consulta['provincia']} · {condicion_seleccionada}"],
    })
    capa_radar = pdk.Layer(
        "ScatterplotLayer",
        data=seleccion,
        get_position="[lon, lat]",
        get_line_color="color",
        get_radius=15500,
        radius_min_pixels=20,
        radius_max_pixels=42,
        line_width_min_pixels=3,
        filled=False,
        stroked=True,
        pickable=True,
    )
    capa_etiqueta = pdk.Layer(
        "TextLayer",
        data=seleccion,
        get_position="[lon, lat]",
        get_text="etiqueta",
        get_color=[245, 249, 255, 255],
        get_size=13,
        get_alignment_baseline="bottom",
        get_pixel_offset=[0, -18],
        pickable=True,
    )
    if enfocar_seleccion:
        vista_inicial = pdk.ViewState(
            latitude=consulta.get("latitud", 18.75),
            longitude=consulta.get("longitud", -70.2),
            zoom=10.2,
            pitch=28,
        )
    else:
        vista_inicial = pdk.ViewState(latitude=18.75, longitude=-70.2, zoom=7.1, pitch=0)
    mapa = pdk.Deck(
        layers=[capa_aura, capa_nucleo, capa_radar, capa_etiqueta],
        initial_view_state=vista_inicial,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        tooltip={"html": "<b>{provincia}</b><br/>{condicion}<br/>{temperatura} °C", "style": {"color": "white"}},
    )
    st.pydeck_chart(mapa, use_container_width=True, height=440)
    st.caption("Pasa el cursor sobre una zona para ver su condición actual. Amarillo: sol · Azul: lluvia · Gris: nubes · Violeta: tormenta.")
except requests.RequestException:
    st.info("El mapa meteorológico no pudo actualizarse en este momento.")

humedad, viento_grafica = st.columns(2)
with humedad:
    st.markdown("#### 💧 Humedad prevista")
    st.bar_chart(pronostico[["humedad"]], color="#4f9ed1", height=230)
with viento_grafica:
    st.markdown("#### 💨 Viento previsto")
    st.bar_chart(pronostico[["viento"]], color="#667eea", height=230)

st.markdown("#### 📅 Pronóstico semanal")
diario = clima["pronostico_diario"].copy()
diario["Día"] = diario["fecha"].dt.strftime("%a %d/%m")
diario = diario.rename(columns={"minima": "Mínima (°C)", "maxima": "Máxima (°C)", "probabilidad_lluvia": "Probabilidad de lluvia"})
diario["Probabilidad de lluvia"] = diario["Probabilidad de lluvia"].map(lambda valor: f"{valor:.0f} %")
st.dataframe(diario[["Día", "Mínima (°C)", "Máxima (°C)", "Probabilidad de lluvia"]], hide_index=True, use_container_width=True)
st.caption("Datos meteorológicos: Open-Meteo · Predicción: modelo local SkyAI")
