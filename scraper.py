from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
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

    for e in enlaces:

        href = e.get("href", "")

        if "/alerta/" in href:

            if href not in urls:

                urls.append(href)

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

            fecha_regex = re.search(
                r"\d{2}-\d{2}-\d{4}\s\d{2}:\d{2}",
                texto
            )

            if fecha_regex:
                fecha = fecha_regex.group()

            if "Alerta Roja" in titulo:
                tipo = "Roja"

            elif "Alerta Amarilla" in titulo:
                tipo = "Amarilla"

            elif "Temprana Preventiva" in titulo:
                tipo = "ATP"

            else:
                tipo = "No definido"

            if "para la Región de " in titulo:

                region = (
                    titulo
                    .split("para la Región de ")[1]
                    .split(" por ")[0]
                )

            elif "para las comunas de " in titulo:

                region = (
                    titulo
                    .split("para 
