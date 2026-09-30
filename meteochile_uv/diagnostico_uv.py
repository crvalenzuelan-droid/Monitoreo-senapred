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
                        "Página UV cargada correctamente."
                    )

                    break

                ultimo_error = (
                    "La página respondió, pero el cuerpo "
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

    if not pagina_cargada:

        mensaje_error = (
            "No fue posible acceder a la página UV "
            "de MeteoChile desde GitHub Actions.\n\n"
            f"Último error:\n{ultimo_error}\n"
        )

        guardar_error(mensaje_error)

        print("")
        print(mensaje_error)

        browser.close()

        raise RuntimeError(
            "MeteoChile no respondió después "
            "de todos los intentos."
        )

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

    html_pagina = page.content()

    with open(
        "meteochile_uv/pagina_uv.html",
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(html_pagina)

    page.screenshot(
        path="meteochile_uv/captura_uv.png",
        full_page=True
    )

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

    print("")
    print("-----------------------------------")
    print("Diagnóstico UV terminado.")
    print(f"URL utilizada: {url_utilizada}")
    print("-----------------------------------")
    print("")
    print("Archivos generados:")
    print("meteochile_uv/texto_uv.txt")
    print("meteochile_uv/pagina_uv.html")
    print("meteochile_uv/captura_uv.png")
    print("meteochile_uv/enlaces_uv.txt")
    print("meteochile_uv/scripts_uv.txt")

    browser.close()
