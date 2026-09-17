from playwright.sync_api import sync_playwright
from datetime import datetime, timezone

titulo = ""
fecha = ""

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto("https://www.senapred.cl/alertas")

    page.wait_for_timeout(10000)

    texto = page.locator("body").inner_text()

    lineas = [x.strip() for x in texto.split("\n") if x.strip()]

    for i, linea in enumerate(lineas):

        if linea.startswith("Monitoreo") or linea.startswith("Se declara"):

            titulo = linea

            if i + 1 < len(lineas):
                fecha = lineas[i + 1]

            break

    browser.close()

# Tipo de alerta

tipo_alerta = "No definido"
prioridad = "Baja"

if "Alerta Roja" in titulo:
    tipo_alerta = "Roja"
    prioridad = "Alta"

elif "Alerta Amarilla" in titulo:
    tipo_alerta = "Amarilla"
    prioridad = "Media"

elif "Temprana Preventiva" in titulo:
    tipo_alerta = "ATP"
    prioridad = "Baja"

# Región / zona

region = "No identificada"

if "para la Región de " in titulo:
    region = titulo.split("para la Región de ")[1].split(" por ")[0]

elif "para las comunas de " in titulo:
    region = titulo.split("para las comunas de ")[1].split(" por ")[0]

elif "para la Provincia de " in titulo:
    region = titulo.split("para la Provincia de ")[1].split(" por ")[0]

# IDs

id_alerta = f"{titulo}|{fecha}"

fecha_rss = datetime.now(timezone.utc).strftime(
    "%a, %d %b %Y %H:%M:%S GMT"
)

rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>

<title>Alertas SENAPRED</title>
<link>https://www.senapred.cl</link>

<item>
<title><![CDATA[{titulo}]]></title>

<link>https://www.senapred.cl/alertas</link>

<guid isPermaLink="false"><![CDATA[{id_alerta}]]></guid>

<description><![CDATA[{fecha}]]></description>

<category><![CDATA[{tipo_alerta}]]></category>

<region><![CDATA[{region}]]></region>

<priority><![CDATA[{prioridad}]]></priority>

<pubDate>{fecha_rss}</pubDate>

</item>

</channel>
</rss>
"""

with open("rss.xml", "w", encoding="utf-8") as archivo:
    archivo.write(rss)

print("RSS actualizado")
print("ALERTA:", titulo)
print("TIPO:", tipo_alerta)
print("REGION:", region)
print("PRIORIDAD:", prioridad)
