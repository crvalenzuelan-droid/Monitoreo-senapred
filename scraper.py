from playwright.sync_api import sync_playwright
import json

detalles = []

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

            detalles.append({
                "url": url,
                "contenido": texto[:8000]
            })

            print("OK:", url)

            detalle_page.close()

        except Exception as e:

            print("ERROR:", url)
            print(str(e))

    browser.close()

with open(
    "alertas_detalle.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        detalles,
        f,
        ensure_ascii=False,
        indent=2
    )

print("JSON generado")
