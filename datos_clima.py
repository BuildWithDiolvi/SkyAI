"""Consulta condiciones actuales y pronósticos desde Open-Meteo."""

import pandas as pd
import requests

from ubicaciones import PROVINCIAS


URL_OPEN_METEO = "https://api.open-meteo.com/v1/forecast"

# Zonas adicionales que no aparecen como provincia individual en el selector.
ZONAS_TURISTICAS = {
    "Punta Cana": (18.5601, -68.3725),
    "Verón": (18.5815, -68.4054),
    "Bávaro": (18.6853, -68.4193),
    "Cap Cana": (18.4444, -68.4558),
}

def obtener_condiciones_mapa() -> pd.DataFrame:
    """Consulta en bloque el clima actual de las 32 provincias dominicanas."""
    ubicaciones_mapa = {**PROVINCIAS, **ZONAS_TURISTICAS}
    ubicaciones = list(ubicaciones_mapa.items())
    respuesta = requests.get(
        URL_OPEN_METEO,
        params={
            "latitude": ",".join(str(coordenadas[0]) for _, coordenadas in ubicaciones),
            "longitude": ",".join(str(coordenadas[1]) for _, coordenadas in ubicaciones),
            "current": ["temperature_2m", "weather_code"],
            "timezone": "America/Santo_Domingo",
        },
        timeout=15,
    )
    respuesta.raise_for_status()
    datos = respuesta.json()
    respuestas = datos if isinstance(datos, list) else [datos]
    marcadores = []
    for (nombre, (latitud, longitud)), resultado in zip(ubicaciones, respuestas):
        actual = resultado["current"]
        marcadores.append({
            "provincia": nombre,
            "lat": latitud,
            "lon": longitud,
            "temperatura": actual["temperature_2m"],
            "codigo_clima": actual["weather_code"],
        })
    return pd.DataFrame(marcadores)


def obtener_clima_actual(latitud: float, longitud: float) -> dict:
    """Devuelve datos actuales, 48 horas y el resumen diario para SkyAI."""
    parametros = {
        "latitude": latitud,
        "longitude": longitud,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "weather_code",
        ],
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "precipitation",
        ],
        "daily": [
            "temperature_2m_min",
            "temperature_2m_max",
            "precipitation_probability_max",
        ],
        "forecast_days": 7,
        "timezone": "America/Santo_Domingo",
    }
    respuesta = requests.get(URL_OPEN_METEO, params=parametros, timeout=10)
    respuesta.raise_for_status()
    datos = respuesta.json()
    actual = datos["current"]
    tiempo = pd.to_datetime(actual["time"])

    horario = datos["hourly"]
    pronostico_horario = pd.DataFrame({
        "tiempo": pd.to_datetime(horario["time"]),
        "temperatura": horario["temperature_2m"],
        "humedad": horario["relative_humidity_2m"],
        "viento": horario["wind_speed_10m"],
        "precipitacion": horario["precipitation"],
    })
    pronostico_horario = pronostico_horario[
        pronostico_horario["tiempo"] >= tiempo
    ].reset_index(drop=True)

    diario = datos["daily"]
    pronostico_diario = pd.DataFrame({
        "fecha": pd.to_datetime(diario["time"]),
        "minima": diario["temperature_2m_min"],
        "maxima": diario["temperature_2m_max"],
        "probabilidad_lluvia": diario["precipitation_probability_max"],
    })

    return {
        "temperatura": actual["temperature_2m"],
        "humedad": actual["relative_humidity_2m"],
        "precipitacion": actual["precipitation"],
        "viento": actual["wind_speed_10m"],
        "codigo_clima": actual["weather_code"],
        "hora": tiempo.hour,
        "dia_del_año": tiempo.dayofyear,
        "dia_semana": tiempo.dayofweek,
        "tiempo": tiempo,
        "pronostico_horario": pronostico_horario,
        "pronostico_diario": pronostico_diario,
    }
