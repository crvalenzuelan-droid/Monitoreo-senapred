from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from html import escape
import json
import re
import time


URL_BASE = (
    "https://www.meteochile.gob.cl/"
    "PortalDMC-web/otros_pronosticos/"
    "radiacion_uv_region.xhtml?estacion="
)

REGIONES = [
    ("Arica y Parinacota", "Arica", "180016"),
    ("Tarapacá", "Iquique", "200006"),
    ("Antofagasta", "Antofagasta", "230001"),
    ("Atacama", "Caldera", "270008"),
    ("Coquimbo", "La Serena", "290004"),
    ("Valparaíso", "Litoral Central", "330120"),
    ("Metropolitana", "Santiago", "330020"),
    ("O'Higgins", "Rancagua", "340045"),
    ("Maule", "Talca", "350050"),
    ("Ñuble", "Chillán", "360011"),
    ("Biobío", "Concepción", "360019"),
    ("La Araucanía", "Temuco", "380029"),
    ("Los Ríos", "Valdivia", "390026"),
    ("Los Lagos", "Puerto Montt", "410005"),
    ("Aysén", "Coyhaique", "450004"),
    ("Magallanes", "Punta Arenas", "520006"),
]


def limpiar_texto(valor):
    if valor is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(valor)
    ).strip()


def normalizar_riesgo(texto):
    valor = limpiar_texto(texto).lower()

    if "extremo" in valor:
        return "Extremo"

    if "muy alto" in valor:
        return "Muy alto"

    if valor == "alto":
        return "Alto"

    if "moderado" in valor:
        return "Moderado"

    if valor == "bajo":
        return "Bajo"

    return "No disponible"


def obtener_valor_maximo(indice_uv):
    numeros = re.findall(
        r"\d+",
        indice_uv or ""
    )

    if not numeros:
        return None

    return max(
        int(numero)
        for numero in numeros
    )


def extraer_pronostico(texto_pagina):
    lineas = [
        limpiar_texto(linea)
        for linea in texto_pagina.splitlines()
        if limpiar_texto(linea)
    ]

    posicion = -1

    for indice, linea in enumerate(lineas):
        if (
            "índice pronosticado para el día"
            in linea.lower()
        ):
            posicion = indice
            break

    if posicion == -1:
        return {
            "fecha": "",
            "indice": "",
            "riesgo": "No disponible",
        }

    bloque = lineas[
        posicion:
        min(len(lineas), posicion + 15)
    ]

    fecha = ""
    indice_uv = ""
    riesgo = "No disponible"

    for linea in bloque:
        coincidencia_fecha = re.search(
            r"\d{2}-\d{2}-\d{4}",
            linea
        )

        if coincidencia_fecha:
            fecha = coincidencia_fecha.group(0)
            break

    for linea in bloque:
        if re.fullmatch(
            r"\d+\s*(?:-\s*\d+)?\+?",
            linea
        ):
            indice_uv = linea.replace(" ", "")
            break

    if indice_uv:
        posicion_indice = bloque.index(
            next(
                linea
                for linea in bloque
                if re.fullmatch(
                    r"\d+\s*(?:-\s*\d+)?\+?",
                    linea
                )
            )
        )

        for linea in bloque[
            posicion_indice + 1:
        ]:
            nivel = normalizar_riesgo(linea)

            if nivel != "No disponible":
                riesgo = nivel
                break

    return {
        "fecha": fecha,
        "indice": indice_uv,
        "riesgo": riesgo,
    }


pronosticos = []

print("")
print("INICIANDO PRONOSTICO UV NACIONAL")
print("===================================")


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
    )

    context = browser.new_context(
        timezone_id="America/Santiago",
        locale="es-CL",
        viewport={
            "width": 1920,
            "height": 1080,
        },
        user_agent=(
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
    )

    for region, estacion, codigo in REGIONES:
        url = URL_BASE + codigo
        texto_pagina = ""
        error_final = ""

        print("")
        print("-----------------------------------")
        print(f"Región: {region}")
        print(f"Estación: {estacion}")
        print(f"Código: {codigo}")

        pagina = context.new_page()

        for intento in range(1, 4):
            try:
                print(f"Intento {intento} de 3")

                respuesta = pagina.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=120000,
                )

                pagina.wait_for_timeout(6000)

                if respuesta is not None:
                    print(
                        "Estado HTTP:",
                        respuesta.status
                    )

                texto_pagina = (
                    pagina.locator("body")
                    .inner_text(timeout=30000)
                )

                if texto_pagina.strip():
                    break

                error_final = (
                    "Página sin contenido visible"
                )

            except Exception as error:
                error_final = str(error)
                print("Error:", error_final)

                if intento < 3:
                    time.sleep(10)

        if texto_pagina.strip():
            resultado = extraer_pronostico(
                texto_pagina
            )
        else:
            resultado = {
                "fecha": "",
                "indice": "",
                "riesgo": "No disponible",
            }

        valor_maximo = obtener_valor_maximo(
            resultado["indice"]
        )

        registro = {
            "region": region,
            "estacion": estacion,
            "codigo_estacion": codigo,
            "fecha_pronostico": resultado["fecha"],
            "indice_uv": resultado["indice"],
            "valor_maximo": valor_maximo,
            "riesgo": resultado["riesgo"],
            "url": url,
            "error": error_final,
        }

        pronosticos.append(registro)

        print(
            "Resultado:",
            registro["fecha_pronostico"],
            registro["indice_uv"],
            registro["riesgo"],
        )

        pagina.close()

    browser.close()


if len(pronosticos) != len(REGIONES):
    raise RuntimeError(
        "No se procesaron todas las regiones"
    )


fechas = [
    registro["fecha_pronostico"]
    for registro in pronosticos
    if registro["fecha_pronostico"]
]

if fechas:
    fecha_general = max(
        set(fechas),
        key=fechas.count
    )
else:
    fecha_general = datetime.now(
        timezone.utc
    ).strftime("%d-%m-%Y")


grupos = {
    "Extremo": [],
    "Muy alto": [],
    "Alto": [],
    "Moderado": [],
    "Bajo": [],
    "No disponible": [],
}

for registro in pronosticos:
    nivel = registro["riesgo"]

    if nivel not in grupos:
        nivel = "No disponible"

    grupos[nivel].append(registro)


valores_disponibles = [
    registro["valor_maximo"]
    for registro in pronosticos
    if registro["valor_maximo"] is not None
]

maximo_nacional = (
    max(valores_disponibles)
    if valores_disponibles
    else None
)


salida_json = {
    "fuente": (
        "Dirección Meteorológica de Chile"
    ),
    "producto": (
        "Pronóstico nacional de radiación UV"
    ),
    "fecha_pronostico": fecha_general,
    "fecha_generacion_utc": (
        datetime.now(
            timezone.utc
        ).isoformat()
    ),
    "valor_maximo_nacional": (
        maximo_nacional
    ),
    "regiones": pronosticos,
}

with open(
    "meteochile_uv/pronostico_uv.json",
    "w",
    encoding="utf-8",
) as archivo:
    json.dump(
        salida_json,
        archivo,
        ensure_ascii=False,
        indent=2,
    )


def crear_lista_regiones(nivel):

    resultados = []

    registros_nivel = grupos.get(
        nivel,
        []
    )

    for registro in registros_nivel:

        if registro["indice_uv"]:

            resultados.append(
                f"{registro['region']} "
                f"({registro['indice_uv']})"
            )

        else:

            resultados.append(
                registro["region"]
            )

    return ", ".join(
        resultados
    )


resumen_extremo = crear_lista_regiones(
    "Extremo"
)

resumen_muy_alto = crear_lista_regiones(
    "Muy alto"
)

resumen_alto = crear_lista_regiones(
    "Alto"
)

resumen_moderado = crear_lista_regiones(
    "Moderado"
)

resumen_bajo = crear_lista_regiones(
    "Bajo"
)

resumen_no_disponible = crear_lista_regiones(
    "No disponible"
)


fecha_rss = datetime.now(
    timezone.utc
).strftime(
    "%a, %d %b %Y %H:%M:%S GMT"
)

id_pronostico = (
    f"UV-NACIONAL|{fecha_general}"
)

titulo_rss = (
    "Pronóstico Nacional de Radiación UV | "
    f"{fecha_general}"
)

maximo_texto = (
    ""
    if maximo_nacional is None
    else str(maximo_nacional)
)

summary = (
    f"FechaPronostico={fecha_general}"
    f"|MaximoNacional={maximo_texto}"
    f"|Extremo={resumen_extremo}"
    f"|MuyAlto={resumen_muy_alto}"
    f"|Alto={resumen_alto}"
    f"|Moderado={resumen_moderado}"
    f"|Bajo={resumen_bajo}"
    f"|NoDisponible={resumen_no_disponible}"
)

url_fuente = (
    "https://www.meteochile.gob.cl/"
    "PortalDMC-web/otros_pronosticos/"
    "radiacion_uv.xhtml"
)

rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Pronóstico Nacional Radiación UV</title>
<link>{escape(url_fuente)}</link>
<description>Pronóstico nacional diario de radiación UV</description>
<language>es-cl</language>
<lastBuildDate>{fecha_rss}</lastBuildDate>

<item>
<title><![CDATA[{titulo_rss}]]></title>
<link>{escape(url_fuente)}</link>
<guid isPermaLink="false"><![CDATA[{id_pronostico}]]></guid>
<description><![CDATA[{summary}]]></description>
<pubDate>{fecha_rss}</pubDate>
</item>

</channel>
</rss>
"""

with open(
    "meteochile_uv/pronostico_uv.xml",
    "w",
    encoding="utf-8",
) as archivo:
    archivo.write(rss)


print("")
print("===================================")
print("PRONOSTICO UV NACIONAL GENERADO")
print("===================================")
print(f"Fecha: {fecha_general}")
print(f"Regiones: {len(pronosticos)}")
print(f"Extremo: {len(grupos['Extremo'])}")
print(f"Muy alto: {len(grupos['Muy alto'])}")
print(f"Alto: {len(grupos['Alto'])}")
print(
    f"Moderado: {len(grupos['Moderado'])}"
)
print(f"Bajo: {len(grupos['Bajo'])}")
print(
    "No disponible:",
    len(grupos["No disponible"])
)
print(
    "JSON: meteochile_uv/"
    "pronostico_uv.json"
)
print(
    "RSS: meteochile_uv/"
    "pronostico_uv.xml"
)
print("===================================")
