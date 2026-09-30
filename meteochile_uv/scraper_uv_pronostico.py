from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from html import escape
import json
import re
import time


# ---------------------------------
# CONFIGURACION
# ---------------------------------

URL_BASE = (
    "https://www.meteochile.gob.cl/"
    "PortalDMC-web/otros_pronosticos/"
    "radiacion_uv_region.xhtml?estacion="
)

REGIONES = [
    {
        "region": "Arica y Parinacota",
        "estacion": "Arica",
        "codigo": "180016"
    },
    {
        "region": "Tarapacá",
        "estacion": "Iquique",
        "codigo": "200006"
    },
    {
        "region": "Antofagasta",
        "estacion": "Antofagasta",
        "codigo": "230001"
    },
    {
        "region": "Atacama",
        "estacion": "Caldera",
        "codigo": "270008"
    },
    {
        "region": "Coquimbo",
        "estacion": "La Serena",
        "codigo": "290004"
    },
    {
        "region": "Valparaíso",
        "estacion": "Litoral Central",
        "codigo": "330120"
    },
    {
        "region": "Metropolitana",
        "estacion": "Santiago",
        "codigo": "330020"
    },
    {
        "region": "O'Higgins",
        "estacion": "Rancagua",
        "codigo": "340045"
    },
    {
        "region": "Maule",
        "estacion": "Talca",
        "codigo": "350050"
    },
    {
        "region": "Ñuble",
        "estacion": "Chillán",
        "codigo": "360011"
    },
    {
        "region": "Biobío",
        "estacion": "Concepción",
        "codigo": "360019"
    },
    {
        "region": "La Araucanía",
        "estacion": "Temuco",
        "codigo": "380029"
    },
    {
        "region": "Los Ríos",
        "estacion": "Valdivia",
        "codigo": "390026"
    },
    {
        "region": "Los Lagos",
        "estacion": "Puerto Montt",
        "codigo": "410005"
    },
    {
        "region": "Aysén",
        "estacion": "Coyhaique",
        "codigo": "450004"
    },
    {
        "region": "Magallanes",
        "estacion": "Punta Arenas",
        "codigo": "520006"
    }
]


def limpiar_texto(valor):

    if valor is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(valor)
    ).strip()


def normalizar_riesgo(riesgo):

    texto = limpiar_texto(riesgo).lower()

    if "extremo" in texto:
        return "Extremo"

    if "muy alto" in texto:
        return "Muy alto"

    if texto == "alto" or " alto" in texto:
        return "Alto"

    if "moderado" in texto:
        return "Moderado"

    if "bajo" in texto:
        return "Bajo"

    return "No disponible"


def valor_superior_indice(indice):

    if not indice:
        return None

    numeros = re.findall(
        r"\d+",
        indice
    )

    if not numeros:
        return None

    return max(
        int(numero)
        for numero in numeros
    )


def obtener_pronostico_desde_texto(texto):

    lineas = [
        limpiar_texto(linea)
        for linea in texto.splitlines()
        if limpiar_texto(linea)
    ]

    fecha_pronostico = ""
    indice_pronosticado = ""
    riesgo_pronosticado = ""

    posicion_pronostico = -1

    for indice, linea in enumerate(lineas):

        if (
            "índice pronosticado para el día"
            in linea.lower()
        ):

            posicion_pronostico = indice
            break

    if posicion_pronostico == -1:

        return {
            "fecha_pronostico": "",
            "indice_uv": "",
            "riesgo": "No disponible"
        }

    # Buscar fecha posterior al encabezado
    for linea in lineas[
        posicion_pronostico + 1:
        posicion_pronostico + 6
    ]:

        fecha_match = re.search(
            r"\d{2}-\d{2}-\d{4}",
            linea
        )

        if fecha_match:

            fecha_pronostico = (
                fecha_match.group(0)
            )

            break

    # Buscar encabezado Indice / Riesgo
    posicion_encabezado = -1

    for indice in range(
        posicion_pronostico + 1,
        min(
            len(lineas),
            posicion_pronostico + 12
        )
    ):

        linea_minuscula = (
            lineas[indice].lower()
        )

        if (
            "índice" in linea_minuscula
            and "riesgo" in linea_minuscula
        ):

            posicion_encabezado = indice
            break

    if posicion_encabezado >= 0:

        valores = lineas[
            posicion_encabezado + 1:
            posicion_encabezado + 6
        ]

        for valor in valores:

            if (
                not indice_pronosticado
                and re.fullmatch(
                    r"\d+\s*(?:-\s*\d+)?\+?",
                    valor
                )
            ):

                indice_pronosticado = (
                    valor.replace(" ", "")
                )

                continue

            riesgo_detectado = (
                normalizar_riesgo(valor)
            )

            if (
                indice_pronosticado
                and riesgo_detectado
                != "No disponible"
            ):

                riesgo_pronosticado = (
                    riesgo_detectado
                )

                break

    if not riesgo_pronosticado:

        riesgo_pronosticado = (
            "No disponible"
        )

    return {
        "fecha_pronostico": fecha_pronostico,
        "indice_uv": indice_pronosticado,
        "riesgo": riesgo_pronosticado
    }


pronosticos = []


# ---------------------------------
# NAVEGADOR
# ---------------------------------

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox"
        ]
    )

    context = browser.new_context(
        timezone_id="America/Santiago",
        locale="es-CL",
        viewport={
            "width": 1920,
            "height": 1080
        },
        user_agent=(
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0.0.0 "
            "Safari/537.36"
        )
    )

    page = context.new_page()

    for configuracion in REGIONES:

        region = configuracion["region"]
        estacion = configuracion["estacion"]
        codigo = configuracion["codigo"]

        url = URL_BASE + codigo

        texto_pagina = ""
        ultimo_error = ""

        print("")
        print("-----------------------------------")
        print(f"Región: {region}")
        print(f"Estación: {estacion}")
        print(f"Código: {codigo}")
        print("-----------------------------------")

        for intento in range(1, 4):

            try:

                print(
                    f"Intento {intento} de 3"
                )

                respuesta = page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=120000
                )

                page.wait_for_timeout(7000)

                if respuesta is not None:

                    print(
                        "Estado HTTP:",
                        respuesta.status
                    )

                texto_pagina = (
                    page.locator("body")
                    .inner_text(
                        timeout=30000
                    )
                )

                if texto_pagina.strip():

                    break

                ultimo_error = (
                    "Página sin contenido visible."
                )

            except Exception as error:

                ultimo_error = str(error)

                print(
                    "Error:",
                    ultimo_error
                )

                if intento < 3:

                    print(
                        "Esperando antes del "
                        "siguiente intento..."
                    )

                    time.sleep(10)

        if not texto_pagina.strip():

            pronostico = {
                "region": region,
                "estacion": estacion,
                "codigo_estacion": codigo,
                "fecha_pronostico": "",
                "indice_uv": "",
                "valor_maximo": None,
                "riesgo": "No disponible",
                "url": url,
                "error": ultimo_error
            }

            pronosticos.append(
                pronostico
            )

            print(
                "Pronóstico no disponible."
            )

            continue

        resultado = (
            obtener_pronostico_desde_texto(
                texto_pagina
            )
        )

        valor_maximo = (
            valor_superior_indice(
                resultado["indice_uv"]
            )
        )

        pronostico = {
            "region": region,
            "estacion": estacion,
            "codigo_estacion": codigo,
            "fecha_pronostico": (
                resultado[
                    "fecha_pronostico"
                ]
            ),
            "indice_uv": (
                resultado["indice_uv"]
            ),
            "valor_maximo": valor_maximo,
            "riesgo": resultado["riesgo"],
            "url": url,
            "error": ""
        }

        pronosticos.append(
            pronostico
        )

        print(
            "Pronóstico:",
            resultado["indice_uv"],
            resultado["riesgo"]
        )

    browser.close()


# ---------------------------------
# FECHA GENERAL DEL PRONOSTICO
# ---------------------------------

fechas_disponibles = [
    item["fecha_pronostico"]
    for item in pronosticos
    if item["fecha_pronostico"]
]

if fechas_disponibles:

    fecha_general = (
        max(
            fechas_disponibles,
            key=fechas_disponibles.count
        )
    )

else:

    fecha_general = datetime.now(
        timezone.utc
    ).strftime(
        "%d-%m-%Y"
    )


# ---------------------------------
# CLASIFICAR POR NIVEL
# ---------------------------------

grupos = {
    "Extremo": [],
    "Muy alto": [],
    "Alto": [],
    "Moderado": [],
    "Bajo": [],
    "No disponible": []
}

for item in pronosticos:

    riesgo = item["riesgo"]

    if riesgo not in grupos:

        riesgo = "No disponible"

    grupos[riesgo].append(
        item
    )


# ---------------------------------
# MAXIMO NACIONAL
# ---------------------------------

pronosticos_con_valor = [
    item
    for item in pronosticos
    if item["valor_maximo"]
    is not None
]

if pronosticos_con_valor:

    maximo_nacional = max(
        item["valor_maximo"]
        for item
        in pronosticos_con_valor
    )

else:

    maximo_nacional = None


# ---------------------------------
# JSON
# ---------------------------------

salida_json = {
    "fuente": (
        "Dirección
