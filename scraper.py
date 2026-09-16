from playwright.sync_api import sync_playwright

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

rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Alertas SENAPRED</title>
<link>https://www.senapred.cl</link>
<description>Alertas SENAPRED</description>

<item>
<title>{titulo}</title>
<description>{fecha}</description>
<pubDate>{fecha}</pubDate>
</item>

</channel>
</rss>
"""

with open("rss.xml", "w", encoding="utf-8") as archivo:
    archivo.write(rss)

print("RSS actualizado")
print(titulo)
print(fecha)
