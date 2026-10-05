"""Traduce los códigos meteorológicos de Open-Meteo a mensajes para SkyAI."""


def interpretar_clima(codigo: int, temperatura: float, viento: float, precipitacion: float) -> dict:
    """Devuelve un estado corto y una recomendación fácil de entender."""
    estados = {
        0: ("☀️ Despejado", "Cielo despejado. Buen momento para actividades al aire libre."),
        1: ("🌤️ Mayormente despejado", "El tiempo se mantiene estable; disfruta el día al aire libre."),
        2: ("⛅ Parcialmente nublado", "Hay algunas nubes, pero las condiciones siguen siendo favorables."),
        3: ("☁️ Nublado", "Cielo cubierto. Considera llevar una prenda ligera."),
        45: ("🌫️ Niebla", "La visibilidad puede reducirse. Conduce con precaución."),
        48: ("🌫️ Niebla con escarcha", "La visibilidad puede reducirse. Conduce con precaución."),
        51: ("🌦️ Llovizna ligera", "Podría caer una llovizna; lleva paraguas si sales."),
        53: ("🌦️ Llovizna moderada", "Lleva paraguas o impermeable si vas a salir."),
        55: ("🌧️ Llovizna intensa", "Conviene posponer actividades al aire libre y llevar impermeable."),
        61: ("🌧️ Lluvia ligera", "Hay lluvia ligera. Lleva paraguas."),
        63: ("🌧️ Lluvia moderada", "La lluvia puede afectar tus traslados; lleva paraguas."),
        65: ("🌧️ Lluvia fuerte", "Evita zonas inundables y conduce con mucha precaución."),
        80: ("🌦️ Chubascos ligeros", "Puede llover por momentos. Lleva paraguas."),
        81: ("🌧️ Chubascos moderados", "Hay chubascos en la zona; planifica tus traslados."),
        82: ("⛈️ Chubascos fuertes", "Evita actividades al aire libre y mantente atento a alertas locales."),
        95: ("⛈️ Tormenta", "Busca un lugar seguro y evita áreas abiertas."),
        96: ("⛈️ Tormenta con granizo", "Permanece bajo techo y sigue las alertas locales."),
        99: ("⛈️ Tormenta fuerte con granizo", "Permanece bajo techo y sigue las alertas locales."),
    }

    estado, recomendacion = estados.get(codigo, ("🌡️ Condiciones actuales", "Consulta los indicadores del dashboard antes de salir."))
    if viento >= 35:
        recomendacion = "Hay viento fuerte. Asegura objetos exteriores y conduce con precaución."
    elif precipitacion > 0 and codigo <= 3:
        recomendacion = "Se registra precipitación. Lleva paraguas si vas a salir."
    elif temperatura >= 34:
        recomendacion = "Temperatura alta. Mantente hidratado y evita el sol intenso al mediodía."
    return {"estado": estado, "recomendacion": recomendacion}
