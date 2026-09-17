from playwright.sync_api import sync_playwright

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

    browser.close()

urls_alertas = []

for e in enlaces:

    href = e.get("href", "")

    if "/alerta/" in href:

        if href not in urls_alertas:

            urls_alertas.append(href)

with open("alertas_urls.txt", "w", encoding="utf-8") as f:

    for url in urls_alertas:

        f.write(url + "\n")

print(f"ALERTAS ENCONTRADAS: {len(urls_alertas)}")
