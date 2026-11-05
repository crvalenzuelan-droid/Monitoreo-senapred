from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from html import escape
from urllib.parse import urlsplit, urlunsplit
import json
import re
import unicodedata


# ============================================================
# CONFIGURACION GENERAL
# ============================================================

URL_ALERTAS_SENAPRED = "https://www.senapred.cl/alertas"

MAXIMO_ENLACES_CANDIDATOS = 25
MAXIMO_ALERTAS_SALIDA = 5

INICIOS_TITULO_VALIDOS = (
    "monitoreo",
    "se declara",
    "se modifica",
    "se cancela",
    "se actualiza",
)


# ============================================================
# NORMALIZACION GENERAL
# ============================================================

def normalizar_texto(texto):
    """
    Convierte un texto a minusculas, elimina tildes,
    normaliza apostrofes y elimina espacios repetidos.
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

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def limpiar_url(url):
    """
    Limpia y valida una URL antes de guardarla.
    """
    if not url:
        return ""

    url = str(url).strip()

    url = url.replace("\r", "")
    url = url.replace("\n", "")
    url = url.replace("&amp;", "&")

    if not re.match(
        r"^https?://",
        url,
        flags=re.IGNORECASE
    ):
        return ""

    try:
        partes = urlsplit(url)

        if not partes.scheme or not partes.netloc:
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
    Evita que una secuencia de cierre CDATA rompa el RSS.
    """
    if texto is None:
        return ""

    return str(texto).replace(
        "]]>",
        "]]]]><![CDATA[>"
    )


def titulo_es_alerta(titulo):
    """
    Confirma que el texto parece corresponder a una
    publicación oficial de alerta SENAPRED.
    """
    titulo_normalizado = normalizar_texto(titulo)

    return titulo_normalizado.startswith(
        INICIOS_TITULO_VALIDOS
    )


def extraer_fecha_datetime(fecha_texto):
    """
    Convierte DD-MM-AAAA HH:MM en datetime para ordenar.
    """
    try:
        return datetime.strptime(
            fecha_texto,
            "%d-%m-%Y %H:%M"
        )

    except (TypeError, ValueError):
        return datetime.min


def similitud_titulos(titulo_portada, titulo_detalle):
    """
    Compara palabras significativas entre el titulo visible
    en la portada y el titulo recuperado desde el detalle.
    """
    portada = normalizar_texto(titulo_portada)
    detalle = normalizar_texto(titulo_detalle)

    if not portada or not detalle:
        return 0.0

    palabras_ignoradas = {
        "se",
        "de",
        "del",
        "la",
        "las",
        "los",
        "para",
        "por",
        "y",
        "el",
        "en",
        "alerta",
        "temprana",
        "preventiva",
    }

    palabras_portada = {
        palabra
        for palabra in re.findall(
            r"[a-z0-9']+",
            portada
        )
        if (
            len(palabra) >= 3
            and palabra not in palabras_ignoradas
        )
    }

    palabras_detalle = {
        palabra
        for palabra in re.findall(
            r"[a-z0-9']+",
            detalle
        )
        if (
            len(palabra) >= 3
            and palabra not in palabras_ignoradas
        )
    }

    if not palabras_portada or not palabras_detalle:
        return 0.0

    coincidencias = (
        palabras_portada
        & palabras_detalle
    )

    base = min(
        len(palabras_portada),
        len(palabras_detalle)
    )

    if base == 0:
        return 0.0

    return len(coincidencias) / base


# ============================================================
# CATALOGO DE REGIONES
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
    "libertador bernardo o'higgins": "O´Higgins",
    "libertador bernardo ohiggins": "O´Higgins",
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
    "magallanes y de la antartica chilena": "Magallanes",
}


# ============================================================
# PROVINCIA A REGION
# ============================================================

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
    "antartica chilena": "Magallanes",
}


# ============================================================
# COMUNA A REGION
# ============================================================

COMUNA_REGION = {
    # Arica y Parinacota
    "arica": "Arica y Parinacota",
    "camarones": "Arica y Parinacota",
    "putre": "Arica y Parinacota",
    "general lagos": "Arica y Parinacota",

    # Tarapaca
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

    # Valparaiso
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
    "padre hurtado": "Metropolitana",
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
    "el monte": "Metropolitana",
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
    "licanten": "Maule",
    "curepto": "Maule",

    # Nuble
    "chillan": "Ñuble",
    "chillan viejo": "Ñuble",
    "pinto": "Ñuble",
    "coihueco": "Ñuble",

    # Biobio
    "concepcion": "Biobío",
    "talcahuano": "Biobío",
    "hualpen": "Biobío",
    "chiguayante": "Biobío",
    "san pedro de la paz": "Biobío",
    "coronel": "Biobío",
    "lota": "Biobío",
    "los angeles": "Biobío",

    # La Araucania
    "temuco": "La Araucanía",
    "padre las casas": "La Araucanía",
    "angol": "La Araucanía",
    "pucon": "La Araucanía",
    "villarrica": "La Araucanía",
    "curarrehue": "La Araucanía",

    # Los Rios
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

    # Aysen
    "coyhaique": "Aysén",
    "aysen": "Aysén",

    # Magallanes
    "punta arenas": "Magallanes",
    "puerto natales": "Magallanes",
}


# ============================================================
# FUNCIONES TERRITORIALES
# ============================================================

def normalizar_region(region):
    """
    Convierte variantes regionales al nombre utilizado
    en PE - Tiendas Falabella.
    """
    region_original = str(region).strip()
    region_normalizada = normalizar_texto(
        region_original
    )

    if not region_normalizada:
        return "No identificada"

    region_normalizada = re.sub(
        r"^(region|región)\s+",
        "",
        region_normalizada,
        flags=re.IGNORECASE
    ).strip()

    candidatos = [
        region_normalizada
    ]

    prefijos = [
        "de los ",
        "de las ",
        "del ",
        "de la ",
        "de ",
    ]

    for prefijo in prefijos:
        if region_normalizada.startswith(prefijo):
            candidatos.append(
                region_normalizada[
                    len(prefijo):
                ].strip()
            )

    for candidato in candidatos:
        if candidato in REGIONES_ALIAS:
            return REGIONES_ALIAS[candidato]

    return region_original


def buscar_regiones_explicitas(titulo):
    """
    Busca regiones escritas dentro del titulo.
    """
    titulo_normalizado = normalizar_texto(
        titulo
    )

    regiones = []

    aliases_ordenados = sorted(
        REGIONES_ALIAS.keys(),
        key=len,
        reverse=True
    )

    for alias in aliases_ordenados:
        patron = (
            r"\b"
            + re.escape(alias)
            + r"\b"
        )

        if re.search(
            patron,
            titulo_normalizado
        ):
            region = REGIONES_ALIAS[alias]

            if region not in regiones:
                regiones.append(region)

    return regiones


def buscar_provincias_en_texto(titulo):
    """
    Devuelve todas las provincias detectadas.
    """
    titulo_normalizado = normalizar_texto(
        titulo
    )

    segmento_territorial = re.split(
        r"\s+por\s+",
        titulo_normalizado,
        maxsplit=1
    )[0]

    provincias = []

    provincias_ordenadas = sorted(
        PROVINCIA_REGION.keys(),
        key=len,
        reverse=True
    )

    for provincia in provincias_ordenadas:
        patron = (
            r"\b"
            + re.escape(provincia)
            + r"\b"
        )

        if re.search(
            patron,
            segmento_territorial
        ):
            if provincia not in provincias:
                provincias.append(
                    provincia
                )

    return provincias


def buscar_comunas_en_texto(titulo):
    """
    Detecta comunas en el segmento territorial anterior a
    la palabra 'por'.
    """
    titulo_normalizado = normalizar_texto(
        titulo
    )

    segmento_territorial = re.split(
        r"\s+por\s+",
        titulo_normalizado,
        maxsplit=1
    )[0]

    comunas_encontradas = []

    comunas_ordenadas = sorted(
        COMUNA_REGION.keys(),
        key=len,
        reverse=True
    )

    for comuna in comunas_ordenadas:
        patron = (
            r"\b"
            + re.escape(comuna)
            + r"\b"
        )

        if re.search(
            patron,
            segmento_territorial
        ):
            comunas_encontradas.append(
                comuna
            )

    resultado = []

    for comuna in comunas_encontradas:
        if comuna not in resultado:
            resultado.append(
                comuna
            )

    return resultado


def regiones_desde_provincias(provincias):
    regiones = []

    for provincia in provincias:
        region = PROVINCIA_REGION.get(
            provincia
        )

        if region and region not in regiones:
            regiones.append(region)

    return regiones


def regiones_desde_comunas(comunas):
    regiones = []

    for comuna in comunas:
        region = COMUNA_REGION.get(
            comuna
        )

        if region and region not in regiones:
            regiones.append(region)

    return regiones


def contiene_indicador(
    titulo_normalizado,
    indicadores
):
    return any(
        indicador in titulo_normalizado
        for indicador in indicadores
    )


def obtener_region_y_cobertura(titulo):
    """
    Determina region, nivel de cobertura y ubicacion.

    Prioridad territorial:
    1. Expresion regional explicita.
    2. Expresion mixta provincia + comuna.
    3. Expresion provincial explicita.
    4. Expresion comunal explicita.
    5. Inferencias de respaldo.

    Las coberturas mixtas provincia + comuna se elevan a
    nivel regional para no dejar tiendas afectadas fuera,
    ya que Power Automate utiliza un unico nivel territorial.
    """
    titulo_normalizado = normalizar_texto(
        titulo
    )

    regiones_explicitas = (
        buscar_regiones_explicitas(
            titulo
        )
    )

    provincias = buscar_provincias_en_texto(
        titulo
    )

    comunas = buscar_comunas_en_texto(
        titulo
    )

    regiones_provincias = (
        regiones_desde_provincias(
            provincias
        )
    )

    regiones_comunas = (
        regiones_desde_comunas(
            comunas
        )
    )

    indicadores_regionales = [
        "para la region de ",
        "para las regiones de ",
        "para la region del ",
        "para las regiones del ",
        "para la region ",
        "para las regiones ",
        "en la region de ",
        "en las regiones de ",
        "region de ",
        "regiones de ",
    ]

    indicadores_provinciales = [
        "para la provincia de ",
        "para las provincias de ",
        "en la provincia de ",
        "en las provincias de ",
        "provincia de ",
        "provincias de ",
    ]

    indicadores_comunales = [
        "para la comuna de ",
        "para las comunas de ",
        "en la comuna de ",
        "en las comunas de ",
        "comuna de ",
        "comunas de ",
    ]

    es_regional = contiene_indicador(
        titulo_normalizado,
        indicadores_regionales
    )

    es_provincial = contiene_indicador(
        titulo_normalizado,
        indicadores_provinciales
    )

    es_comunal = contiene_indicador(
        titulo_normalizado,
        indicadores_comunales
    )

    # --------------------------------------------------------
    # 1. COBERTURA REGIONAL EXPLICITA
    # --------------------------------------------------------

    if es_regional and regiones_explicitas:
        return (
            ",".join(regiones_explicitas),
            "Región",
            ",".join(regiones_explicitas)
        )

    # --------------------------------------------------------
    # 2. COBERTURA MIXTA PROVINCIA + COMUNA
    # --------------------------------------------------------

    if es_provincial and es_comunal:
        regiones_mixtas = []

        for region in (
            regiones_provincias
            + regiones_comunas
            + regiones_explicitas
        ):
            if region not in regiones_mixtas:
                regiones_mixtas.append(
                    region
                )

        if regiones_mixtas:
            return (
                ",".join(regiones_mixtas),
                "Región",
                ",".join(regiones_mixtas)
            )

    # --------------------------------------------------------
    # 3. COBERTURA PROVINCIAL EXPLICITA
    # --------------------------------------------------------

    if es_provincial and provincias:
        return (
            ",".join(regiones_provincias)
            if regiones_provincias
            else "No identificada",
            "Provincia",
            ",".join(provincias)
        )

    # --------------------------------------------------------
    # 4. COBERTURA COMUNAL EXPLICITA
    # --------------------------------------------------------

    if es_comunal and comunas:
        return (
            ",".join(regiones_comunas)
            if regiones_comunas
            else "No identificada",
            "Comuna",
            ",".join(comunas)
        )

    # --------------------------------------------------------
    # 5. RESPALDOS
    # --------------------------------------------------------

    if regiones_explicitas:
        return (
            ",".join(regiones_explicitas),
            "Región",
            ",".join(regiones_explicitas)
        )

    if provincias:
        return (
            ",".join(regiones_provincias)
            if regiones_provincias
            else "No identificada",
            "Provincia",
            ",".join(provincias)
        )

    if comunas:
        return (
            ",".join(regiones_comunas)
            if regiones_comunas
            else "No identificada",
            "Comuna",
            ",".join(comunas)
        )

    return (
        "No identificada",
        "No identificada",
        ""
    )


# ============================================================
# EXTRACCION DE PORTADA
# ============================================================

def obtener_enlaces_candidatos(page):
    """
    Obtiene enlaces visibles de alertas y conserva el texto
    mostrado por SENAPRED junto con la URL.
    """
    enlaces = page.locator(
        'a[href*="/alerta/"]'
    ).evaluate_all(
        """
        links => links.map(link => ({
            texto: (
                link.innerText
                || link.textContent
                || link.getAttribute("aria-label")
                || link.getAttribute("title")
                || ""
            ).trim(),
            href: link.href
        }))
        """
    )

    candidatos = []
    urls_vistas = set()

    for enlace in enlaces:
        href = limpiar_url(
            enlace.get("href", "")
        )

        titulo_portada = str(
            enlace.get("texto", "")
        ).strip()

        if not href:
            continue

        if "/alerta/" not in href:
            continue

        if href in urls_vistas:
            continue

        if not titulo_es_alerta(
            titulo_portada
        ):
            continue

        urls_vistas.add(href)

        candidatos.append(
            {
                "titulo_portada": titulo_portada,
                "url": href,
            }
        )

        if len(candidatos) >= MAXIMO_ENLACES_CANDIDATOS:
            break

    return candidatos


# ============================================================
# EXTRACCION DE UNA ALERTA
# ============================================================

def procesar_alerta(
    context,
    candidato
):
    url = candidato["url"]

    titulo_portada = candidato[
        "titulo_portada"
    ]

    detalle_page = None

    try:
        detalle_page = context.new_page()

        detalle_page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        detalle_page.wait_for_timeout(
            5000
        )

        texto = detalle_page.locator(
            "body"
        ).inner_text()

        lineas = [
            linea.strip()
            for linea in texto.split("\n")
            if linea.strip()
        ]

        titulo = ""
        fecha = ""
        accion = ""
        tipo = "No definido"
        prioridad = "Baja"

        # ----------------------------------------------------
        # TITULO Y ACCION
        # ----------------------------------------------------

        for linea in lineas:
            linea_normalizada = normalizar_texto(
                linea
            )

            if linea_normalizada.startswith(
                INICIOS_TITULO_VALIDOS
            ):
                titulo = linea.strip()

                if linea_normalizada.startswith(
                    "monitoreo"
                ):
                    accion = "Monitoreo"

                elif linea_normalizada.startswith(
                    "se declara"
                ):
                    accion = "Se declara"

                elif linea_normalizada.startswith(
                    "se modifica"
                ):
                    accion = "Se modifica"

                elif linea_normalizada.startswith(
                    "se cancela"
                ):
                    accion = "Se cancela"

                elif linea_normalizada.startswith(
                    "se actualiza"
                ):
                    accion = "Se actualiza"

                break

        if not titulo:
            print(
                "ALERTA OMITIDA: "
                "no se encontro titulo"
            )
            print(url)
            return None

        # ----------------------------------------------------
        # VALIDAR TITULO Y URL
        # ----------------------------------------------------

        similitud = similitud_titulos(
            titulo_portada,
            titulo
        )

        if similitud < 0.55:
            print(
                "ALERTA OMITIDA: "
                "el titulo de portada no coincide "
                "con el detalle enlazado"
            )
            print(
                "PORTADA:",
                titulo_portada
            )
            print(
                "DETALLE:",
                titulo
            )
            print(
                "URL:",
                url
            )
            print(
                "SIMILITUD:",
                round(similitud, 2)
            )
            return None

        # ----------------------------------------------------
        # FECHA SENAPRED
        # ----------------------------------------------------

        fecha_match = re.search(
            r"\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}",
            texto
        )

        if fecha_match:
            fecha = fecha_match.group(
                0
            ).strip()

        if not fecha:
            print(
                "ALERTA OMITIDA: "
                "no se encontro fecha"
            )
            print(titulo)
            return None

        # ----------------------------------------------------
        # TIPO Y PRIORIDAD
        # ----------------------------------------------------

        titulo_normalizado = normalizar_texto(
            titulo
        )

        if "alerta roja" in titulo_normalizado:
            tipo = "Roja"
            prioridad = "Alta"

        elif (
            "alerta amarilla"
            in titulo_normalizado
        ):
            tipo = "Amarilla"
            prioridad = "Media"

        elif (
            "temprana preventiva"
            in titulo_normalizado
        ):
            tipo = "ATP"
            prioridad = "Baja"

        # ----------------------------------------------------
        # REGION Y COBERTURA
        # ----------------------------------------------------

        (
            region,
            nivel_cobertura,
            ubicacion_cobertura
        ) = obtener_region_y_cobertura(
            titulo
        )

        # ----------------------------------------------------
        # DETALLE LIMPIO
        # ----------------------------------------------------

        detalle = texto

        inicios_detalle = [
            "De acuerdo con la información",
            "En consideración a estos antecedentes",
        ]

        for texto_inicio in inicios_detalle:
            posicion_inicio = detalle.find(
                texto_inicio
            )

            if posicion_inicio >= 0:
                detalle = detalle[
                    posicion_inicio:
                ]
                break

        textos_pie = [
            "Volver",
            "Ayuda",
            "Biblio GRD",
            "Planos de evacuación",
            "Visor Chile Preparado",
            "Contacto",
        ]

        for texto_pie in textos_pie:
            posicion_pie = detalle.find(
                texto_pie
            )

            if posicion_pie > 0:
                detalle = detalle[
                    :posicion_pie
                ]
                break

        detalle = detalle.strip()

        # ----------------------------------------------------
        # IDENTIFICADOR ESTABLE
        # ----------------------------------------------------

        id_alerta = (
            f"{titulo}|{fecha}"
        )

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
            "detalle": detalle,
            "_fecha_orden": extraer_fecha_datetime(
                fecha
            ),
        }

        print(
            "OK:",
            titulo,
            "| Region:",
            region,
            "| NivelCobertura:",
            nivel_cobertura,
            "| UbicacionCobertura:",
            ubicacion_cobertura,
            "| URL:",
            url
        )

        return alerta

    except Exception as error:
        print(
            "ERROR PROCESANDO ALERTA"
        )
        print(url)
        print(str(error))

        return None

    finally:
        if detalle_page:
            detalle_page.close()


# ============================================================
# PROCESO PRINCIPAL DE EXTRACCION
# ============================================================

alertas_validas = []

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True
    )

    context = browser.new_context(
        timezone_id="America/Santiago"
    )

    page = context.new_page()

    page.goto(
        URL_ALERTAS_SENAPRED,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(
        10000
    )

    texto_portada = page.locator(
        "body"
    ).inner_text()

    with open(
        "portada_senapred.txt",
        "w",
        encoding="utf-8"
    ) as archivo:
        archivo.write(
            texto_portada
        )

    candidatos = obtener_enlaces_candidatos(
        page
    )

    print(
        "Enlaces candidatos encontrados:",
        len(candidatos)
    )

    for candidato in candidatos:
        alerta = procesar_alerta(
            context,
            candidato
        )

        if alerta:
            alertas_validas.append(
                alerta
            )

    browser.close()


# ============================================================
# ORDENAR Y LIMITAR ALERTAS
# ============================================================

alertas_validas.sort(
    key=lambda alerta: alerta[
        "_fecha_orden"
    ],
    reverse=True
)

alertas = alertas_validas[
    :MAXIMO_ALERTAS_SALIDA
]

for alerta in alertas:
    alerta.pop(
        "_fecha_orden",
        None
    )

print(
    "Alertas validas seleccionadas:",
    len(alertas)
)


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
    summary = (
        f"Accion={alerta['accion']}"
        f"|Tipo={alerta['tipo']}"
        f"|Region={alerta['region']}"
        f"|Prioridad={alerta['prioridad']}"
        f"|Fecha={alerta['fecha_senapred']}"
        f"|NivelCobertura="
        f"{alerta['nivel_cobertura']}"
        f"|UbicacionCobertura="
        f"{alerta['ubicacion_cobertura']}"
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
<language>es-cl</language>
<lastBuildDate>{fecha_rss}</lastBuildDate>
{items}
</channel>
</rss>
"""


with open(
    "rss.xml",
    "w",
    encoding="utf-8"
) as archivo:
    archivo.write(
        rss
    )


print(
    f"RSS generado con {len(alertas)} alertas"
)
