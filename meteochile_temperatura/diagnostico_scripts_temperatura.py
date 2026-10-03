from playwright.sync_api import sync_playwright
import json
import re
import time


URL_PRONOSTICO = (
    "https://www.meteochile.gob.cl/"
    "PortalDMC-web/pronostico_general.xhtml"
)

SCRIPTS = [
    {
        "nombre": "pronostico.js",
        "url": (
            "https://archivos.meteochile.gob.cl/"
            "portaldmc/meteochile/js/"
            "pronostico.js?version=1"
        )
    },
    {
        "nombre": "render_pronostico.js",
        "url": (
            "https://archivos.meteochile.gob.cl/"
            "portaldmc/localJS/js/pronosticoGeneral/"
            "render_pronostico.js?version=1"
        )
    },
    {
        "nombre": (
            "renderPronosticoTemperaturasExtremas.js"
        ),
        "url": (
            "https://archivos.meteochile.gob.cl/"
            "portaldmc/localJS/js/pronosticoGeneral/"
            "renderPronosticoTemperaturasExtremas.js"
            "?version=1"
        )
    },
    {
        "nombre": "temperaturas_extremas.js",
        "url": (
            "https://archivos.meteochile.gob.cl/"
            "portaldmc/meteochile/js/"
            "temperaturas_extremas.js?version=1"
        )
    },
    {
        "nombre": "periodo_pronostico.js",
        "url": (
            "https://archivos.meteochile.gob.cl/"
            "portaldmc/localJS/js/pronosticoGeneral/"
            "periodo_pronostico.js"
        )
    }
]


def guardar_archivo(ruta, contenido):

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(contenido)


def extraer_hallazgos(nombre, contenido):

    hallazgos = []

    lineas = contenido.splitlines()

    patrones = [
        "ajax",
        "getjson",
        "fetch",
        "url:",
        "temperatura",
        "pronostico",
        "mínima",
        "minima",
        "máxima",
        "maxima",
        "servicio",
        "json",
        "xml",
        "localidad",
        "ciudad",
        "region",
        "estacion",
        "endpoint"
    ]

    for numero, linea in enumerate(
        lineas,
        start=1
    ):

        linea_minuscula = linea.lower()

        if any(
            patron in linea_minuscula
            for patron in patrones
        ):

            inicio = max(
                0,
                numero - 4
            )

            fin = min(
                len(lineas),
                numero + 3
            )

            bloque = "\n".join(
                lineas[inicio:fin]
            )

            hallazgos.append({
                "archivo": nombre,
                "linea": numero,
                "contenido": bloque
            })

    urls = re.findall(
        r"""https?://[^\s"'<>]+""",
        contenido
    )

    for url in urls:

        hallazgos.append({
            "archivo": nombre,
            "linea": 0,
            "contenido": (
                f"URL ENCONTRADA: {url}"
            )
        })

    return hallazgos


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features="
            "AutomationControlled",
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
        ),
        extra_http_headers={
            "Accept-Language": (
                "es-CL,es;q=0.9,en;q=0.8"
            ),
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
    )

    page = context.new_page()

    pagina_abierta = False
    ultimo_error = ""

    # ---------------------------------
    # ABRIR PAGINA PRINCIPAL
    # ---------------------------------

    for intento in range(1, 4):

        try:

            print("")
            print(
                "Abriendo página de "
                "pronóstico general"
            )

            print(
                f"Intento {intento} de 3"
            )

            respuesta = page.goto(
                URL_PRONOSTICO,
                wait_until="domcontentloaded",
                timeout=120000
            )

            page.wait_for_timeout(
                15000
            )

            if respuesta is not None:

                print(
                    "Estado página:",
                    respuesta.status
                )

            texto = page.locator(
                "body"
            ).inner_text(
                timeout=30000
            )

            if texto.strip():

                pagina_abierta = True
                break

        except Exception as error:

            ultimo_error = str(error)

            print(
                "Error:",
                ultimo_error
            )

            if intento < 3:

                time.sleep(15)

    if not pagina_abierta:

        browser.close()

        raise RuntimeError(
            "No fue posible abrir la página "
            f"de pronóstico: {ultimo_error}"
        )

    hallazgos_totales = []
    resultados_descarga = []

    # ---------------------------------
    # DESCARGAR SCRIPTS
    # ---------------------------------

    for script in SCRIPTS:

        nombre = script["nombre"]
        url = script["url"]

        print("")
        print(
            "-----------------------------------"
        )
        print(
            f"Descargando: {nombre}"
        )
        print(
            f"URL: {url}"
        )
        print(
            "-----------------------------------"
        )

        contenido = ""
        error_script = ""
        estado = None

        for intento in range(1, 4):

            try:

                respuesta_script = (
                    context.request.get(
                        url,
                        timeout=120000,
                        headers={
                            "User-Agent": (
                                "Mozilla/5.0 "
                                "(Windows NT 10.0; "
                                "Win64; x64) "
                                "AppleWebKit/537.36 "
                                "(KHTML, like Gecko) "
                                "Chrome/140.0.0.0 "
                                "Safari/537.36"
                            ),
                            "Accept": (
                                "text/javascript,"
                                "application/javascript,"
                                "application/ecmascript,"
                                "*/*;q=0.8"
                            ),
                            "Referer": (
                                URL_PRONOSTICO
                            )
                        }
                    )
                )

                estado = (
                    respuesta_script.status
                )

                print(
                    f"Intento {intento}: "
                    f"estado {estado}"
                )

                if respuesta_script.ok:

                    contenido = (
                        respuesta_script.text()
                    )

                    if contenido.strip():

                        break

                error_script = (
                    f"Respuesta HTTP {estado}"
                )

            except Exception as error:

                error_script = str(error)

                print(
                    "Error:",
                    error_script
                )

            if intento < 3:

                time.sleep(10)

        resultados_descarga.append({
            "archivo": nombre,
            "url": url,
            "estado": estado,
            "bytes": len(
                contenido.encode(
                    "utf-8"
                )
            ),
            "error": error_script
        })

        if not contenido.strip():

            print(
                f"No fue posible descargar "
                f"{nombre}"
            )

            continue

        ruta_salida = (
            "meteochile_temperatura/"
            + nombre
        )

        guardar_archivo(
            ruta_salida,
            contenido
        )

        print(
            f"Guardado: {ruta_salida}"
        )

        hallazgos = extraer_hallazgos(
            nombre,
            contenido
        )

        hallazgos_totales.extend(
            hallazgos
        )

        print(
            "Hallazgos encontrados:",
            len(hallazgos)
        )

    # ---------------------------------
    # GUARDAR RESUMEN
    # ---------------------------------

    with open(
        "meteochile_temperatura/"
        "resultado_descarga_scripts.json",
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            resultados_descarga,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    with open(
        "meteochile_temperatura/"
        "hallazgos_scripts_temperatura.json",
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            hallazgos_totales,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    with open(
        "meteochile_temperatura/"
        "hallazgos_scripts_temperatura.txt",
        "w",
        encoding="utf-8"
    ) as archivo:

        for hallazgo in hallazgos_totales:

            archivo.write(
                "===================================\n"
            )

            archivo.write(
                f"ARCHIVO: "
                f"{hallazgo['archivo']}\n"
            )

            archivo.write(
                f"LÍNEA: "
                f"{hallazgo['linea']}\n"
            )

            archivo.write(
                "-----------------------------------\n"
            )

            archivo.write(
                hallazgo["contenido"]
            )

            archivo.write(
                "\n\n"
            )

    print("")
    print(
        "==================================="
    )
    print(
        "DIAGNÓSTICO DE SCRIPTS TERMINADO"
    )
    print(
        "==================================="
    )
    print(
        "Scripts analizados:",
        len(SCRIPTS)
    )
    print(
        "Hallazgos:",
        len(hallazgos_totales)
    )
    print(
        "Resultados guardados en "
        "meteochile_temperatura"
    )
    print(
        "==================================="
    )

    browser.close()
