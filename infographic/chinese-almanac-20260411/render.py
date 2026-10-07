from playwright.sync_api import sync_playwright

jobs = [
    (r"E:\Boom Project\infographic\chinese-almanac-20260411\infographic.html", 1080, 1920,
     r"E:\Boom Project\infographic\chinese-almanac-20260411\infographic.png"),
    (r"E:\Boom Project\infographic\chinese-almanac-20260411\infographic-1080x1380.html", 1080, 1380,
     r"E:\Boom Project\infographic\chinese-almanac-20260411\infographic-1080x1380.png"),
    (r"E:\Boom Project\infographic\chinese-almanac-20260411\infographic-1380x1080.html", 1380, 1080,
     r"E:\Boom Project\infographic\chinese-almanac-20260411\infographic-1380x1080.png"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    for html, w, h, out in jobs:
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        pg.goto("file:///" + html.replace("\\", "/"))
        pg.wait_for_timeout(2000)  # let webfonts load
        pg.screenshot(path=out, clip={"x": 0, "y": 0, "width": w, "height": h})
        pg.close()
        print("rendered", out)
    b.close()
