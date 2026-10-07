from playwright.sync_api import sync_playwright
import json

base = r"E:\Boom Project\infographic\chinese-almanac-20261110"
jobs = [
    (base + r"\infographic.html", 1080, 1920),
    (base + r"\infographic-1080x1380.html", 1080, 1380),
    (base + r"\infographic-1380x1080.html", 1380, 1080),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    for html, w, h in jobs:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.goto("file:///" + html.replace("\\", "/"))
        pg.wait_for_timeout(1500)
        data = pg.evaluate("""() => {
            const out = {};
            const canvas = document.querySelector('.canvas');
            out.canvas = canvas ? {sh: canvas.scrollHeight, ch: canvas.clientHeight, sw: canvas.scrollWidth, cw: canvas.clientWidth} : null;
            // every card: check vertical overflow
            out.cards = [...document.querySelectorAll('.card, .col')].map(el => {
                const r = el.getBoundingClientRect();
                return {cls: el.className, top: Math.round(r.top), bottom: Math.round(r.bottom),
                        overflow: el.scrollHeight > el.clientHeight + 2};
            });
            // any element whose bottom exceeds canvas height
            out.overflowing = [...document.querySelectorAll('*')].filter(el => {
                const r = el.getBoundingClientRect();
                return r.bottom > window.innerHeight + 1 && r.height > 0;
            }).slice(0,10).map(el => el.className + ' bottom=' + Math.round(el.getBoundingClientRect().bottom));
            // dos li count
            const dos = document.querySelector('.dos');
            out.dos_count = dos ? dos.querySelectorAll('li').length : 0;
            const donts = document.querySelector('.donts');
            out.donts_count = donts ? donts.querySelectorAll('li').length : 0;
            return out;
        }""")
        print("==", html.split("\\")[-1], "viewport", w, "x", h)
        print("  canvas:", data["canvas"])
        print("  dos:", data["dos_count"], "donts:", data["donts_count"])
        print("  overflowing:", data["overflowing"])
        over = [c for c in data["cards"] if c["overflow"]]
        print("  card overflow:", over if over else "none")
        # report max bottom of any card
        if data["cards"]:
            mb = max(c["bottom"] for c in data["cards"])
            print("  max card bottom:", mb, "(canvas h:", h, ")")
        pg.close()
    b.close()
