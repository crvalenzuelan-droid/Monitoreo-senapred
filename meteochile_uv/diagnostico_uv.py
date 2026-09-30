from playwright.sync_api import sync_playwright


URL_UV = (
    "https://www.meteochile.gob.cl/"
    "PortalDMC-web/otros_pronosticos/radiacion_uv.xhtml"
)


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    context = browser.new_context(
        timezone_id="America/Santiago",
        locale="es-CL",
        viewport={
            "width": 1920,
            "height": 1080
        }
    )

    page = context.new_page()

    print("Abriendo página de pronóstico UV...")

    page.goto(
        URL_UV,
        wait_until="domcontentloaded",
        timeout=120000
    )

    page.wait_for_timeout(15000)

    texto_pagina = page.locator("body").inner_text()

    with open(
        "meteochile_uv/texto_uv.txt",
        "w",
        encoding="utf-8"
    ) as archivo:

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

    enlaces = page.locator("a").evaluate_all("""
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

            texto = enlace.get("texto", "")
            href = enlace.get("href", "")

            archivo.write(
                f"{texto} | {href}\n"
            )

    scripts = page.locator("script").evaluate_all("""
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
                script.get("texto", "")
            )

            archivo.write("\n")

    print("Diagnóstico UV terminado.")
    print("")
    print("Archivos generados:")
    print("meteochile_uv/texto_uv.txt")
    print("meteochile_uv/pagina_uv.html")
    print("meteochile_uv/captura_uv.png")
    print("meteochile_uv/enlaces_uv.txt")
    print("meteochile_uv/scripts_uv.txt")

    browser.close()
