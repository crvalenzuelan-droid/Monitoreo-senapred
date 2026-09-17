from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto("https://www.senapred.cl/alertas")

    page.wait_for_timeout(10000)

    texto = page.locator("body").inner_text()

    with open(
        "portada_senapred.txt",
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(texto)

    browser.close()

print("PORTADA GENERADA")
