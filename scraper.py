from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from html import escape
from urllib.parse import urlsplit, urlunsplit
import json
import re
import unicodedata


# ============================================================
# FUNCIONES DE NORMALIZACION
# ============================================================

def normalizar_texto(texto):
    """
    Convierte texto a minúsculas, elimina tildes y normaliza
    espacios y apóstrofes para facilitar las comparaciones.
    """
    if texto is None:
        return ""

    texto = str(texto).strip().lower()

    texto = texto.replace("´", "'")
    texto = texto.replace("’", "'")
    texto = texto.replace("`", "'")

    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def limpiar_url(url):
    """
    Devuelve una URL válida para SharePoint y RSS.
    Si el valor no comienza con http o https, devuelve vacío.
    """
    if not url:
        return ""

    url = str(url).strip()

    url = url.replace("\r", "")
    url = url.replace("\n", "")
    url = url.replace("&amp;", "&")

    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        return ""

    try:
        partes = urlsplit(url)

        if not partes.netloc:
            return ""

        return urlunsplit(
            (
                partes.scheme,
                partes.netloc,
                partes.path,
                partes.query,
                partes.fragment
            )
        )

    except Exception:
        return ""


def proteger_cdata(texto):
    """
    Evita que el contenido rompa una sección CDATA del RSS.
    """
    if texto is None:
        return ""

    return str(texto).replace("]]>", "]]]]><![CDATA[>")


# ============================================================
# CATALOGOS TERRITORIALES
# ============================================================

REGIONES_ALIAS = {
    "arica y parinacota": "Arica y Parinacota",
    "tarapaca": "Tarapacá",
    "antofagasta": "Antofagasta",
    "atacama": "Atacama",
    "coquimbo": "Coquimbo",
    "valparaiso": "Valparaíso",
    "metropolitana": "Metropolitana",
    "metropolitana de santiago": "Metropolitana",
    "region metropolitana": "Metropolitana",
    "region metropolitana de santiago": "Metropolitana",
    "libertador general bernardo o'higgins": "O´Higgins",
    "libertador general bernardo ohiggins": "O´Higgins",
    "o'higgins": "O´Higgins",
    "ohiggins": "O´Higgins",
    "maule": "Maule",
    "nuble": "Ñuble",
    "biobio": "Biobío",
    "la araucania": "La Araucanía",
    "araucania": "La Araucanía",
    "los rios": "Los Ríos",
    "los lagos": "Los Lagos",
    "aysen": "Aysén",
    "aysen del general carlos ibanez del campo": "Aysén",
    "magallanes": "Magallanes",
    "magallanes y de la antartica chilena": "Magallanes"
}


PROVINCIA_REGION = {
    "arica": "Arica y Parinacota",
    "parinacota": "Arica y Parinacota",
    "iquique": "Tarapacá",
    "tamarugal": "Tarapacá",
    "antofagasta": "Antofagasta",
    "el loa": "Antofagasta",
    "tocopilla": "Antofagasta",
    "copiapo": "Atacama",
    "chanaral": "Atacama",
    "huasco": "Atacama",
    "elqui": "Coquimbo",
    "limari": "Coquimbo",
    "choapa": "Coquimbo",
    "valparaiso": "Valparaíso",
    "isla de pascua": "Valparaíso",
    "los andes": "Valparaíso",
    "petorca": "Valparaíso",
    "quillota": "Valparaíso",
    "san antonio": "Valparaíso",
    "san felipe de aconcagua": "Valparaíso",
    "marga marga": "Valparaíso",
    "santiago": "Metropolitana",
    "cordillera": "Metropolitana",
    "chacabuco": "Metropolitana",
    "maipo": "Metropolitana",
    "melipilla": "Metropolitana",
    "talagante": "Metropolitana",
    "cachapoal": "O´Higgins",
    "cardenal caro": "O´Higgins",
    "colchagua": "O´Higgins",
    "curico": "Maule",
    "talca": "Maule",
    "linares": "Maule",
    "cauquenes": "Maule",
    "diguillin": "Ñuble",
    "itata": "Ñuble",
    "punilla": "Ñuble",
    "concepcion": "Biobío",
    "arauco": "Biobío",
    "biobio": "Biobío",
    "malleco": "La Araucanía",
    "cautin": "La Araucanía",
    "valdivia": "Los Ríos",
    "ranco": "Los Ríos",
    "llanquihue": "Los Lagos",
    "chiloe": "Los Lagos",
    "osorno": "Los Lagos",
    "palena": "Los Lagos",
    "coyhaique": "Aysén",
    "aysen": "Aysén",
    "general carrera": "Aysén",
    "capitan prat": "Aysén",
    "magallanes": "Magallanes",
    "ultima esperanza": "Magallanes",
    "tierra del fuego": "Magallanes",
    "antartica chilena": "Magallanes"
}


COMUNA_REGION = {
    # Arica y Parinacota
    "arica": "Arica y Parinacota",
    "camarones": "Arica y Parinacota",
    "putre": "Arica y Parinacota",
    "general lagos": "Arica y Parinacota",

    # Tarapacá
    "iquique": "Tarapacá",
    "alto hospicio": "Tarapacá",
    "pozo almonte": "Tarapacá",
    "camina": "Tarapacá",
    "colchane": "Tarapacá",
    "huara": "Tarapacá",
    "pica": "Tarapacá",

    # Antofagasta
    "antofagasta": "Antofagasta",
    "calama": "Antofagasta",
    "taltal": "Antofagasta",
    "mejillones": "Antofagasta",
    "sierra gorda": "Antofagasta",
    "tocopilla": "Antofagasta",
    "maria elena": "Antofagasta",
    "ollague": "Antofagasta",
    "san pedro de atacama": "Antofagasta",

    # Atacama
    "copiapo": "Atacama",
    "caldera": "Atacama",
    "tierra amarilla": "Atacama",
    "chanaral": "Atacama",
    "diego de almagro": "Atacama",
    "vallenar": "Atacama",
    "alto del carmen": "Atacama",
    "freirina": "Atacama",
    "huasco": "Atacama",

    # Coquimbo
    "la serena": "Coquimbo",
    "coquimbo": "Coquimbo",
    "andacollo": "Coquimbo",
    "la higuera": "Coquimbo",
    "paiguano": "Coquimbo",
    "vicuna": "Coquimbo",
    "ovalle": "Coquimbo",
    "combarbala": "Coquimbo",
    "monte patria": "Coquimbo",
    "punitaqui": "Coquimbo",
    "rio hurtado": "Coquimbo",
    "illapel": "Coquimbo",
    "canela": "Coquimbo",
    "los vilos": "Coquimbo",
    "salamanca": "Coquimbo",

    # Valparaíso
    "valparaiso": "Valparaíso",
    "vina del mar": "Valparaíso",
    "concon": "Valparaíso",
    "quilpue": "Valparaíso",
    "villa alemana": "Valparaíso",
    "limache": "Valparaíso",
    "olmue": "Valparaíso",
    "la calera": "Valparaíso",
    "quillota": "Valparaíso",
    "la cruz": "Valparaíso",
    "nogales": "Valparaíso",
    "hijuelas": "Valparaíso",
    "san felipe": "Valparaíso",
    "los andes": "Valparaíso",
    "san antonio": "Valparaíso",
    "cartagena": "Valparaíso",
    "el quisco": "Valparaíso",
    "el tabo": "Valparaíso",
    "algarrobo": "Valparaíso",
    "santo domingo": "Valparaíso",

    # Metropolitana
    "santiago": "Metropolitana",
    "san jose de maipo": "Metropolitana",
    "puente alto": "Metropolitana",
    "pirque": "Metropolitana",
    "la florida": "Metropolitana",
    "penalolen": "Metropolitana",
    "la reina": "Metropolitana",
    "las condes": "Metropolitana",
    "lo barnechea": "Metropolitana",
    "vitacura": "Metropolitana",
    "colina": "Metropolitana",
    "providencia": "Metropolitana",
    "nunoa": "Metropolitana",
    "macul": "Metropolitana",
    "san joaquin": "Metropolitana",
    "la granja": "Metropolitana",
    "san ramon": "Metropolitana",
    "la cisterna": "Metropolitana",
    "el bosque": "Metropolitana",
    "lo espejo": "Metropolitana",
    "pedro aguirre cerda": "Metropolitana",
    "cerrillos": "Metropolitana",
    "estacion central": "Metropolitana",
    "maipu": "Metropolitana",
    "pudahuel": "Metropolitana",
    "quilicura": "Metropolitana",
    "huechuraba": "Metropolitana",
    "conchali": "Metropolitana",
    "recoleta": "Metropolitana",
    "independencia": "Metropolitana",
    "renca": "Metropolitana",
    "quinta normal": "Metropolitana",
    "lo prado": "Metropolitana",
    "cerro navia": "Metropolitana",
    "san miguel": "Metropolitana",
    "la pintana": "Metropolitana",
    "san bernardo": "Metropolitana",
    "melipilla": "Metropolitana",
    "penaflor": "Metropolitana",
    "talagante": "Metropolitana",
    "buin": "Metropolitana",
    "paine": "Metropolitana",
    "lampa": "Metropolitana",
    "tiltil": "Metropolitana",

    # O'Higgins
    "rancagua": "O´Higgins",
    "san fernando": "O´Higgins",
    "machali": "O´Higgins",
    "rengo": "O´Higgins",
    "pichilemu": "O´Higgins",

    # Maule
    "talca": "Maule",
    "curico": "Maule",
    "linares": "Maule",
    "cauquenes": "Maule",

    # Ñuble
    "chillan": "Ñuble",
    "chillan viejo": "Ñuble",
    "pinto": "Ñuble",
    "coihueco": "Ñuble",

    # Biobío
    "concepcion": "Biobío",
    "talcahuano": "Biobío",
    "hualpen": "Biobío",
    "chiguayante": "Biobío",
    "san pedro de la paz": "Biobío",
    "coronel": "Biobío",
    "lota": "Biobío",
    "los angeles": "Biobío",

    # La Araucanía
    "temuco": "La Araucanía",
    "padre las casas": "La Araucanía",
    "angol": "La Araucanía",
    "pucon": "La Araucanía",
    "villarrica": "La Araucanía",

    # Los Ríos
    "valdivia": "Los Ríos",
    "la union": "Los Ríos",
    "rio bueno": "Los Ríos",
    "panguipulli": "Los Ríos",

    # Los Lagos
    "puerto montt": "Los Lagos",
    "puerto varas": "Los Lagos",
    "castro": "Los Lagos",
    "ancud": "Los Lagos",
    "osorno": "Los Lagos",

    # Aysén
    "coyhaique": "Aysén",
    "aysen": "Aysén",

    # Magallanes
    "punta arenas": "Magallanes",
    "puerto natales": "Magallanes"
}


# ============================================================
# FUNCIONES TERRITORIALES
# ============================================================

def normalizar_region(region):
    region_normalizada = normalizar_texto(region)

    if not region_normalizada:
        return "No identificada"

    region_normalizada = re.sub(
        r"^(region|región)\s+(de\s+|del\s+|de la\s+|de los\s+|de las\s+)?",
        "",
        region_normalizada,
        flags=re.IGNORECASE
    ).strip()

    return REGIONES_ALIAS.get(
        region_normalizada,
        region.strip()
    )


def buscar_region_explicita(titulo):
    """
    Busca expresiones como:
    para la Región Metropolitana por...
    para la región de Los Lagos por...
    """
    patrones = [
        (
            r"para\s+la\s+regi[oó]n"
            r"(?:\s+de\s+los|\s+de\s+las|\s+del|\s+de\s+la|\s+de)?"
            r"\s+(.+?)(?:\s+por\s+|,|$)"
        ),
        (
            r"para\s+regi[oó]n"
            r"\s+(.+?)(?:\s+por\s+|,|$)"
        )
    ]

    for patron in patrones:
        coincidencia = re.search(
            patron,
            titulo,
            flags=re.IGNORECASE
        )

        if coincidencia:
            return normalizar_region(
                coincidencia.group(1).strip()
            )

    return ""


def buscar_region_por_provincia(titulo):
    titulo_normalizado = normalizar_texto(titulo)

    provincias_ordenadas = sorted(
        PROVINCIA_REGION.keys(),
        key=len,
        reverse=True
    )

    for provincia in provincias_ordenadas:
        patron = r"\b" + re.escape(provincia) + r"\b"

        if re.search(patron, titulo_normalizado):
            return PROVINCIA_REGION[provincia]

    return ""


def buscar_comunas_en_texto(titulo):
    titulo_normalizado = normalizar_texto(titulo)

    comunas_encontradas = []

    comunas_ordenadas = sorted(
        COMUNA_REGION.keys(),
        key=len,
        reverse=True
    )

    for comuna in comunas_ordenadas:
        patron = r"\b" + re.escape(comuna) + r"\b"

        if re.search(patron, titulo_normalizado):
            comunas_encontradas.append(comuna)

    # Evitar duplicados conservando el orden
    resultado = []

    for comuna in comunas_encontradas:
        if comuna not in resultado:
            resultado.append(comuna)

    return resultado


def obtener_region_y_cobertura(titulo):
    """
    Devuelve:
    region
    nivel_cobertura
    ubicacion_cobertura
    """
    region_explicita = buscar_region_explicita(titulo)

    comunas = buscar_comunas_en_texto(titulo)

    if region_explicita:
        if comunas:
            return (
                region_explicita,
                "Comuna",
                "|".join(comunas)
            )

        return (
            region_explicita,
            "Región",
            region_explicita
        )

    if comunas:
        regiones = []

        for comuna in comunas:
            region_comuna = COMUNA_REGION.get(comuna)

            if region_comuna and region_comuna not in regiones:
                regiones.append(region_comuna)

        if len(regiones) == 1:
            return (
                regiones[0],
                "Comuna",
                "|".join(comunas)
            )

        if len(regiones) > 1:
            return (
                "Cobertura múltiple",
                "Comuna",
                "|".join(comunas)
            )

    region_provincia = buscar_region_por_provincia(titulo)

    if region_provincia:
        return (
            region_provincia,
            "Provincia",
            region_provincia
        )

    return (
        "No identificada",
        "No identificada",
        ""
    )


# ============================================================
# EXTRACCION DE ALERTAS
# ============================================================

alertas = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        timezone_id="America/Santiago"
    )

    page = context.new_page()

    page.goto(
        "https://www.senapred.cl/alertas",
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(10000)

    texto_portada = page.locator("body").inner_text()

    with open(
        "portada_senapred.txt",
        "w",
        encoding="utf-8"
    ) as archivo:
        archivo.write(texto_portada)

    enlaces = page.locator("a").evaluate_all(
        """
        links => links.map(link => ({
            texto: link.innerText,
            href: link.href
        }))
        """
    )

    urls = []

    for enlace in enlaces:

        href = limpiar_url(
            enlace.get("href", "")
        )

        if "/alerta/" in href and href not in urls:
            urls.append(href)

    # Procesar solamente las 5 alertas más recientes
    urls = urls[:5]

    print(f"Alertas encontradas: {len(urls)}")

    for url in urls:

        detalle_page = None

        try:

            detalle_page = context.new_page()

            detalle_page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            detalle_page.wait_for_timeout(5000)

            texto = detalle_page.locator("body").inner_text()

            lineas = [
                linea.strip()
                for linea in texto.split("\n")
                if linea.strip()
            ]

            titulo = ""
            fecha = ""
            accion = ""
            tipo = ""
            prioridad = "Baja"

            # ------------------------------------------------
            # TITULO Y ACCION
            # ------------------------------------------------

            for linea in lineas:

                linea_normalizada = normalizar_texto(linea)

                if (
                    linea_normalizada.startswith("monitoreo")
                    or linea_normalizada.startswith("se declara")
                    or linea_normalizada.startswith("se modifica")
                    or linea_normalizada.startswith("se cancela")
                    or linea_normalizada.startswith("se actualiza")
                ):

                    titulo = linea.strip()

                    if linea_normalizada.startswith("monitoreo"):
                        accion = "Monitoreo"

                    elif linea_normalizada.startswith("se declara"):
                        accion = "Se declara"

                    elif linea_normalizada.startswith("se modifica"):
                        accion = "Se modifica"

                    elif linea_normalizada.startswith("se cancela"):
                        accion = "Se cancela"

                    elif linea_normalizada.startswith("se actualiza"):
                        accion = "Se actualiza"

                    break

            if not titulo:
                print("ALERTA OMITIDA: no se encontró título")
                print(url)
                continue

            # ------------------------------------------------
            # FECHA
            # ------------------------------------------------

            fecha_match = re.search(
                r"\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}",
                texto
            )

            if fecha_match:
                fecha = fecha_match.group(0).strip()

            if not fecha:
                print("ALERTA OMITIDA: no se encontró fecha")
                print(titulo)
                continue

            # ------------------------------------------------
            # TIPO Y PRIORIDAD
            # ------------------------------------------------

            titulo_normalizado = normalizar_texto(titulo)

            if "alerta roja" in titulo_normalizado:
                tipo = "Roja"
                prioridad = "Alta"

            elif "alerta amarilla" in titulo_normalizado:
                tipo = "Amarilla"
                prioridad = "Media"

            elif "temprana preventiva" in titulo_normalizado:
                tipo = "ATP"
                prioridad = "Baja"

            else:
                tipo = "No definido"
                prioridad = "Baja"

            # ------------------------------------------------
            # REGION Y COBERTURA
            # ------------------------------------------------

            (
                region,
                nivel_cobertura,
                ubicacion_cobertura
            ) = obtener_region_y_cobertura(titulo)

            # ------------------------------------------------
            # DETALLE LIMPIO
            # ------------------------------------------------

            detalle = texto

            inicios_detalle = [
                "De acuerdo con la información",
                "En consideración a estos antecedentes"
            ]

            for texto_inicio in inicios_detalle:

                posicion_inicio = detalle.find(texto_inicio)

                if posicion_inicio >= 0:
                    detalle = detalle[posicion_inicio:]
                    break

            textos_pie = [
                "Volver",
                "Ayuda",
                "Biblio GRD",
                "Planos de evacuación",
                "Visor Chile Preparado",
                "Contacto"
            ]

            for texto_pie in textos_pie:

                posicion_pie = detalle.find(texto_pie)

                if posicion_pie > 0:
                    detalle = detalle[:posicion_pie]
                    break

            detalle = detalle.strip()

            # ------------------------------------------------
            # IDENTIFICADOR ESTABLE
            # ------------------------------------------------

            id_alerta = f"{titulo}|{fecha}"

            alerta = {
                "id_alerta": id_alerta,
                "accion": accion,
                "tipo": tipo,
                "prioridad": prioridad,
                "region": region,
                "nivel_cobertura": nivel_cobertura,
                "ubicacion_cobertura": ubicacion_cobertura,
                "fecha_senapred": fecha,
                "titulo": titulo,
                "url": limpiar_url(url),
                "detalle": detalle
            }

            alertas.append(alerta)

            print(
                "OK:",
                titulo,
                "| Región:",
                region,
                "| Cobertura:",
                nivel_cobertura,
                "| Ubicación:",
                ubicacion_cobertura
            )

        except Exception as error:

            print("ERROR PROCESANDO ALERTA")
            print(url)
            print(str(error))

        finally:

            if detalle_page:
                detalle_page.close()

    browser.close()


# ============================================================
# GENERAR JSON
# ============================================================

with open(
    "alertas.json",
    "w",
    encoding="utf-8"
) as archivo:

    json.dump(
        alertas,
        archivo,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# GENERAR RSS
# ============================================================

fecha_rss = datetime.now(
    timezone.utc
).strftime(
    "%a, %d %b %Y %H:%M:%S GMT"
)

items = ""

for alerta in alertas:

    # Se conserva la estructura original para no romper
    # las expresiones actuales de Power Automate.
    summary = (
        f"Accion={alerta['accion']}"
        f"|Tipo={alerta['tipo']}"
        f"|Region={alerta['region']}"
        f"|Prioridad={alerta['prioridad']}"
        f"|Fecha={alerta['fecha_senapred']}"
    )

    titulo_cdata = proteger_cdata(
        alerta["titulo"]
    )

    id_cdata = proteger_cdata(
        alerta["id_alerta"]
    )

    summary_cdata = proteger_cdata(
        summary
    )

    url_xml = escape(
        alerta["url"],
        quote=True
    )

    items += f"""
<item>
<title><![CDATA[{titulo_cdata}]]></title>
<link>{url_xml}</link>
<guid isPermaLink="false"><![CDATA[{id_cdata}]]></guid>
<description><![CDATA[{summary_cdata}]]></description>
<pubDate>{fecha_rss}</pubDate>
</item>
"""


rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Alertas SENAPRED</title>
<link>https://www.senapred.cl</link>
<description>Alertas SENAPRED</description>
{items}
</channel>
</rss>
"""


with open(
    "rss.xml",
    "w",
    encoding="utf-8"
) as archivo:

    archivo.write(rss)


print(f"RSS generado con {len(alertas)} alertas")
