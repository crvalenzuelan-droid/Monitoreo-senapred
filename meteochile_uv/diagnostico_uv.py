from playwright.sync_api import sync_playwright
import time


URLS_UV = [
    (
        "https://www.meteochile.gob.cl/"
        "PortalDMC-web/otros_pronosticos/radiacion_uv.xhtml"
    ),
    (
        "https://meteochile.gob.cl/"
        "PortalDMC-web/otros_pronosticos/radiacion_uv.xhtml"
    )
]

URL_SCRIPT_UV = (
    "https://archivos.meteochile.gob.cl/"
    "portaldmc/localJS/js/otrosPronosticos/"
    "radiacionUv.js"
)


def guardar_error(mensaje):

    with open(
        "meteochile_uv/error_uv.txt",
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(mensaje)


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
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        extra_http_headers={
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,image/avif,"
                "image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "es-CL,es;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1"
        }
    )

    page = context.new_page()

    pagina_cargada = False
    url_utilizada = ""
    ultimo_error = ""

    # ---------------------------------
    # ABRIR PAGINA DE METEOCHILE
    # ---------------------------------

    for url in URLS_UV:

        if pagina_cargada:
            break

        for intento in range(1, 4):

            try:

                print("")
                print("-----------------------------------")
                print(f"URL: {url}")
                print(f"Intento: {intento} de 3")
                print("-----------------------------------")

                respuesta = page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=120000
                )

                page.wait_for_timeout(15000)

                if respuesta is not None:

                    print(
                        "Estado HTTP:",
                        respuesta.status
                    )

                texto_pagina = page.locator(
                    "body"
                ).inner_text(
                    timeout=30000
                )

                if texto_pagina.strip():

                    pagina_cargada = True
                    url_utilizada = url

                    print(
                        "Pagina UV cargada correctamente."
                    )

                    break

                ultimo_error = (
                    "La pagina respondio, pero el cuerpo "
                    "no contiene texto."
                )

                print(ultimo_error)

            except Exception as error:

                ultimo_error = str(error)

                print(
                    "Error al abrir MeteoChile:"
                )

                print(ultimo_error)

                if intento < 3:

                    print(
                        "Esperando 15 segundos antes "
                        "del siguiente intento..."
                    )

                    time.sleep(15)

    # ---------------------------------
    # CONTROL DE ERROR DE PAGINA
    # ---------------------------------

    if not pagina_cargada:

        mensaje_error = (
            "No fue posible acceder a la pagina UV "
            "de MeteoChile desde GitHub Actions.\n\n"
            f"Ultimo error:\n{ultimo_error}\n"
        )

        guardar_error(mensaje_error)

        print("")
        print(mensaje_error)

        browser.close()

        raise RuntimeError(
            "MeteoChile no respondio despues "
            "de todos los intentos."
        )

    # ---------------------------------
    # GUARDAR TEXTO VISIBLE
    # ---------------------------------

    texto_pagina = page.locator(
        "body"
    ).inner_text()

    with open(
        "meteochile_uv/texto_uv.txt",
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(
            f"URL utilizada: {url_utilizada}\n\n"
        )

        archivo.write(texto_pagina)

    # ---------------------------------
    # GUARDAR HTML COMPLETO
    # ---------------------------------

    html_pagina = page.content()

    with open(
        "meteochile_uv/pagina_uv.html",
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(html_pagina)

    # ---------------------------------
    # GUARDAR CAPTURA COMPLETA
    # ---------------------------------

    page.screenshot(
        path="meteochile_uv/captura_uv.png",
        full_page=True
    )

    # ---------------------------------
    # EXTRAER ENLACES
    # ---------------------------------

    enlaces = page.locator(
        "a"
    ).evaluate_all("""
        links => links.map(link => ({
            texto: (link.innerText || "").trim(),
            href: link.href
        }))
    """)

    with open(
        "meteochile_uv/enlaces_uv.txt",
        "w",
        encoding="utf-8"
    ) as archivo:

        for enlace in enlaces:

            texto = enlace.get(
                "texto",
                ""
            )

            href = enlace.get(
                "href",
                ""
            )

            archivo.write(
                f"{texto} | {href}\n"
            )

    # ---------------------------------
    # EXTRAER LISTADO DE SCRIPTS
    # ---------------------------------

    scripts = page.locator(
        "script"
    ).evaluate_all("""
        scripts => scripts.map(script => ({
            src: script.src || "",
            texto: script.innerText || ""
        }))
    """)

    with open(
        "meteochile_uv/scripts_uv.txt",
        "w",
        encoding="utf-8"
    ) as archivo:

        for script in scripts:

            archivo.write(
                "====================================\n"
            )

            archivo.write(
                f"SRC: {script.get('src', '')}\n"
            )

            archivo.write(
                script.get(
                    "texto",
                    ""
                )
            )

            archivo.write("\n")

    # ---------------------------------
    # DESCARGAR RADIACIONUV.JS
    # ---------------------------------

    try:

        print("")
        print("-----------------------------------")
        print("Descargando radiacionUv.js...")
        print("-----------------------------------")

        respuesta_script = context.request.get(
            URL_SCRIPT_UV,
            timeout=120000,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/140.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/javascript,application/javascript,"
                    "application/ecmascript,*/*;q=0.8"
                ),
                "Referer": url_utilizada
            }
        )

        print(
            "Estado radiacionUv.js:",
            respuesta_script.status
        )

        if not respuesta_script.ok:

            raise RuntimeError(
                "La descarga de radiacionUv.js "
                f"respondio con estado {respuesta_script.status}"
            )

        contenido_script_uv = respuesta_script.text()

        if not contenido_script_uv.strip():

            raise RuntimeError(
                "radiacionUv.js fue descargado, "
                "pero su contenido esta vacio."
            )

        with open(
            "meteochile_uv/radiacionUv.js",
            "w",
            encoding="utf-8"
        ) as archivo:

            archivo.write(contenido_script_uv)

        print(
            "Archivo radiacionUv.js guardado correctamente."
        )

    except Exception as error:

        mensaje_error_script = (
            "No fue posible descargar radiacionUv.js.\n\n"
            f"Error:\n{str(error)}\n"
        )

        print(mensaje_error_script)

        with open(
            "meteochile_uv/error_script_uv.txt",
            "w",
            encoding="utf-8"
        ) as archivo:

            archivo.write(mensaje_error_script)

    # ---------------------------------
    # RESUMEN FINAL
    # ---------------------------------

    print("")
    print("-----------------------------------")
    print("Diagnostico UV terminado.")
    print(f"URL utilizada: {url_utilizada}")
    print("-----------------------------------")
    print("")
    print("Archivos generados:")
    print("meteochile_uv/texto_uv.txt")
    print("meteochile_uv/pagina_uv.html")
    print("meteochile_uv/captura_uv.png")
    print("meteochile_uv/enlaces_uv.txt")
    print("meteochile_uv/scripts_uv.txt")
    print("meteochile_uv/radiacionUv.js")

        # ---------------------------------
    # DIAGNOSTICO PAGINA UV REGIONAL
    # ---------------------------------

    url_uv_regional = (
        "https://www.meteochile.gob.cl/"
        "PortalDMC-web/otros_pronosticos/"
        "radiacion_uv_region.xhtml"
        "?estacion=330020"
    )

    try:

        print("")
        print("-----------------------------------")
        print("Abriendo pagina UV regional...")
        print(url_uv_regional)
        print("-----------------------------------")

        pagina_regional = context.new_page()

        respuesta_regional = pagina_regional.goto(
            url_uv_regional,
            wait_until="domcontentloaded",
            timeout=120000
        )

        pagina_regional.wait_for_timeout(15000)

        if respuesta_regional is not None:

            print(
                "Estado pagina regional:",
                respuesta_regional.status
            )

        texto_regional = pagina_regional.locator(
            "body"
        ).inner_text(
            timeout=30000
        )

        with open(
            "meteochile_uv/texto_uv_regional.txt",
            "w",
            encoding="utf-8"
        ) as archivo:

            archivo.write(texto_regional)

        html_regional = pagina_regional.content()

        with open(
            "meteochile_uv/pagina_uv_regional.html",
            "w",
            encoding="utf-8"
        ) as archivo:

            archivo.write(html_regional)

        pagina_regional.screenshot(
            path=(
                "meteochile_uv/"
                "captura_uv_regional.png"
            ),
            full_page=True
        )

        recursos_regionales = (
            pagina_regional.locator(
                "script, img, iframe"
            ).evaluate_all("""
                elementos => elementos.map(elemento => ({
                    etiqueta: elemento.tagName,
                    src: elemento.src || "",
                    id: elemento.id || "",
                    clase: elemento.className || ""
                }))
            """)
        )

        with open(
            "meteochile_uv/"
            "recursos_uv_regional.txt",
            "w",
            encoding="utf-8"
        ) as archivo:

            for recurso in recursos_regionales:

                archivo.write(
                    f"ETIQUETA: "
                    f"{recurso.get('etiqueta', '')}\n"
                )

                archivo.write(
                    f"SRC: "
                    f"{recurso.get('src', '')}\n"
                )

                archivo.write(
                    f"ID: "
                    f"{recurso.get('id', '')}\n"
                )

                archivo.write(
                    f"CLASE: "
                    f"{recurso.get('clase', '')}\n"
                )

                archivo.write(
                    "-----------------------------------\n"
                )

        print(
            "Diagnostico regional UV completado."
        )

        pagina_regional.close()

    except Exception as error:

        print(
            "No fue posible diagnosticar "
            "la pagina UV regional:"
        )

        print(str(error))
        
    browser.close()
