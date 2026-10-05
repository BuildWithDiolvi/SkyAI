import pandas as pd
import requests
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


# ============================================================
# SKYAI - ENTRENAMIENTO DEL MODELO
# ============================================================

print("☁ SkyAI - Iniciando modelo")
print()


# ============================================================
# CARGAR HISTORIAL CLIMÁTICO
# ============================================================

historial = pd.read_csv("historial_clima.csv")


# ============================================================
# CONVERTIR LA COLUMNA DE TIEMPO
# ============================================================

historial["time"] = pd.to_datetime(
    historial["time"],
    format="mixed"
)


# ============================================================
# TEMPERATURA DE LA SIGUIENTE HORA
# ============================================================

historial["temperatura_siguiente"] = (
    historial["temperature_2m"].shift(-1)
)

historial = historial.dropna(
    subset=["temperatura_siguiente"]
)


# ============================================================
# VARIABLES TEMPORALES
# ============================================================

historial["hora"] = historial["time"].dt.hour

historial["dia_del_año"] = (
    historial["time"].dt.dayofyear
)

historial["día_semana"] = (
    historial["time"].dt.dayofweek
)


# ============================================================
# INFORMACIÓN DE LOS DATOS
# ============================================================

print("☁ SkyAI - Datos para Machine Learning")

print()

print(
    "Total de registros:",
    len(historial)
)

print()

print(historial.head())


# ============================================================
# VARIABLES PARA MACHINE LEARNING
# ============================================================

X = historial[
    [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "hora",
        "dia_del_año",
        "día_semana"
    ]
]

y = historial["temperatura_siguiente"]


print()

print("☁ SkyAI - Variables del modelo")

print()

print("X - Datos que utiliza el modelo:")

print(X.head())

print()

print("y - Temperatura que queremos predecir:")

print(y.head())


# ============================================================
# SEPARAR DATOS RESPETANDO EL ORDEN TEMPORAL
# ============================================================

cantidad_datos = len(X)

punto_separacion = int(
    cantidad_datos * 0.8
)


X_entrenamiento = X.iloc[
    :punto_separacion
]

X_prueba = X.iloc[
    punto_separacion:
]


y_entrenamiento = y.iloc[
    :punto_separacion
]

y_prueba = y.iloc[
    punto_separacion:
]


print()

print("☁ SkyAI - División temporal")

print(
    "Datos para entrenamiento:",
    len(X_entrenamiento)
)

print(
    "Datos para prueba:",
    len(X_prueba)
)


# ============================================================
# CREAR EL MODELO
# ============================================================

modelo = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# ============================================================
# ENTRENAR EL MODELO
# ============================================================

modelo.fit(
    X_entrenamiento,
    y_entrenamiento
)


print()

print("☁ SkyAI - Modelo entrenado")

print("El modelo terminó de aprender.")


# ============================================================
# GUARDAR EL MODELO
# ============================================================

joblib.dump(
    modelo,
    "modelo_skyai.pkl"
)

print()

print("☁ SkyAI - Modelo guardado")

print("Archivo: modelo_skyai.pkl")


# ============================================================
# HACER PREDICCIONES DE PRUEBA
# ============================================================

predicciones = modelo.predict(
    X_prueba
)


print()

print("☁ SkyAI - Predicciones")

print("Primeras 5 predicciones:")

print(predicciones[:5])


# ============================================================
# COMPARAR TEMPERATURA REAL VS PREDICCIÓN
# ============================================================

comparacion = pd.DataFrame(
    {
        "Temperatura_real": y_prueba.values,
        "Temperatura_predicha": predicciones
    }
)


print()

print("☁ SkyAI - Comparación")

print(comparacion.head())


# ============================================================
# EVALUAR EL MODELO
# ============================================================

error_mae = mean_absolute_error(
    y_prueba,
    predicciones
)


print()

print("☁ SkyAI - Evaluación del modelo")

print(
    "Error promedio del modelo:",
    round(error_mae, 2),
    "°C"
)


# ============================================================
# PROVINCIAS DE REPÚBLICA DOMINICANA
# ============================================================

provincias = {
    "Santo Domingo": (18.4861, -69.9312),
    "Distrito Nacional": (18.4861, -69.9312),
    "San Pedro de Macorís": (18.4539, -69.3086),
    "La Romana": (18.4273, -68.9728),
    "Santiago": (19.4517, -70.6970),
    "Puerto Plata": (19.7934, -70.6884),
    "La Vega": (19.2221, -70.5296),
    "San Cristóbal": (18.4167, -70.1058),
    "Boca Chica": (18.4500, -69.6000),
    "Baní": (18.2796, -70.3319),
    "Barahona": (18.2085, -71.1008),
    "Higüey": (18.6150, -68.7070),
    "San Francisco de Macorís": (19.3000, -70.2500),
    "Moca": (19.3935, -70.5256),
    "Nagua": (19.3832, -69.8474),
    "Samaná": (19.2056, -69.3369),
    "Monte Cristi": (19.8483, -71.6457),
    "Dajabón": (19.5488, -71.7083),
    "Mao": (19.5519, -71.0781),
    "Azua": (18.4530, -70.7349),
    "San Juan": (18.8059, -71.2299),
    "Elías Piña": (18.8750, -71.7000),
    "Independencia": (18.5000, -71.8500),
    "Pedernales": (18.0384, -71.7440),
    "Hato Mayor": (18.7630, -69.2568),
    "El Seibo": (18.7656, -69.0389),
    "Monte Plata": (18.8070, -69.7840),
    "Hermanas Mirabal": (19.3744, -70.4161),
    "Sánchez Ramírez": (19.0000, -70.1667),
    "Monseñor Nouel": (18.9167, -70.4167),
    "Espaillat": (19.3833, -70.5167),
    "Valverde": (19.5667, -70.9167),
    "Santiago Rodríguez": (19.4667, -71.3333)
}


# ============================================================
# SELECCIONAR PROVINCIA
# ============================================================

provincia = "San Pedro de Macorís"

latitud, longitud = provincias[
    provincia
]


print()

print("☁ SkyAI - Ubicación")

print(
    "Provincia:",
    provincia
)

print(
    "Latitud:",
    latitud
)

print(
    "Longitud:",
    longitud
)


# ============================================================
# CONSULTAR OPEN-METEO
# ============================================================

url = "https://api.open-meteo.com/v1/forecast"


parametros = {
    "latitude": latitud,
    "longitude": longitud,
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m"
    ],
    "timezone": "America/Santo_Domingo"
}


try:

    respuesta = requests.get(
        url,
        params=parametros,
        timeout=10
    )

    respuesta.raise_for_status()

    datos_clima = respuesta.json()


except requests.RequestException as error:

    print()

    print("❌ Error al consultar Open-Meteo:")

    print(error)

    raise SystemExit


# ============================================================
# OBTENER CONDICIONES ACTUALES
# ============================================================

temperatura_actual = (
    datos_clima["current"]["temperature_2m"]
)

humedad_nueva = (
    datos_clima["current"]["relative_humidity_2m"]
)

precipitacion_nueva = (
    datos_clima["current"]["precipitation"]
)

viento_nuevo = (
    datos_clima["current"]["wind_speed_10m"]
)


hora_actual = pd.to_datetime(
    datos_clima["current"]["time"]
)

hora_nueva = hora_actual.hour

dia_del_año_nuevo = (
    hora_actual.dayofyear
)

dia_semana_nuevo = (
    hora_actual.dayofweek
)


# ============================================================
# PREPARAR DATOS PARA SKYAI
# ============================================================

datos_nuevos = pd.DataFrame(
    {
        "temperature_2m": [
            temperatura_actual
        ],

        "relative_humidity_2m": [
            humedad_nueva
        ],

        "precipitation": [
            precipitacion_nueva
        ],

        "wind_speed_10m": [
            viento_nuevo
        ],

        "hora": [
            hora_nueva
        ],

        "dia_del_año": [
            dia_del_año_nuevo
        ],

        "día_semana": [
            dia_semana_nuevo
        ]
    }
)


# ============================================================
# HACER PREDICCIÓN
# ============================================================

temperatura_predicha = modelo.predict(
    datos_nuevos
)


# ============================================================
# MOSTRAR DATOS ACTUALES
# ============================================================

print()

print("☁ SkyAI - Datos actuales de Open-Meteo")

print(
    "Temperatura actual:",
    temperatura_actual,
    "°C"
)

print(
    "Humedad:",
    humedad_nueva,
    "%"
)

print(
    "Precipitación:",
    precipitacion_nueva,
    "mm"
)

print(
    "Viento:",
    viento_nuevo,
    "km/h"
)

print(
    "Hora:",
    hora_nueva
)


# ============================================================
# MOSTRAR PREDICCIÓN
# ============================================================

print()

print("☁ SkyAI - Nueva predicción")

print(
    "Temperatura predicha para la próxima hora:",
    round(
        temperatura_predicha[0],
        2
    ),
    "°C"
)