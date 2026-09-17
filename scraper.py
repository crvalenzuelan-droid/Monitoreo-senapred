from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.senapred.cl/alerta/se-declara-alerta-temprana-preventiva-para-la-provincia-de-el-loa-y-las-comunas-de-antofagasta-y-taltal-por-nevadas-2026-09-16-18-55-04"
    )

    page.wait_for_timeout(10000)

    html = page.content()

    with open("detalle.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("HTML GUARDADO")

    browser.close()
