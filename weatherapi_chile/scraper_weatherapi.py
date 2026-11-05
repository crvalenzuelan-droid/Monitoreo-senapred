import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


# ============================================================
# CONFIGURACION GENERAL
# ============================================================

ZONA_HORARIA_CHILE = ZoneInfo("America/Santiago")

CARPETA_SALIDA = Path("weatherapi_chile")

ARCHIVO_JSON_COMPLETO = (
    CARPETA_SALIDA / "pronostico_weatherapi_chile.json"
)

ARCHIVO_JSON_UV = (
    CARPETA_SALIDA / "pronostico_uv_weatherapi.json"
)

ARCHIVO_XML_UV = (
    CARPETA_SALIDA / "pronostico_uv_weatherapi.xml"
)

ARCHIVO_JSON_TEMPERATURAS = (
    CARPETA_SALIDA
    / "pronostico_temperaturas_weatherapi.json"
)

ARCHIVO_XML_TEMPERATURAS = (
    CARPETA_SALIDA
    / "pronostico_temperaturas_weatherapi.xml"
)

ARCHIVO_ESTADO = (
    CARPETA_SALIDA / "estado_weatherapi.json"
)

URL_API = (
    "https://api.weatherapi.com/v1/forecast.json"
)

MAXIMO_INTENTOS = 3
ESPERA_ENTRE_INTENTOS = 5


# ============================================================
# CIUDADES DE REFERENCIA
# ============================================================

CIUDADES = [
    {
        "region": "Arica y Parinacota",
        "ciudad": "Arica",
        "latitud": -18.4783,
        "longitud": -70.3126
    },
    {
        "region": "Tarapacá",
        "ciudad": "Iquique",
        "latitud": -20.2307,
        "longitud": -70.1357
    },
    {
        "region": "Antofagasta",
        "ciudad": "Antofagasta",
        "latitud": -23.6509,
        "longitud": -70.3975
    },
    {
        "region": "Atacama",
        "ciudad": "Copiapó",
        "latitud": -27.3668,
        "longitud": -70.3323
    },
    {
        "region": "Coquimbo",
        "ciudad": "La Serena",
        "latitud": -29.9027,
        "longitud": -71.2519
    },
    {
        "region": "Valparaíso",
        "ciudad": "Valparaíso",
        "latitud": -33.0472,
        "longitud": -71.6127
    },
    {
        "region": "Metropolitana",
        "ciudad": "Santiago",
        "latitud": -33.4489,
        "longitud": -70.6693
    },
    {
        "region": "O´Higgins",
        "ciudad": "Rancagua",
        "latitud": -34.1708,
        "longitud": -70.7444
    },
    {
        "region": "Maule",
        "ciudad": "Talca",
        "latitud": -35.4264,
        "longitud": -71.6554
    },
    {
        "region": "Ñuble",
        "ciudad": "Chillán",
        "latitud": -36.6066,
        "longitud": -72.1034
    },
    {
        "region": "Biobío",
        "ciudad": "Concepción",
        "latitud": -36.8201,
        "longitud": -73.0444
    },
    {
        "region": "La Araucanía",
        "ciudad": "Temuco",
        "latitud": -38.7359,
        "longitud": -72.5904
    },
    {
        "region": "Los Ríos",
        "ciudad": "Valdivia",
        "latitud": -39.8142,
        "longitud": -73.2459
    },
    {
        "region": "Los Lagos",
        "ciudad": "Puerto Montt",
        "latitud": -41.4693,
        "longitud": -72.9424
    },
    {
        "region": "Aysén",
        "ciudad": "Coyhaique",
        "latitud": -45.5752,
        "longitud": -72.0662
    },
    {
        "region": "Magallanes",
        "ciudad": "Punta Arenas",
        "latitud": -53.1638,
        "longitud": -70.9171
    }
]


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def ahora_chile():
    return datetime.now(ZONA_HORARIA_CHILE)


def fecha_hoy_chile():
    return ahora_chile().strftime("%Y-%m-%d")


def fecha_hoy_local():
    return ahora_chile().strftime("%d-%m-%Y")


def fecha_rss():
    return ahora_chile().strftime(
        "%a, %d %b %Y %H:%M:%S %z"
    )


def proteger_cdata(texto):
    if texto is None:
        return ""

    return str(texto).replace(
        "]]>",
        "]]]]><![CDATA[>"
    )


def validar_numero(
    valor,
    nombre,
    minimo,
    maximo
):
    try:
        numero = float(valor)

    except (TypeError, ValueError):
        raise ValueError(
            f"{nombre} no es numerico: {valor}"
        )

    if numero < minimo or numero > maximo:
        raise ValueError(
            f"{nombre} fuera de rango: {numero}"
        )

    return numero


def clasificar_uv(valor_uv):
    uv = float(valor_uv)

    if uv < 3:
        return "Bajo"

    if uv < 6:
        return "Moderado"

    if uv < 8:
        return "Alto"

    if uv < 11:
        return "Muy Alto"

    return "Extremo"


def escribir_json(ruta, contenido):
    ruta.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            contenido,
            archivo,
            ensure_ascii=False,
            indent=2
        )


def escribir_texto(ruta, contenido):
    ruta.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(contenido)


# ============================================================
# CONSULTA WEATHERAPI
# ============================================================

def consultar_weatherapi(
    api_key,
    ciudad
):
    coordenadas = (
        f"{ciudad['latitud']},"
        f"{ciudad['longitud']}"
    )

    parametros = {
        "key": api_key,
        "q": coordenadas,
        "days": 1,
        "aqi": "no",
        "alerts": "no",
        "lang": "es"
    }

    url = (
        f"{URL_API}?"
        f"{urllib.parse.urlencode(parametros)}"
    )

    ultimo_error = None

    for intento in range(
        1,
        MAXIMO_INTENTOS + 1
    ):
        try:
            solicitud = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Falabella-Prevencion-"
                        "WeatherAPI/1.0"
                    ),
                    "Accept": "application/json"
                }
            )

            with urllib.request.urlopen(
                solicitud,
                timeout=45
            ) as respuesta:

                codigo = respuesta.getcode()

                if codigo != 200:
                    raise RuntimeError(
                        "WeatherAPI respondio "
                        f"HTTP {codigo}"
                    )

                contenido = (
                    respuesta.read().decode("utf-8")
                )

                datos = json.loads(contenido)

                if "error" in datos:
                    mensaje = datos["error"].get(
                        "message",
                        "Error no identificado"
                    )

                    raise RuntimeError(
                        f"WeatherAPI: {mensaje}"
                    )

                return datos

        except Exception as error:
            ultimo_error = error

            print(
                f"Intento {intento} fallido para "
                f"{ciudad['ciudad']}: {error}"
            )

            if intento < MAXIMO_INTENTOS:
                time.sleep(
                    ESPERA_ENTRE_INTENTOS
                )

    raise RuntimeError(
        "No fue posible consultar "
        f"{ciudad['ciudad']}: {ultimo_error}"
    )


# ============================================================
# PROCESAMIENTO POR CIUDAD
# ============================================================

def procesar_ciudad(
    ciudad,
    respuesta
):
    location = respuesta.get(
        "location",
        {}
    )

    current = respuesta.get(
        "current",
        {}
    )

    forecast = respuesta.get(
        "forecast",
        {}
    )

    forecastday = forecast.get(
        "forecastday",
        []
    )

    if not forecastday:
        raise ValueError(
            "Sin forecastday para "
            f"{ciudad['ciudad']}"
        )

    pronostico_dia = forecastday[0]

    fecha_api = pronostico_dia.get(
        "date",
        ""
    )

    fecha_esperada = fecha_hoy_chile()

    if fecha_api != fecha_esperada:
        raise ValueError(
            "Fecha incorrecta para "
            f"{ciudad['ciudad']}. "
            f"WeatherAPI={fecha_api}, "
            f"Chile={fecha_esperada}"
        )

    day = pronostico_dia.get(
        "day",
        {}
    )

    horas = pronostico_dia.get(
        "hour",
        []
    )

    temperatura_actual = validar_numero(
        current.get("temp_c"),
        "temperatura_actual",
        -40,
        55
    )

    sensacion_termica = validar_numero(
        current.get("feelslike_c"),
        "sensacion_termica",
        -50,
        65
    )

    temperatura_minima = validar_numero(
        day.get("mintemp_c"),
        "temperatura_minima",
        -40,
        50
    )

    temperatura_maxima = validar_numero(
        day.get("maxtemp_c"),
        "temperatura_maxima",
        -35,
        55
    )

    if temperatura_maxima < temperatura_minima:
        raise ValueError(
            "Temperatura maxima menor que "
            f"la minima en {ciudad['ciudad']}"
        )

    valores_uv_horarios = []

    for hora in horas:
        valor_uv = hora.get("uv")

        if valor_uv is None:
            continue

        try:
            valores_uv_horarios.append(
                float(valor_uv)
            )

        except (TypeError, ValueError):
            continue

    uv_diario = day.get("uv")

    if uv_diario is None:
        uv_diario = current.get("uv")

    valores_uv_disponibles = []

    if uv_diario is not None:
        valores_uv_disponibles.append(
            float(uv_diario)
        )

    valores_uv_disponibles.extend(
        valores_uv_horarios
    )

    if not valores_uv_disponibles:
        raise ValueError(
            "Sin indice UV para "
            f"{ciudad['ciudad']}"
        )

    uv_maximo = max(
        valores_uv_disponibles
    )

    uv_maximo = validar_numero(
        uv_maximo,
        "uv_maximo",
        0,
        25
    )

    condicion = (
        day.get("condition", {})
        .get("text", "No informada")
    )

    humedad = validar_numero(
        current.get("humidity"),
        "humedad",
        0,
        100
    )

    viento_maximo = validar_numero(
        day.get("maxwind_kph"),
        "viento_maximo",
        0,
        250
    )

    probabilidad_lluvia = day.get(
        "daily_chance_of_rain",
        0
    )

    try:
        probabilidad_lluvia = int(
            probabilidad_lluvia
        )

    except (TypeError, ValueError):
        probabilidad_lluvia = 0

    hora_local_api = location.get(
        "localtime",
        ""
    )

    ultima_actualizacion = current.get(
        "last_updated",
        ""
    )

    return {
        "fecha_pronostico": fecha_api,
        "region": ciudad["region"],
        "ciudad_referencia": ciudad["ciudad"],
        "latitud": ciudad["latitud"],
        "longitud": ciudad["longitud"],
        "ubicacion_api": location.get(
            "name",
            ciudad["ciudad"]
        ),
        "pais_api": location.get(
            "country",
            "Chile"
        ),
        "hora_local_api": hora_local_api,
        "ultima_actualizacion_api": (
            ultima_actualizacion
        ),
        "temperatura_actual_c": round(
            temperatura_actual,
            1
        ),
        "temperatura_minima_c": round(
            temperatura_minima,
            1
        ),
        "temperatura_maxima_c": round(
            temperatura_maxima,
            1
        ),
        "sensacion_termica_c": round(
            sensacion_termica,
            1
        ),
        "humedad_porcentaje": round(
            humedad,
            0
        ),
        "viento_maximo_kmh": round(
            viento_maximo,
            1
        ),
        "probabilidad_lluvia_porcentaje": (
            probabilidad_lluvia
        ),
        "condicion": condicion,
        "uv_maximo": round(
            uv_maximo,
            1
        ),
        "categoria_uv": clasificar_uv(
            uv_maximo
        )
    }


# ============================================================
# VALIDACION NACIONAL
# ============================================================

def validar_resultados(
    resultados,
    errores
):
    if errores:
        raise RuntimeError(
            "Existen errores regionales: "
            + " | ".join(errores)
        )

    if len(resultados) != len(CIUDADES):
        raise RuntimeError(
            f"Se esperaban {len(CIUDADES)} "
            "regiones y se obtuvieron "
            f"{len(resultados)}"
        )

    regiones_obtenidas = {
        registro["region"]
        for registro in resultados
    }

    regiones_esperadas = {
        ciudad["region"]
        for ciudad in CIUDADES
    }

    faltantes = (
        regiones_esperadas
        - regiones_obtenidas
    )

    if faltantes:
        raise RuntimeError(
            "Faltan regiones: "
            + ", ".join(
                sorted(faltantes)
            )
        )

    fechas = {
        registro["fecha_pronostico"]
        for registro in resultados
    }

    if fechas != {fecha_hoy_chile()}:
        raise RuntimeError(
            f"Fechas inconsistentes: {fechas}"
        )


# ============================================================
# JSON COMPLETO
# ============================================================

def generar_json_completo(resultados):
    contenido = {
        "fuente": "WeatherAPI.com",
        "fecha_pronostico": fecha_hoy_chile(),
        "fecha_generacion_chile": (
            ahora_chile().isoformat()
        ),
        "zona_horaria": "America/Santiago",
        "cantidad_regiones": len(resultados),
        "regiones": resultados
    }

    escribir_json(
        ARCHIVO_JSON_COMPLETO,
        contenido
    )


# ============================================================
# PRODUCTO UV
# ============================================================

def generar_json_uv(resultados):
    maximo_nacional = max(
        registro["uv_maximo"]
        for registro in resultados
    )

    contenido = {
        "fuente": "WeatherAPI.com",
        "fecha_pronostico": fecha_hoy_chile(),
        "fecha_generacion_chile": (
            ahora_chile().isoformat()
        ),
        "maximo_nacional": maximo_nacional,
        "regiones": [
            {
                "region": registro["region"],
                "ciudad_referencia": (
                    registro["ciudad_referencia"]
                ),
                "uv_maximo": registro["uv_maximo"],
                "categoria": (
                    registro["categoria_uv"]
                )
            }
            for registro in resultados
        ]
    }

    escribir_json(
        ARCHIVO_JSON_UV,
        contenido
    )


def generar_xml_uv(resultados):
    fecha_local = fecha_hoy_local()
    fecha_publicacion = fecha_rss()

    maximo_nacional = max(
        registro["uv_maximo"]
        for registro in resultados
    )

    items = ""

    for registro in resultados:
        guid = (
            "UV-WEATHERAPI|"
            f"{fecha_local}|"
            f"{registro['region']}"
        )

        descripcion = (
            "Fuente=WeatherAPI.com"
            f"|FechaPronostico={fecha_local}"
            f"|Region={registro['region']}"
            "|CiudadReferencia="
            f"{registro['ciudad_referencia']}"
            f"|UVMaximo={registro['uv_maximo']}"
            f"|Categoria={registro['categoria_uv']}"
            f"|MaximoNacional={maximo_nacional}"
        )

        items += f"""
<item>
<title><![CDATA[Pronóstico UV | {proteger_cdata(registro['region'])} | {fecha_local}]]></title>
<link>https://www.weatherapi.com/</link>
<guid isPermaLink="false"><![CDATA[{proteger_cdata(guid)}]]></guid>
<description><![CDATA[{proteger_cdata(descripcion)}]]></description>
<pubDate>{fecha_publicacion}</pubDate>
</item>
"""

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Pronóstico UV Chile WeatherAPI</title>
<link>https://www.weatherapi.com/</link>
<description>Pronóstico diario UV por región de Chile</description>
<language>es-cl</language>
<lastBuildDate>{fecha_publicacion}</lastBuildDate>
{items}
</channel>
</rss>
"""

    escribir_texto(
        ARCHIVO_XML_UV,
        rss
    )


# ============================================================
# PRODUCTO TEMPERATURAS
# ============================================================

def generar_json_temperaturas(
    resultados
):
    contenido = {
        "fuente": "WeatherAPI.com",
        "fecha_pronostico": fecha_hoy_chile(),
        "fecha_generacion_chile": (
            ahora_chile().isoformat()
        ),
        "regiones": [
            {
                "region": registro["region"],
                "ciudad_referencia": (
                    registro["ciudad_referencia"]
                ),
                "temperatura_actual_c": (
                    registro["temperatura_actual_c"]
                ),
                "temperatura_minima_c": (
                    registro["temperatura_minima_c"]
                ),
                "temperatura_maxima_c": (
                    registro["temperatura_maxima_c"]
                ),
                "sensacion_termica_c": (
                    registro["sensacion_termica_c"]
                ),
                "humedad_porcentaje": (
                    registro["humedad_porcentaje"]
                ),
                "viento_maximo_kmh": (
                    registro["viento_maximo_kmh"]
                ),
                "probabilidad_lluvia_porcentaje": (
                    registro[
                        "probabilidad_lluvia_porcentaje"
                    ]
                ),
                "condicion": registro["condicion"]
            }
            for registro in resultados
        ]
    }

    escribir_json(
        ARCHIVO_JSON_TEMPERATURAS,
        contenido
    )


def generar_xml_temperaturas(
    resultados
):
    fecha_local = fecha_hoy_local()
    fecha_publicacion = fecha_rss()

    items = ""

    for registro in resultados:
        guid = (
            "TEMP-WEATHERAPI|"
            f"{fecha_local}|"
            f"{registro['region']}"
        )

        descripcion = (
            "Fuente=WeatherAPI.com"
            f"|FechaPronostico={fecha_local}"
            f"|Region={registro['region']}"
            "|CiudadReferencia="
            f"{registro['ciudad_referencia']}"
            "|TemperaturaActual="
            f"{registro['temperatura_actual_c']}"
            "|TemperaturaMinima="
            f"{registro['temperatura_minima_c']}"
            "|TemperaturaMaxima="
            f"{registro['temperatura_maxima_c']}"
            "|SensacionTermica="
            f"{registro['sensacion_termica_c']}"
            "|Humedad="
            f"{registro['humedad_porcentaje']}"
            "|VientoMaximo="
            f"{registro['viento_maximo_kmh']}"
            "|ProbabilidadLluvia="
            f"{registro['probabilidad_lluvia_porcentaje']}"
            f"|Condicion={registro['condicion']}"
        )

        items += f"""
<item>
<title><![CDATA[Pronóstico Temperaturas | {proteger_cdata(registro['region'])} | {fecha_local}]]></title>
<link>https://www.weatherapi.com/</link>
<guid isPermaLink="false"><![CDATA[{proteger_cdata(guid)}]]></guid>
<description><![CDATA[{proteger_cdata(descripcion)}]]></description>
<pubDate>{fecha_publicacion}</pubDate>
</item>
"""

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Pronóstico Temperaturas Chile WeatherAPI</title>
<link>https://www.weatherapi.com/</link>
<description>Pronóstico diario de temperaturas por región de Chile</description>
<language>es-cl</language>
<lastBuildDate>{fecha_publicacion}</lastBuildDate>
{items}
</channel>
</rss>
"""

    escribir_texto(
        ARCHIVO_XML_TEMPERATURAS,
        rss
    )


# ============================================================
# ESTADO DEL PROCESO
# ============================================================

def escribir_estado(
    estado,
    mensaje,
    cantidad_regiones=0,
    errores=None
):
    contenido = {
        "estado": estado,
        "mensaje": mensaje,
        "fecha_revision_chile": (
            ahora_chile().isoformat()
        ),
        "fecha_esperada": fecha_hoy_chile(),
        "cantidad_regiones": cantidad_regiones,
        "errores": errores or []
    }

    escribir_json(
        ARCHIVO_ESTADO,
        contenido
    )


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

def main():
    api_key = os.environ.get(
        "WEATHERAPI_KEY",
        ""
    ).strip()

    if not api_key:
        escribir_estado(
            estado="ERROR",
            mensaje=(
                "No existe el secreto "
                "WEATHERAPI_KEY"
            )
        )

        print(
            "ERROR: no existe WEATHERAPI_KEY."
        )

        return 1

    print(
        "Iniciando pronostico WeatherAPI Chile"
    )

    print(
        "Fecha esperada en Chile: "
        f"{fecha_hoy_chile()}"
    )

    resultados = []
    errores = []

    for indice, ciudad in enumerate(
        CIUDADES,
        start=1
    ):
        print(
            f"[{indice}/{len(CIUDADES)}] "
            f"Consultando {ciudad['ciudad']} "
            f"({ciudad['region']})"
        )

        try:
            respuesta = consultar_weatherapi(
                api_key,
                ciudad
            )

            registro = procesar_ciudad(
                ciudad,
                respuesta
            )

            resultados.append(
                registro
            )

            print(
                f"OK | {registro['region']} | "
                f"UV {registro['uv_maximo']} "
                f"{registro['categoria_uv']} | "
                "Min "
                f"{registro['temperatura_minima_c']} C | "
                "Max "
                f"{registro['temperatura_maxima_c']} C"
            )

        except Exception as error:
            mensaje_error = (
                f"{ciudad['region']}: {error}"
            )

            errores.append(
                mensaje_error
            )

            print(
                f"ERROR | {mensaje_error}"
            )

    try:
        validar_resultados(
            resultados,
            errores
        )

    except Exception as error:
        escribir_estado(
            estado="ERROR",
            mensaje=str(error),
            cantidad_regiones=len(resultados),
            errores=errores
        )

        print(
            f"ERROR DE VALIDACION: {error}"
        )

        print(
            "No se generaran nuevos archivos "
            "de pronostico."
        )

        return 1

    generar_json_completo(
        resultados
    )

    generar_json_uv(
        resultados
    )

    generar_xml_uv(
        resultados
    )

    generar_json_temperaturas(
        resultados
    )

    generar_xml_temperaturas(
        resultados
    )

    escribir_estado(
        estado="OK",
        mensaje=(
            "Pronostico generado correctamente"
        ),
        cantidad_regiones=len(resultados)
    )

    print("")
    print(
        "Pronostico WeatherAPI generado "
        "correctamente."
    )

    print(
        "Regiones procesadas: "
        f"{len(resultados)}"
    )

    print(
        "Archivos guardados en: "
        f"{CARPETA_SALIDA}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
