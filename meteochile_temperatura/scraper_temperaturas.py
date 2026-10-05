from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from html import escape, unescape
import json
import re
import time


# =================================================
# CONFIGURACION
# =================================================

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


# =================================================
# FUNCIONES DE LIMPIEZA
# =================================================

def limpiar_html(texto):

    valor = texto or ""

    # Algunos nombres vienen codificados
    # más de una vez.
    #
    # Ejemplo:
    # Copiap&amp;oacute;
    # se transforma en:
    # Copiapó

    for _ in range(4):

        nuevo_valor = unescape(
            valor
        )

        if nuevo_valor == valor:
            break

        valor = nuevo_valor

    return re.sub(
        r"\s+",
        " ",
        valor
    ).strip()


# =================================================
# EXTRACCION DE CAMPOS SIMPLES
# =================================================

def extraer_texto(
    bloque,
    nombre_campo
):

    resultado = re.search(
        rf"\b{re.escape(nombre_campo)}"
        rf"\s*:\s*([\"'])(.*?)\1",
        bloque,
        flags=re.DOTALL
    )

    if not resultado:
        return ""

    return limpiar_html(
        resultado.group(2)
    )


def extraer_numero(
    bloque,
    nombre_campo
):

    resultado = re.search(
        rf"\b{re.escape(nombre_campo)}"
        rf"\s*:\s*(-?\d+)",
        bloque
    )

    if not resultado:
        return None

    return int(
        resultado.group(1)
    )


# =================================================
# EXTRACCION DE ARREGLOS
# =================================================

def extraer_arreglo_texto(
    bloque,
    nombre_campo
):

    resultado = re.search(
        rf"\b{re.escape(nombre_campo)}"
        rf"\s*:\s*\[(.*?)\]",
        bloque,
        flags=re.DOTALL
    )

    if not resultado:
        return []

    contenido = resultado.group(1)

    valores = re.findall(
        r"([\"'])(.*?)\1",
        contenido*
        flags=re.DOTALL
    )

  * return [
        limpiar_html(valor)
        for _, valor in valores*        if limpiar_html(valor)
   *]


# ============================*====================
# PROCESAR TE*PERATURAS
# ======================*==========================

def co*vertir_numero(valor):

    if valo* is None:
        return None

   *texto = str(
        valor
    ).s*rip()

    if not texto:
        r*turn None

    try:

        return float(
            texto.replace(
                ",",
                "."
            )
        )

    except ValueError:

        return None


def separar_temperatura(valor):

    texto = limpiar_html(
        valor
    )

    # ---------------------------------------------
    # FORMATO COMPLETO
    #
    # Ejemplo:
    # 10/23
    #
    # Resultado:
    # mínima = 10
    # máxima = 23
    # ---------------------------------------------

    resultado_completo = re.fullmatch(
        r"\s*(-?\d+(?:[.,]\d+)?)"
        r"\s*/\s*"
        r"(-?\d+(?:[.,]\d+)?)\s*",
        texto
    )

    if *esultado_completo:

        minima*= convertir_numero(
            resultado_completo.group(1)
        )

        maxima = convertir_numero(
            resultado_completo.group(2)
        )

        return {
            "minima": minima,
            "maxima": maxima
        }

    # ---------------------------------------------
    # FORMATO SIN MINIMA
    #
    # Ejemplo:
    # /23
    #
    # Resultado:
    # mínima = None
    # máxima = 23
    # ---------------------------------------------

    resultado_solo_maxima = re.fullmatch(
        r"\s*/\s*"
        r"(-?\d+(?:[.,]\d+)?)\s*",
        texto
    )

    if resultado_solo_maxima:

        maxima = convertir_numero(
            resultado_solo_maxima.group(1)
        )

        return {
            "minima": None,
            "maxima": maxima
        }

    # ---------------------------------------------
    # FORMATO SIN MAXIMA
    #
    # Ejemplo:
    # 10/
    #
    # Resultado:
    # mínima = 10
    # máxima = None
    # ---------------------------------------------

    resultado_solo_minima = re.fullmatch(
        r"\s*(-?\d+(?:[.,]\d+)?)"
        r"\s*/\s*",
        texto
    )

    if resultado_solo_minima:

        minima = convertir_numero(
            resultado_solo_minima.group(1)
        )

        return {
            "minima": minima,
            "maxima": None
        }

    # ---------------------------------------------
    # FORMATO DE UN SOLO NUMERO
    #
    # Si MeteoChile entrega solamente un valor
    # sin separador, se interpreta como máxima.
    # ---------------------------------------------

    resultado_un_valor = re.fullmatch(
        r"\s*(-?\d+(?:[.,]\d+)?)\s*",
        texto
    )

    if resultado_un_valor:

        maxima = convertir_numero(
            resultado_un_valor.group(1)
        )

        return {
            "minima": None,
            "maxima": maxima
        }

    return {
        "minima": None,
        "maxima": None
    }


# =================================================
# CLASIFICACION PREVENTIVA
# =================================================

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


# =================================================
# CONVERSION DE FECHA
# =================================================

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


# =================================================
# DESCARGAR PRONOSTICO.JS
# =================================================

def descargar_pronostico():

    ultimo_error = ""

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

        contenido = ""

        for intento in range(
            1,
            4
        ):

            try:

                respuesta = (
                    contexto.request.get(
                        URL_SCRIPT,
                        timeout=120000,
                        headers={
                            "Accept": (
                                "text/javascript,"
                                "application/javascript,"
                                "*/*;q=0.8"
                            ),
                            "Referer": URL_FUENTE,
                            "Cache-Control": (
                                "no-cache"
                            ),
                            "Pragma": (
                                "no-cache"
                            )
                        }
                    )
                )

                print(
                    f"Intento {intento}: "
                    "estado de pronostico.js: "
                    f"{respuesta.status}"
                )

                if respuesta.ok:

                    contenido = (
                        respuesta.text()
                    )

                    if contenido.strip():
                        break

                ultimo_error = (
                    "Respuesta HTTP "
                    f"{respuesta.status}"
                )

            except 
