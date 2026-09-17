from playwright.sync_api import sync_playwright
import json
import re

alertas = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto("https://www.senapred.cl/alertas")

    page.wait_for_timeout(10000)

    enlaces = page.locator("a").evaluate_all("""
        links => links.map(link => ({
            texto: link.innerText,
            href: link.href
        }))
    """)

    urls = []

    for enlace in enlaces:

        href = enlace.get("href", "")

        if "/alerta/" in href:

            if href not in urls:

                urls.append(href)

    # Solo las últimas 10
    urls = urls[:10]

    print(f"Alertas encontradas: {len(urls)}")

    for url in urls:

        try:

            detalle_page = browser.new_page()

            detalle_page.goto(url)

            detalle_page.wait_for_timeout(5000)

            texto = detalle_page.locator("body").inner_text()

            lineas = [x.strip() for x in texto.split("\n") if x.strip()]

            titulo = ""
            fecha = ""
            accion = ""
            tipo = ""
            region = ""

            # Buscar título y acción
            for linea in lineas:

                if (
                    linea.startswith("Monitoreo")
                    or linea.startswith("Se declara")
                    or linea.startswith("Se modifica")
                    or linea.startswith("Se cancela")
                    or linea.startswith("Se actualiza")
                ):

                    titulo = linea

                    if linea.startswith("Monitoreo"):
                        accion = "Monitoreo"

                    elif linea.startswith("Se declara"):
                        accion = "Se declara"

                    elif linea.startswith("Se modifica"):
                        accion = "Se modifica"

                    elif linea.startswith("Se cancela"):
                        accion = "Se cancela"

                    elif linea.startswith("Se actualiza"):
                        accion = "Se actualiza"

                    break

            # Buscar fecha SENAPRED
            fecha_match = re.search(
                r"\d{2}-\d{2}-\d{4}\s\d{2}:\d{2}",
                texto
            )

            if fecha_match:
                fecha = fecha_match.group(0)

            # Tipo alerta
            if "Alerta Roja" in titulo:
                tipo = "Roja"

            elif "Alerta Amarilla" in titulo:
                tipo = "Amarilla"

            elif "Temprana Preventiva" in titulo:
                tipo = "ATP"

            else:
                tipo = "No definido"

            # Región / cobertura
            if "para la Región de " in titulo:

                region = (
                    titulo.split("para la Región de ")[1]
                    .split(" por ")[0]
                )

            elif "para las comunas de " in titulo:

                region = (
                    titulo.split("para las comunas de ")[1]
                    .split(" por ")[0]
                )

            elif "para la Provincia de " in titulo:

                region = (
                    titulo.split("para la Provincia de ")[1]
                    .split(" por ")[0]
                )

            else:

                region = "No identificada"

            alerta = {
                "id_alerta": f"{titulo}|{fecha}",
                "accion": accion,
                "tipo": tipo,
                "region": region,
                "fecha_senapred": fecha,
                "titulo": titulo,
                "url": url,
                "detalle": texto[:15000]
            }

            alertas.append(alerta)

            print("OK:", titulo)

            detalle_page.close()

        except Exception as e:

            print("ERROR:", url)
            print(str(e))

    browser.close()

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

print(f"Alertas procesadas: {len(alertas)}")
