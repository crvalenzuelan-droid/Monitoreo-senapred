from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from html import unescape, escape
import json
import re


URL_SCRIPT = (
    "https://archivos.meteochile.gob.cl/"
    "portaldmc/meteochile/js/"
    "pronostico.js?version=1"
)

URL_FUENTE = (
    "https://www.meteochile.gob.cl/"
    "PortalDMC-web/pronostico_general.xhtml"
)

RUTA_JSON = (
    "meteochile_temperatura/"
    "pronostico_temperaturas.json"
)

RUTA_XML = (
    "meteochile_temperatura/"
    "pronostico_temperaturas.xml"
)


def limpiar_html(texto):

    valor = texto or ""

    # MeteoChile presenta algunos caracteres
    # con doble codificación HTML.
    for _ in range(3):
        nuevo_valor = unescape(valor)

        if nuevo_valor == valor:
            break

        valor = nuevo_valor

    return re.sub(
        r"\s+",
        " ",
        valor
    ).strip()


def extraer_texto(bloque, nombre_campo):

    patron = (
        rf"{re.escape(nombre_campo)}"
        rf"\s*:\s*.*?[\"']"
    )

    resultado = re.search(
        patron,
        bloque,
        flags=re.DOTALL
    )

    if not resultado:
        return ""

    return limpiar_html(
        resultado.group(1)
    )


def extraer_numero(bloque, nombre_campo):

    resultado = re.search(
        rf"{re.escape(nombre_campo)}"
        rf"\s*:\s*(-?\d+)",
        bloque
    )

    if not resultado:
        return None

    return int(
        resultado.group(1)
    )


def extraer_arreglo_texto(
    bloque,
    nombre_campo
):

    resultado = re.search(
        rf"{re.escape(nombre_campo)}"
        rf"\s*:\s*\[(.*?)\]",
        bloque,
        flags=re.DOTALL
    )

    if not resultado:
        return []

    contenido = resultado.group(1)

    valores = re.findall(
        r""".*?["']""",
        contenido,
        flags=re.DOTALL
    )

    return [
        limpiar_html(valor)
        for valor in valores
        if limpiar_html(valor)
    ]


def separar_temperatura(valor):

    texto = limpiar_html(valor)

    resultado = re.fullmatch(
        r"\s*(-?\d+(?:[.,]\d+)?)"
        r"\s*/\s*"
        r"(-?\d+(?:[.,]\d+)?)\s*",
        texto
    )

    if not resultado:

        return {
            "minima": None,
            "maxima": None
        }

    minima = float(
        resultado.group(1).replace(
            ",",
            "."
        )
    )

    maxima = float(
        resultado.group(2).replace(
            ",",
            "."
        )
    )

    return {
        "minima": minima,
        "maxima": maxima
    }


def clasificar_temperatura(maxima):

    if maxima is None:
        return "No disponible"

    if maxima >= 40:
        return "Condición crítica"

    if maxima >= 34:
        return "Calor intenso"

    if maxima >= 30:
        return "Preventivo"

    return "Normal"


def convertir_fecha(fecha_sql):

    if not fecha_sql:
        return ""

    try:

        fecha = datetime.strptime(
            fecha_sql,
            "%Y-%m-%d"
        )

        return fecha.strftime(
            "%d-%m-%Y"
        )

    except ValueError:

        return fecha_sql


with sync_playwright() as p:

    navegador = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features="
            "AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox"
        ]
    )

    contexto = navegador.new_context(
        locale="es-CL",
        timezone_id="America/Santiago",
        user_agent=(
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0.0.0 "
            "Safari/537.36"
        )
    )

    respuesta = contexto.request.get(
        URL_SCRIPT,
        timeout=120000,
        headers={
            "Accept": (
                "text/javascript,"
                "application/javascript,"
                "*/*;q=0.8"
            ),
            "Referer": URL_FUENTE
        }
    )

    print(
        "Estado de pronostico.js:",
        respuesta.status
    )

    if not respuesta.ok:

        navegador.close()

        raise RuntimeError(
            "No fue posible descargar "
            "pronostico.js. "
            f"Estado HTTP: {respuesta.status}"
        )

    contenido = respuesta.text()

    navegador.close()


if not contenido.strip():

    raise RuntimeError(
        "pronostico.js fue descargado, "
        "pero está vacío."
    )


bloques = re.findall(
    r"Pronostico\.push\s*\(\s*"
    r"\{(.*?)\}\s*\)\s*;",
    contenido,
    flags=re.DOTALL
)

print(
    "Localidades encontradas:",
    len(bloques)
)

pronosticos = []


for bloque in bloques:

    indice = extraer_texto(
        bloque,
        "indice"
    )

    ciudad = extraer_texto(
        bloque,
        "ciudad"
    )

    region = extraer_texto(
        bloque,
        "region"
    )

    fecha_sql = extraer_texto(
        bloque,
        "fechasql"
    )

    fecha_redaccion = extraer_texto(
        bloque,
        "fechasqlredaccion"
    )

    texto_resto_dia = extraer_texto(
        bloque,
        "texto_resto_dia"
    )

    fecha_resto_dia = extraer_texto(
        bloque,
        "fecha_resto_dia"
    )

    cantidad_dias = extraer_numero(
        bloque,
        "tope"
    )

    fechas = extraer_arreglo_texto(
        bloque,
        "fecha"
    )

    temperaturas = extraer_arreglo_texto(
        bloque,
        "temperatura"
    )

    if not indice or not ciudad:
        continue

    dias = []

    cantidad = max(
        len(fechas),
        len(temperaturas)
    )

    for posicion in range(cantidad):

        etiqueta_fecha = (
            fechas[posicion]
            if posicion < len(fechas)
            else ""
        )

        temperatura_texto = (
            temperaturas[posicion]
            if posicion < len(temperaturas)
            else ""
        )

        valores = separar_temperatura(
            temperatura_texto
        )

        dias.append({
            "posicion": posicion + 1,
            "fecha_etiqueta": etiqueta_fecha,
            "temperatura": temperatura_texto,
            "minima": valores["minima"],
            "maxima": valores["maxima"],
            "nivel_temperatura": (
                clasificar_temperatura(
                    valores["maxima"]
                )
            )
        })

    primer_dia = (
        dias[0]
        if dias
        else {
            "temperatura": "",
            "minima": None,
            "maxima": None,
            "nivel_temperatura": (
                "No disponible"
            )
        }
    )

    registro = {
        "indice": indice,
        "ciudad": ciudad,
        "region_codigo": region,
        "fecha_pronostico_iso": fecha_sql,
        "fecha_pronostico": (
            convertir_fecha(
                fecha_sql
            )
        ),
        "fecha_redaccion": fecha_redaccion,
        "cantidad_dias": cantidad_dias,
        "texto_resto_dia": texto_resto_dia,
        "fecha_resto_dia": fecha_resto_dia,
        "temperatura_primer_dia": (
            primer_dia["temperatura"]
        ),
        "temperatura_minima": (
            primer_dia["minima"]
        ),
        "temperatura_maxima": (
            primer_dia["maxima"]
        ),
        "nivel_temperatura": (
            primer_dia[
                "nivel_temperatura"
            ]
        ),
        "dias": dias
    }

    pronosticos.append(
        registro
    )

    print(
        f"OK: {ciudad} | "
        f"{fecha_sql} | "
        f"{primer_dia['temperatura']} | "
        f"{primer_dia['nivel_temperatura']}"
    )


if not pronosticos:

    raise RuntimeError(
        "No fue posible extraer localidades "
        "desde pronostico.js."
    )


pronosticos.sort(
    key=lambda item: (
        item["region_codigo"],
        item["ciudad"]
    )
)


fecha_referencia = next(
    (
        item["fecha_pronostico"]
        for item in pronosticos
        if item["fecha_pronostico"]
    ),
    datetime.now(
        timezone.utc
    ).strftime(
        "%d-%m
