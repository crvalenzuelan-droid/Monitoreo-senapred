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

    for _ in range(4):

        nuevo_valor = unescape(valor)

        if nuevo_valor == valor:
            break

        valor = nuevo_valor

    return re.sub(
        r"\s+",
        " ",
        valor
    ).strip()


# =================================================
# EXTRACCION DE CAMPOS
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
# PROCESAMIENTO DE TEMPERATURAS
# =================================================

def convertir_numero(valor):

    if valor is None:
        return None

    texto = str(valor).strip()

    if not texto:
        return None

    try:

        return float(
            texto.replace(",", ".")
        )

    except ValueError:

        return None


def separar_temperatura(valor):

    texto = limpiar_html(valor)

    # Formato completo: 10/23
    resultado_completo = re.fullmatch(
        r"\s*(-?\d+(?:[.,]\d+)?)"
        r"\s*/\s*"
        r"(-?\d+(?:[.,]\d+)?)\s*",
        texto
    )

    if resultado_completo:

        return {
            "minima": convertir_numero(
                resultado_completo.group(1)
            ),
            "maxima": convertir_numero(
                resultado_completo.group(2)
            )
        }

    # Formato sin minima: /23
    resultado_solo_maxima = re.fullmatch(
        r"\s*/\s*"
        r"(-?\d+(?:[.,]\d+)?)\s*",
        texto
    )

    if resultado_solo_maxima:

        return {
            "minima": None,
            "maxima": convertir_numero(
                resultado_solo_maxima.group(1)
            )
        }

    # Formato sin maxima: 10/
    resultado_solo_minima = re.fullmatch(
        r"\s*(-?\d+(?:[.,]\d+)?)"
        r"\s*/\s*",
        texto
    )

    if resultado_solo_minima:

        return {
            "minima": convertir_numero(
                resultado_solo_minima.group(1)
            ),
            "maxima": None
        }

    # Un solo valor se interpreta como maxima
    resultado_un_valor = re.fullmatch(
        r"\s*(-?\d+(?:[.,]\d+)?)\s*",
        texto
    )

    if res*ltado_un_valor:

        return {
*           "minima": None,
       *    "maxima": convertir_numero(
  *             resultado_un_valor.gr*up(1)
            )
        }

   *return {
        "minima": None,
 *      "maxima": None
    }


def c*asificar_temperatura(maxima):

   *if maxima is None:
        return *No disponible"

    if maxima >= 4*:
        return "Condición crític*"

    if maxima >= 34:
        re*urn "Calor intenso"

    if maxima*>= 30:
        return "Preventivo"*
    return "Normal"


# =========*==================================*====
# CONVERSION DE FECHA
# =====*==================================*========

def convertir_fecha(fech*_sql):

    if not fecha_sql:
    *   return ""

    try:

        fe*ha = datetime.strptime(
          * fecha_sql,
            "%Y-%m-%d"*        )

        return fecha.st*ftime(
            "%d-%m-%Y"
    *   )

    except ValueError:

    *   return fecha_sql


# ==========*==================================*===
# DESCARGAR PRONOSTICO.JS
# ==*==================================*===========

def descargar_pronost*co():

    ultimo_error = ""

    *ith sync_playwright() as p:

     *  navegador = p.chromium.launch(
 *          headless=True,
         *  args=[
                "--disable-blink-features="
                "AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]
        )

        contexto * navegador.new_context(
          * locale="es-CL",
            timez*ne_id="America/Santiago",
        *   user_agent=(
                "M*zilla/5.0 "
                "(Wind*ws NT 10.0; Win64; x64) "
        *       "AppleWebKit/537.36 "
     *          "(KHTML, like Gecko) "
                "Chrome/140.0.0.0 "
                "Safari/537.36"
            )
        )

        contenido = ""

        for intento in range(1, 4):

            try:

                respuesta = contexto.request.get(
                    URL_SCRIPT,
                    timeout=120000,
                    headers={
                        "Accept": (
                            "text/javascript,"
                            "application/javascript,"
                            "*/*;q=0.8"
                        )*
                        "Referer"* URL_FUENTE,
                     *  "Cache-Control": "no-cache",
   *                    "Pragma": "no-*ache"
                    }
      *         )

                print(*                    f"Intento {int*nto}: "
                    "estad* de pronostico.js: "
             *      f"{respuesta.status}"
      *         )

                if res*uesta.ok:

                    con*enido = respuesta.text()

        *           if contenido.strip():
 *                      break

     *          ultimo_error = (
       *            "Respuesta HTTP "
    *               f"{respuesta.status*"
                )

            e*cept Exception as error:

        *       ultimo_error = str(error)

*               print(
            *       f"Error intento {intento}: *
                    f"{ultimo_err*r}"
                )

           *if intento < 3:

                p*int(
                    "Esperand* antes del "
                    "siguiente intento..."
                )

                time.sleep(10)

        navegador.close()

    if not contenido.strip():

        raise RuntimeError(
            "No fue posible descargar "
            "pronostico.js. "
            f"Último error: {ultimo_error}"
        )

    return contenido


# =================================================
# PROCESAR LOCALIDADES
# =================================================

def procesar_pronosticos(contenido):

    bloques = re.findall(
        r"Pronostico\.push\s*"
        r"\(\s*\{(.*?)\}"
        r"\s*\)\s*;",
        contenido,
        flags=re.DOTALL
    )

    print(
        "Localidades encontradas:",
        len(bloques)
    )

    pronosticos = []

    for numero_bloque, bloque in enumerate(
        bloques,
        start=1
    ):

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

            print(
                "OMITIDO bloque "
                f"{numero_bloque}: "
                "sin indice o ciudad"
            )

            continue

        dias = []

        cantidad = max(
            len(fechas),
            len(temperaturas)
        )

        for posicion in range(cantidad):

            if posicion < len(fechas):
                etiqueta_fecha = fechas[posicion]
            else:
                etiqueta_fecha = ""

            if posicion < len(temperaturas):
                temperatura_texto = temperaturas[posicion]
            else:
                temperatura_texto = ""

            valores = separar_temperatura(
                temperatura_texto
            )

            nivel_temperatura = (
                clasificar_temperatura(
                    valores["maxima"]
                )
            )

            dias.append({
                "posicion": posicion + 1,
                "fecha_etiqueta": etiqueta_fecha,
                "temperatura": temperatura_texto,
                "minima": valores["minima"],
                "maxima": valores["maxima"],
                "nivel_temperatura": nivel_temperatura
            })

        if dias:

            primer_dia = dias[0]

        else:

            primer_dia = {
                "temperatura": "",
                "minima": None,
                "maxima": None,
                "nivel_temperatura": "No disponible"
            }

        registro = {
            "indice": indice,
            "ciudad": ciudad,
            "region_codigo": region,
            "fecha_pronostico_iso": fecha_sql,
            "fecha_pronostico": convertir_fecha(
                fecha_sql
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

        pronosticos.append(registro)

        print(
            f"OK: {ciudad} | "
            f"{fecha_sql} | "
            f"{primer_dia['temperatura']} | "
            f"Min: {primer_dia['minima']} | "
            f"Max: {primer_dia['maxima']} | "
            f"{primer_dia['nivel_temperatura']}"
        )

    if not pronosticos:

        raise RuntimeError(
            "No fue posible extraer "
            "localidades desde "
            "pronostico.js."
        )

    pronosticos.sort(
        key=lambda item: (
            item["region_codigo"],
            item["ciudad"]
        )
    )

    return pronosticos


# =================================================
# GENERAR JSON
# =================================================

def generar_json(
    pronosticos,
    fecha_referencia
):

    salida_json = {
        "fuente": (
            "Dirección Meteorológica "
            "de Chile"
        ),
        "producto": (
            "Pronóstico de temperaturas "
            "por localidad"
        ),
        "fecha_referencia": fecha_referencia,
        "fecha_generacion_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "cantidad_localidades": len(pronosticos),
        "localidades": pronosticos
    }

    with open(
        RUTA_JSON,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            salida_json,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    print(
        "JSON generado correctamente:",
        RUTA_JSON
    )


# =================================================
# GENERAR XML RSS
# =================================================

def generar_xml(pronosticos):

    fecha_rss = datetime.now(
        timezone.utc
    ).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    items_rss = []

    for registro in pronosticos:

        if registro["temperatura_minima"] is None:
            minima = ""
        else:
            minima = str(
                registro["temperatura_minima"]
            )

        if registro["temperatura_maxima"] is None:
            maxima = ""
        else:
            maxima = str(
                registro["temperatura_maxima"]
            )

        identificador = (
            f"TEMP|"
            f"{registro['indice']}|"
            f"{registro['fecha_pronostico_iso']}"
        )

        titulo = (
            f"{registro['ciudad']} | "
            f"{registro['temperatura_primer_dia']} °C | "
            f"{registro['fecha_pronostico']}"
        )

        resumen = (
            f"IndiceLocalidad="
            f"{registro['indice']}"
            f"|Ciudad="
            f"{registro['ciudad']}"
            f"|CodigoRegion="
            f"{registro['region_codigo']}"
            f"|FechaPronostico="
            f"{registro['fecha_pronostico']}"
            f"|TemperaturaMinima="
            f"{minima}"
            f"|TemperaturaMaxima="
            f"{maxima}"
            f"|NivelTemperatura="
            f"{registro['nivel_temperatura']}"
            f"|Condicion="
            f"{registro['texto_resto_dia']}"
        )

        item_xml = f"""
<item>
<title><![CDATA[{titulo}]]></title>
<link>{escape(URL_FUENTE)}</link>
<guid isPermaLink="false"><![CDATA[{identificador}]]></guid>
<description><![CDATA[{resumen}]]></description>
<pubDate>{fecha_rss}</pubDate>
</item>
"""

        items_rss.append(item_xml)

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Pronóstico de Temperaturas por Localidad</title>
<link>{escape(URL_FUENTE)}</link>
<description>Pronóstico diario de temperaturas mínimas y máximas publicado por MeteoChile</description>
<language>es-cl</language>
<lastBuildDate>{fecha_rss}</lastBuildDate>

{''.join(items_rss)}

</channel>
</rss>
"""

    with open(
        RUTA_XML,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(rss)

    print(
        "XML generado correctamente:",
        RUTA_XML
    )


# =================================================
# EJECUCION PRINCIPAL
# =================================================

def main():

    print("")
    print("===================================")
    print("INICIANDO PRONOSTICO TEMPERATURAS")
    print("===================================")

    contenido = descargar_pronostico()

    pronosticos = procesar_pronosticos(
        contenido
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
            "%d-%m-%Y"
        )
    )

    generar_json(
        pronosticos,
        fecha_referencia
    )

    generar_xml(pronosticos)

    print("")
    print("===================================")
    print("PRONOSTICO TEMPERATURAS GENERADO")
    print("===================================")
    print(
        "Localidades procesadas:",
        len(pronosticos)
    )
    print(
        "Fecha de referencia:",
        fecha_referencia
    )
    print("JSON:", RUTA_JSON)
    print("RSS:", RUTA_XML)
    print("===================================")


if __name__ == "__main__":
    main()
