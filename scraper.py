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

    with open("enlaces.txt", "w", encoding="utf-8") as f:

        for e in enlaces:

            if e["href"] and "alerta" in e["href"]:

                f.write(f"{e['texto']} | {e['href']}\n")
                print(e["texto"])
                print(e["href"])
                print("-" * 50)
