from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto("https://www.senapred.cl/alertas")

    page.wait_for_timeout(10000)

    texto = page.locator("body").inner_text()

    lineas = [x.strip() for x in texto.split("\n") if x.strip()]

    for i, linea in enumerate(lineas):

        if linea.startswith("Monitoreo") or linea.startswith("Se declara"):

            print("ALERTA:")
            print(linea)

            if i + 1 < len(lineas):
                print("FECHA:")
                print(lineas[i + 1])

            break

    browser.close()
