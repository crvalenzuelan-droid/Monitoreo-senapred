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

    for enlace in enlaces:

        href = enlace.get("href", "")

        if "/alerta/" in href:

            if href not in urls:

                urls.append(href)

    # SOLO LAS 5 MÁS RECIENTES
    urls = urls[:5]

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

            # ------------------------------------------------
            # TITULO / ACCION
            # ------------------------------------------------

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

            # ------------------------------------------------
            # FECHA SENAPRED
            # BUSCAR LA FECHA DEBAJO DEL TITULO
            # ------------------------------------------------

            for i, linea in enumerate(lineas):

                if titulo and linea == titulo:

                    for j in range(i + 1, min(i + 10, len(lineas))):

                        fecha_match = re.search(
                            r"\d{2}-\d{2}-\d{4}\s\d{2}:\d{2}",
                            lineas[j]
                        )

                        if fecha_match:

                            fecha = fecha_match.group(0)
                            break

                    break

            # ------------------------------------------------
            # TIPO ALERTA
            # ------------------------------------------------

            if "Alerta Roja" in titulo:
                tipo = "Roja"
                prioridad = "Alta"

            elif "Alerta Amarilla" in titulo:
                tipo = "Amarilla"
                prioridad = "Media"

            elif "Temprana Preventiva" in titulo:
                tipo = "ATP"
                prioridad = "Baja"

            else:
                tipo = "No definido"
                prioridad = "Baja"

            # ------------------------------------------------
            # REGION
            # ------------------------------------------------

            try:

                if "para la Región de " in titulo:

                    region = (
                        titulo
                        .split("para la Región de ")[1]
                        .split(" por ")[0]
                    )

                elif "para la Región del " in titulo:

                    region = (
                        titulo
                        .split("para la Región del ")[1]
                        .split(" por ")[0]
                    )

                elif "para la Región de los " in titulo:

                    region = (
                        titulo
                        .split("para la Región de los ")[1]
                        .split(" por ")[0]
                    )

                elif "para la Región de las " in titulo:

                    region = (
                        titulo
                        .split("para la Región de las ")[1]
                        .split(" por ")[0]
                    )

                elif "para las comunas de " in titulo:

                    region = (
                        titulo
                        .split("para las comunas de ")[1]
                        .split(" por ")[0]
                    )

                elif "para la comuna de " in titulo:

                    region = (
                        titulo
                        .split("para la comuna de ")[1]
                        .split(" por ")[0]
                    )

                elif "para la Provincia de " in titulo:

                    region = (
                        titulo
                        .split("para la Provincia de ")[1]
                        .split(" por ")[0]
                    )

                else:

                    region = "No identificada"

            except:

                region = "No identificada"

            # ------------------------------------------------
            # LIMPIEZA DE DETALLE
            # ------------------------------------------------

            detalle = texto

            inicio = detalle.find(
                "De acuerdo con la información"
            )

            if inicio == -1:

                inicio = detalle.find(
                    "En consideración a estos antecedentes"
                )

            if inicio > 0:

                detalle = detalle[inicio:]

            pie = [
                "Volver",
                "Ayuda",
                "Biblio GRD",
                "Planos de evacuación",
                "Visor Chile Preparado",
                "Contacto"
            ]

            for x in pie:

                pos = detalle.find(x)

                if pos > 0:

                    detalle = detalle[:pos]
                    break

            detalle = detalle.strip()

            id_alerta = f"{titulo}|{fecha}"

            alerta = {
                "id_alerta": id_alerta,
                "accion": accion,
                "tipo": tipo,
                "prioridad": prioridad,
                "region": region,
                "fecha_senapred": fecha,
                "titulo": titulo,
                "url": url,
                "detalle": detalle
            }

            alertas.append(alerta)

            print("OK:", titulo)

            detalle_page.close()

        except Exception as error:

            print("ERROR PROCESANDO ALERTA")
            print(url)
            print(str(error))

            continue

    browser.close()

# ------------------------------------------------
# JSON
# ------------------------------------------------

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

# ------------------------------------------------
# RSS
# ------------------------------------------------

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
    )

    items += f"""
<item>
<title><![CDATA[{alerta['titulo']}]]></title>
<link>{alerta['url']}</link>
<guid isPermaLink="false"><![CDATA[{alerta['id_alerta']}]]></guid>
<description><![CDATA[{summary}]]></description>
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
