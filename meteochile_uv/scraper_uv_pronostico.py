from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from html import escape
import json
import re
import time


# =================================================
# CONFIGURACION
# =================================================

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


# =================================================
# FUNCIONES
# =================================================

def limpiar_texto(valor):

    if valor is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(valor)
    ).strip()


def normalizar_riesgo(riesgo):

    texto = limpiar_texto(
        riesgo
    ).lower()

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

    # ---------------------------------
    # BUSCAR INICIO DEL PRONOSTICO
    # -------
