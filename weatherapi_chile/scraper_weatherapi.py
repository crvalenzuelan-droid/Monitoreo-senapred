import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ZONA_HORARIA_CHILE = ZoneInfo("America/Santiago")
CARPETA_SALIDA = Path("weatherapi_chile")
ARCHIVO_JSON_COMPLETO = CARPETA_SALIDA / "pronostico_weatherapi_chile.json"
ARCHIVO_JSON_UV = CARPETA_SALIDA / "pronostico_uv_weatherapi.json"
ARCHIVO_XML_UV = CARPETA_SALIDA / "pronostico_uv_weatherapi.xml"
ARCHIVO_JSON_TEMPERATURAS = CARPETA_SALIDA / "pronostico_temperaturas_weatherapi.json"
ARCHIVO_XML_TEMPERATURAS = CARPETA_SALIDA / "pronostico_temperaturas_weatherapi.xml"
ARCHIVO_ESTADO = CARPETA_SALIDA / "estado_weatherapi.json"
URL_API = "https://api.weatherapi.com/v1/forecast.json"
MAXIMO_INTENTOS = 3
ESPERA_ENTRE_INTENTOS = 5
HORA_UV_REPORTE = "08:00"

CIUDADES = [
    {"region": "Arica y Parinacota", "ciudad": "Arica", "latitud": -18.4783, "longitud": -70.3126},
    {"region": "Tarapacá", "ciudad": "Iquique", "latitud": -20.2307, "longitud": -70.1357},
    {"region": "Antofagasta", "ciudad": "Antofagasta", "latitud": -23.6509, "longitud": -70.3975},
    {"region": "Atacama", "ciudad": "Copiapó", "latitud": -27.3668, "longitud": -70.3323},
    {"region": "Coquimbo", "ciudad": "La Serena", "latitud": -29.9027, "longitud": -71.2519},
    {"region": "Valparaíso", "ciudad": "Valparaíso", "latitud": -33.0472, "longitud": -71.6127},
    {"region": "Metropolitana", "ciudad": "Santiago", "latitud": -33.4489, "longitud": -70.6693},
    {"region": "O´Higgins", "ciudad": "Rancagua", "latitud": -34.1708, "longitud": -70.7444},
    {"region": "Maule", "ciudad": "Talca", "latitud": -35.4264, "longitud": -71.6554},
    {"region": "Ñuble", "ciudad": "Chillán", "latitud": -36.6066, "longitud": -72.1034},
    {"region": "Biobío", "ciudad": "Concepción", "latitud": -36.8201, "longitud": -73.0444},
    {"region": "La Araucanía", "ciudad": "Temuco", "latitud": -38.7359, "longitud": -72.5904},
    {"region": "Los Ríos", "ciudad": "Valdivia", "latitud": -39.8142, "longitud": -73.2459},
    {"region": "Los Lagos", "ciudad": "Puerto Montt", "latitud": -41.4693, "longitud": -72.9424},
    {"region": "Aysén", "ciudad": "Coyhaique", "latitud": -45.5752, "longitud": -72.0662},
    {"region": "Magallanes", "ciudad": "Punta Arenas", "latitud": -53.1638, "longitud": -70.9171},
]


def ahora_chile():
    return datetime.now(ZONA_HORARIA_CHILE)


def fecha_hoy_chile():
    return ahora_chile().strftime("%Y-%m-%d")


def fecha_hoy_local():
    return ahora_chile().strftime("%d-%m-%Y")


def fecha_rss():
    return ahora_chile().strftime("%a, %d %b %Y %H:%M:%S %z")


def proteger_cdata(texto):
    return "" if texto is None else str(texto).replace("]]>", "]]]]><![CDATA[>")


def validar_numero(valor, nombre, minimo, maximo):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} no es numerico: {valor}")
    if numero < minimo:
        raise ValueError(f"{nombre} menor al minimo: {numero}")
    if numero > maximo:
        raise ValueError(f"{nombre} mayor al maximo: {numero}")
    return numero


def clasificar_uv(valor_uv):
    uv = float(valor_uv or 0)
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
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(contenido, archivo, ensure_ascii=False, indent=2)


def escribir_texto(ruta, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)


def consultar_weatherapi(api_key, ciudad):
    coordenadas = f"{ciudad['latitud']},{ciudad['longitud']}"
    parametros = {"key": api_key, "q": coordenadas, "days": 1, "aqi": "no", "alerts": "no", "lang": "es"}
    url = f"{URL_API}?{urllib.parse.urlencode(parametros)}"
    ultimo_error = None
    for intento in range(1, MAXIMO_INTENTOS + 1):
        try:
            solicitud = urllib.request.Request(url, headers={"User-Agent": "Falabella-Prevencion-WeatherAPI/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(solicitud, timeout=45) as respuesta:
                if respuesta.getcode() != 200:
                    raise RuntimeError(f"WeatherAPI respondio HTTP {respuesta.getcode()}")
                datos = json.loads(respuesta.read().decode("utf-8"))
                if "error" in datos:
                    raise RuntimeError(f"WeatherAPI: {datos['error'].get('message', 'Error no identificado')}")
                return datos
        except Exception as error:
            ultimo_error = error
            print(f"Intento {intento} fallido para {ciudad['ciudad']}: {error}")
            if intento < MAXIMO_INTENTOS:
                time.sleep(ESPERA_ENTRE_INTENTOS)
    raise RuntimeError(f"No fue posible consultar {ciudad['ciudad']}: {ultimo_error}")


def obtener_uv_horario(horas, hora_objetivo=HORA_UV_REPORTE):
    registros_validos = []
    for hora in horas:
        try:
            uv = float(hora.get("uv"))
        except (TypeError, ValueError):
            continue
        hora_texto = str(hora.get("time", ""))[-5:]
        if len(hora_texto) != 5:
            continue
        registros_validos.append({"hora": hora_texto, "uv": uv})

    if not registros_validos:
        return None, None, None, None

    registro_objetivo = next((r for r in registros_validos if r["hora"] == hora_objetivo), None)
    if registro_objetivo is None:
        objetivo_minutos = int(hora_objetivo[:2]) * 60 + int(hora_objetivo[3:])
        registro_objetivo = min(
            registros_validos,
            key=lambda r: abs((int(r["hora"][:2]) * 60 + int(r["hora"][3:])) - objetivo_minutos),
        )

    registro_maximo = max(registros_validos, key=lambda r: r["uv"])
    return registro_objetivo["uv"], registro_objetivo["hora"], registro_maximo["uv"], registro_maximo["hora"]


def procesar_ciudad(ciudad, respuesta):
    location = respuesta.get("location", {})
    current = respuesta.get("current", {})
    forecastday = respuesta.get("forecast", {}).get("forecastday", [])
    if not forecastday:
        raise ValueError(f"Sin forecastday para {ciudad['ciudad']}")

    pronostico_dia = forecastday[0]
    fecha_api = pronostico_dia.get("date", "")
    if fecha_api != fecha_hoy_chile():
        raise ValueError(f"Fecha incorrecta para {ciudad['ciudad']}. WeatherAPI={fecha_api}, Chile={fecha_hoy_chile()}")

    day = pronostico_dia.get("day", {})
    horas = pronostico_dia.get("hour", [])
    temperatura_actual = validar_numero(current.get("temp_c"), "temperatura_actual", -40, 55)
    sensacion_termica = validar_numero(current.get("feelslike_c"), "sensacion_termica", -50, 65)
    temperatura_minima = validar_numero(day.get("mintemp_c"), "temperatura_minima", -40, 50)
    temperatura_maxima = validar_numero(day.get("maxtemp_c"), "temperatura_maxima", -35, 55)
    if temperatura_maxima < temperatura_minima:
        raise ValueError(f"Temperatura maxima menor que la minima en {ciudad['ciudad']}")

    uv_hora_reporte, hora_reporte_uv, uv_maximo_horario, hora_uv_maximo = obtener_uv_horario(horas)
    uv_diario = day.get("uv")
    if uv_diario is None:
        uv_diario = current.get("uv")
    uv_diario = validar_numero(uv_diario, "uv_diario_api", 0, 25)
    if uv_hora_reporte is None:
        uv_hora_reporte = validar_numero(current.get("uv", 0), "uv_hora_reporte", 0, 25)
        hora_reporte_uv = str(location.get("localtime", ""))[-5:] or HORA_UV_REPORTE
    else:
        uv_hora_reporte = validar_numero(uv_hora_reporte, "uv_hora_reporte", 0, 25)
    if uv_maximo_horario is None:
        uv_maximo_horario = uv_diario
        hora_uv_maximo = "No disponible"
    else:
        uv_maximo_horario = validar_numero(uv_maximo_horario, "uv_maximo_horario", 0, 25)

    # Mantiene compatibilidad: uv_maximo sigue siendo el mayor valor diario disponible.
    uv_maximo = validar_numero(max(uv_diario, uv_maximo_horario), "uv_maximo", 0, 25)

    humedad = validar_numero(current.get("humidity"), "humedad", 0, 100)
    viento_maximo = validar_numero(day.get("maxwind_kph"), "viento_maximo", 0, 250)
    try:
        probabilidad_lluvia = int(day.get("daily_chance_of_rain", 0))
    except (TypeError, ValueError):
        probabilidad_lluvia = 0

    return {
        "fecha_pronostico": fecha_api,
        "region": ciudad["region"],
        "ciudad_referencia": ciudad["ciudad"],
        "latitud": ciudad["latitud"],
        "longitud": ciudad["longitud"],
        "ubicacion_api": location.get("name", ciudad["ciudad"]),
        "pais_api": location.get("country", "Chile"),
        "hora_local_api": location.get("localtime", ""),
        "ultima_actualizacion_api": current.get("last_updated", ""),
        "temperatura_actual_c": round(temperatura_actual, 1),
        "temperatura_minima_c": round(temperatura_minima, 1),
        "temperatura_maxima_c": round(temperatura_maxima, 1),
        "sensacion_termica_c": round(sensacion_termica, 1),
        "humedad_porcentaje": round(humedad, 0),
        "viento_maximo_kmh": round(viento_maximo, 1),
        "probabilidad_lluvia_porcentaje": probabilidad_lluvia,
        "condicion": day.get("condition", {}).get("text", "No informada"),
        "uv_hora_reporte": round(uv_hora_reporte, 1),
        "hora_reporte_uv": hora_reporte_uv,
        "categoria_uv_hora": clasificar_uv(uv_hora_reporte),
        "uv_diario_api": round(uv_diario, 1),
        "uv_maximo_horario": round(uv_maximo_horario, 1),
        "hora_uv_maximo": hora_uv_maximo,
        "uv_maximo": round(uv_maximo, 1),
        "categoria_uv": clasificar_uv(uv_maximo),
    }


def validar_resultados(resultados, errores):
    if errores:
        raise RuntimeError("Existen errores regionales: " + " | ".join(errores))
    if len(resultados) != len(CIUDADES):
        raise RuntimeError(f"Se esperaban {len(CIUDADES)} regiones y se obtuvieron {len(resultados)}")
    faltantes = {c["region"] for c in CIUDADES} - {r["region"] for r in resultados}
    if faltantes:
        raise RuntimeError("Faltan regiones: " + ", ".join(sorted(faltantes)))
    fechas = {r["fecha_pronostico"] for r in resultados}
    if fechas != {fecha_hoy_chile()}:
        raise RuntimeError(f"Fechas inconsistentes: {fechas}")


def generar_json_completo(resultados):
    escribir_json(ARCHIVO_JSON_COMPLETO, {
        "fuente": "WeatherAPI.com",
        "fecha_pronostico": fecha_hoy_chile(),
        "fecha_generacion_chile": ahora_chile().isoformat(),
        "zona_horaria": "America/Santiago",
        "cantidad_regiones": len(resultados),
        "regiones": resultados,
    })


def generar_json_uv(resultados):
    escribir_json(ARCHIVO_JSON_UV, {
        "fuente": "WeatherAPI.com",
        "fecha_pronostico": fecha_hoy_chile(),
        "fecha_generacion_chile": ahora_chile().isoformat(),
        "hora_uv_reporte_referencia": HORA_UV_REPORTE,
        "maximo_nacional": max(r["uv_maximo"] for r in resultados),
        "regiones": [{
            "region": r["region"],
            "ciudad_referencia": r["ciudad_referencia"],
            "uv_hora_reporte": r["uv_hora_reporte"],
            "hora_reporte_uv": r["hora_reporte_uv"],
            "categoria_uv_hora": r["categoria_uv_hora"],
            "uv_diario_api": r["uv_diario_api"],
            "uv_maximo_horario": r["uv_maximo_horario"],
            "uv_maximo": r["uv_maximo"],
            "hora_uv_maximo": r["hora_uv_maximo"],
            "categoria": r["categoria_uv"],
        } for r in resultados],
    })


def generar_xml_uv(resultados):
    fecha_local = fecha_hoy_local()
    fecha_publicacion = fecha_rss()
    maximo_nacional = max(r["uv_maximo"] for r in resultados)
    categorias = {"Extremo": [], "Muy Alto": [], "Alto": [], "Moderado": [], "Bajo": []}
    for r in resultados:
        categorias.setdefault(r["categoria_uv"], []).append(f"{r['region']} ({r['uv_maximo']})")
    descripcion = (
        "Fuente=WeatherAPI.com"
        f"|FechaPronostico={fecha_local}"
        f"|MaximoNacional={maximo_nacional}"
        f"|Extremo={', '.join(categorias['Extremo'])}"
        f"|MuyAlto={', '.join(categorias['Muy Alto'])}"
        f"|Alto={', '.join(categorias['Alto'])}"
        f"|Moderado={', '.join(categorias['Moderado'])}"
        f"|Bajo={', '.join(categorias['Bajo'])}"
        "|NoDisponible="
    )
    guid = f"UV-NACIONAL-WEATHERAPI|{fecha_local}"
    item = f"""
<item>
<title><![CDATA[Pronóstico Nacional de Radiación UV WeatherAPI | {fecha_local}]]></title>
<link>https://www.weatherapi.com/</link>
<guid isPermaLink="false"><![CDATA[{proteger_cdata(guid)}]]></guid>
<description><![CDATA[{proteger_cdata(descripcion)}]]></description>
<pubDate>{fecha_publicacion}</pubDate>
</item>
"""
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Pronóstico Nacional Radiación UV WeatherAPI</title>
<link>https://www.weatherapi.com/</link>
<description>Pronóstico nacional diario de radiación UV</description>
<language>es-cl</language>
<lastBuildDate>{fecha_publicacion}</lastBuildDate>
{item}</channel></rss>
"""
    escribir_texto(ARCHIVO_XML_UV, rss)


def generar_json_temperaturas(resultados):
    escribir_json(ARCHIVO_JSON_TEMPERATURAS, {
        "fuente": "WeatherAPI.com",
        "fecha_pronostico": fecha_hoy_chile(),
        "fecha_generacion_chile": ahora_chile().isoformat(),
        "regiones": [{
            "region": r["region"],
            "ciudad_referencia": r["ciudad_referencia"],
            "temperatura_actual_c": r["temperatura_actual_c"],
            "temperatura_minima_c": r["temperatura_minima_c"],
            "temperatura_maxima_c": r["temperatura_maxima_c"],
            "sensacion_termica_c": r["sensacion_termica_c"],
            "humedad_porcentaje": r["humedad_porcentaje"],
            "viento_maximo_kmh": r["viento_maximo_kmh"],
            "probabilidad_lluvia_porcentaje": r["probabilidad_lluvia_porcentaje"],
            "condicion": r["condicion"],
            "uv_hora_reporte": r["uv_hora_reporte"],
            "hora_reporte_uv": r["hora_reporte_uv"],
            "categoria_uv_hora": r["categoria_uv_hora"],
            "uv_maximo": r["uv_maximo"],
            "hora_uv_maximo": r["hora_uv_maximo"],
            "categoria_uv_maximo": r["categoria_uv"],
        } for r in resultados],
    })


def generar_xml_temperaturas(resultados):
    fecha_local = fecha_hoy_local()
    fecha_publicacion = fecha_rss()
    items = ""
    for r in resultados:
        guid = f"TEMP-WEATHERAPI|{fecha_local}|{r['region']}"
        descripcion = (
            "Fuente=WeatherAPI.com"
            f"|FechaPronostico={fecha_local}"
            f"|Region={r['region']}"
            f"|CiudadReferencia={r['ciudad_referencia']}"
            f"|TemperaturaActual={r['temperatura_actual_c']}"
            f"|TemperaturaMinima={r['temperatura_minima_c']}"
            f"|TemperaturaMaxima={r['temperatura_maxima_c']}"
            f"|SensacionTermica={r['sensacion_termica_c']}"
            f"|Humedad={r['humedad_porcentaje']}"
            f"|VientoMaximo={r['viento_maximo_kmh']}"
            f"|ProbabilidadLluvia={r['probabilidad_lluvia_porcentaje']}"
            f"|Condicion={r['condicion']}"
            f"|UVHoraReporte={r['uv_hora_reporte']}"
            f"|HoraReporteUV={r['hora_reporte_uv']}"
            f"|CategoriaUVHora={r['categoria_uv_hora']}"
            f"|UVMaximo={r['uv_maximo']}"
            f"|HoraUVMaximo={r['hora_uv_maximo']}"
            f"|CategoriaUVMaximo={r['categoria_uv']}"
        )
        items += f"""
<item>
<title><![CDATA[Pronóstico Temperaturas | {proteger_cdata(r['region'])} | {fecha_local}]]></title>
<link>https://www.weatherapi.com/</link>
<guid isPermaLink="false"><![CDATA[{proteger_cdata(guid)}]]></guid>
<description><![CDATA[{proteger_cdata(descripcion)}]]></description>
<pubDate>{fecha_publicacion}</pubDate>
</item>
"""
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Pronóstico Temperaturas Chile WeatherAPI</title>
<link>https://www.weatherapi.com/</link>
<description>Pronóstico diario de temperaturas y UV por región de Chile</description>
<language>es-cl</language>
<lastBuildDate>{fecha_publicacion}</lastBuildDate>
{items}</channel></rss>
"""
    escribir_texto(ARCHIVO_XML_TEMPERATURAS, rss)


def escribir_estado(estado, mensaje, cantidad_regiones=0, errores=None):
    escribir_json(ARCHIVO_ESTADO, {
        "estado": estado,
        "mensaje": mensaje,
        "fecha_revision_chile": ahora_chile().isoformat(),
        "fecha_esperada": fecha_hoy_chile(),
        "cantidad_regiones": cantidad_regiones,
        "errores": errores or [],
    })


def main():
    api_key = os.environ.get("WEATHERAPI_KEY", "").strip()
    if not api_key:
        escribir_estado("ERROR", "No existe el secreto WEATHERAPI_KEY")
        print("ERROR: no existe WEATHERAPI_KEY.")
        return 1

    print("Iniciando pronostico WeatherAPI Chile")
    print(f"Fecha esperada en Chile: {fecha_hoy_chile()}")
    resultados, errores = [], []
    for indice, ciudad in enumerate(CIUDADES, start=1):
        print(f"[{indice}/{len(CIUDADES)}] Consultando {ciudad['ciudad']} ({ciudad['region']})")
        try:
            registro = procesar_ciudad(ciudad, consultar_weatherapi(api_key, ciudad))
            resultados.append(registro)
            print(
                f"OK | {registro['region']} | "
                f"UV {registro['hora_reporte_uv']}={registro['uv_hora_reporte']} {registro['categoria_uv_hora']} | "
                f"UV max {registro['uv_maximo']} {registro['categoria_uv']} a las {registro['hora_uv_maximo']} | "
                f"Min {registro['temperatura_minima_c']} C | Max {registro['temperatura_maxima_c']} C"
            )
        except Exception as error:
            mensaje_error = f"{ciudad['region']}: {error}"
            errores.append(mensaje_error)
            print(f"ERROR | {mensaje_error}")

    try:
        validar_resultados(resultados, errores)
    except Exception as error:
        escribir_estado("ERROR", str(error), len(resultados), errores)
        print(f"ERROR DE VALIDACION: {error}")
        print("No se generaran nuevos archivos de pronostico.")
        return 1

    generar_json_completo(resultados)
    generar_json_uv(resultados)
    generar_xml_uv(resultados)
    generar_json_temperaturas(resultados)
    generar_xml_temperaturas(resultados)
    escribir_estado("OK", "Pronostico generado correctamente", len(resultados))
    print("\nPronostico WeatherAPI generado correctamente.")
    print(f"Regiones procesadas: {len(resultados)}")
    print(f"Archivos guardados en: {CARPETA_SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
