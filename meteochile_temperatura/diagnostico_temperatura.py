from playwright.sync_api import sync_playwright
import json
import time


URL_PRINCIPAL = (
    "https://www.meteochile.gob.cl/"
    "PortalDMC-web/index.xhtml"
)


def guardar_texto(ruta, contenido):

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(contenido)


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
        ),
        extra_http_headers={
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,image/avif,"
                "image/webp,*/*;q=0.8"
            ),
            "Accept-Language": (
                "es-CL,es;q=0.9,en;q=0.8"
            ),
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
    )

    page = context.new_page()

    # ---------------------------------
    # REGISTRAR SOLICITUDES DE RED
    # ---------------------------------

    solicitudes = []

    def registrar_respuesta(respuesta):

        url = respuesta.url

        palabras_clave = [
            "pronost",
            "temperatura",
            "ciudad",
            "localidad",
            "meteor",
            "json",
            "xml",
            "servicio"
        ]

        if any(
            palabra in url.lower()
            for palabra in palabras_clave
        ):

            solicitudes.append({
                "url": url,
                "estado": respuesta.status,
                "tipo": (
                    respuesta.request.resource_type
                )
            })

    page.on(
        "response",
        registrar_respuesta
    )

    # ---------------------------------
    # ABRIR METEOCHILE
    # ---------------------------------

    pagina_cargada = False
    ultimo_error = ""

    for intento in range(1, 4):

        try:

            print("")
            print(
                "-----------------------------------"
            )
            print(
                f"Intento {intento} de 3"
            )
            print(
                f"URL: {URL_PRINCIPAL}"
            )
            print(
                "-----------------------------------"
            )

            respuesta = page.goto(
                URL_PRINCIPAL,
                wait_until="domcontentloaded",
                timeout=120000
            )

            page.wait_for_timeout(
                20000
            )

            if respuesta is not None:

                print(
                    "Estado HTTP:",
                    respuesta.status
                )

            texto = page.locator(
                "body"
            ).inner_text(
                timeout=30000
            )

            if texto.strip():

                pagina_cargada = True
                break

            ultimo_error = (
                "La página respondió sin "
                "contenido visible."
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

                time.sleep(15)

    if not pagina_cargada:

        guardar_texto(
            "meteochile_temperatura/"
            "error_temperatura.txt",
            ultimo_error
        )

        browser.close()

        raise RuntimeError(
            "No fue posible acceder "
            "a MeteoChile."
        )

    # ---------------------------------
    # GUARDAR TEXTO VISIBLE
    # ---------------------------------

    texto_pagina = page.locator(
        "body"
    ).inner_text()

    guardar_texto(
        "meteochile_temperatura/"
        "texto_temperatura.txt",
        texto_pagina
    )

    # ---------------------------------
    # GUARDAR HTML
    # ---------------------------------

    html_pagina = page.content()

    guardar_texto(
        "meteochile_temperatura/"
        "pagina_temperatura.html",
        html_pagina
    )

    # ---------------------------------
    # CAPTURA DE PANTALLA
    # ---------------------------------

    page.screenshot(
        path=(
            "meteochile_temperatura/"
            "captura_temperatura.png"
        ),
        full_page=True
    )

    # ---------------------------------
    # EXTRAER ENLACES
    # ---------------------------------

    enlaces = page.locator(
        "a"
    ).evaluate_all("""
        enlaces => enlaces.map(enlace => ({
            texto: (
                enlace.innerText || ""
            ).trim(),
            href: enlace.href || ""
        }))
    """)

    with open(
        "meteochile_temperatura/"
        "enlaces_temperatura.json",
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            enlaces,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    # ---------------------------------
    # EXTRAER SCRIPTS
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
        "meteochile_temperatura/"
        "scripts_temperatura.json",
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            scripts,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    # ---------------------------------
    # GUARDAR SOLICITUDES DE RED
    # ---------------------------------

    with open(
        "meteochile_temperatura/"
        "solicitudes_temperatura.json",
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            solicitudes,
            archivo,
            ensure_ascii=False,
            indent=2
        )

    print("")
    print(
        "==================================="
    )
    print(
        "DIAGNOSTICO TEMPERATURA TERMINADO"
    )
    print(
        "==================================="
    )
    print(
        "Archivos generados:"
    )
    print(
        "texto_temperatura.txt"
    )
    print(
        "pagina_temperatura.html"
    )
    print(
        "captura_temperatura.png"
    )
    print(
        "enlaces_temperatura.json"
    )
    print(
        "scripts_temperatura.json"
    )
    print(
        "solicitudes_temperatura.json"
    )
    print(
        "==================================="
    )

    browser.close()
