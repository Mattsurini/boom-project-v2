# -*- coding: utf-8 -*-
import re, os

BASE = r"E:\Boom Project\infographic"
SRC  = os.path.join(BASE, "chinese-almanac-20260411")   # proven 16-dos CSS, fits all 3 sizes
OUT  = os.path.join(BASE, "chinese-almanac-20261110")
os.makedirs(OUT, exist_ok=True)

# ---- page facts (source of truth for date-specific Thai) ----
page = open(r"C:/Users/Turbo/AppData/Local/Temp/almanac_20261110.txt", encoding="utf-8").read()
P = [p.strip() for p in page.split("|")]
i0 = next(i for i, p in enumerate(P) if p == "The Chinese Almanac")

lunar_note  = P[i0+6]     # เดือน 10 วันที่ 2
year_line   = P[i0+10]    # ปีมะเมีย (ม้้่า) ธาตไฟหยาง
month_line  = P[i0+12]    # เดือนกุน ธาตุดินหยิน
day_zodiac  = P[i0+14]    # วัญชวด (หนู) ธาตุดินหยาง
dos    = P[i0+16 : i0+32] # 16
donts  = P[i0+34 : i0+36] # 2
chong_full = P[i0+38]     # ปีมะเมี่ย (ปี่ม้้า)
dir_line   = P[i0+41]     # ของวัญคิือทิศใต้ ...
seem = P[i0+45]           # แดง / ชมพู่ / ม่วง
kha  = P[i0+48]           # เหลือง / น้้้้ำตาล
avoid= P[i0+51]           # เขี๊่ยว
dont_label = P[i0+33]     # ไม่ควรถือ
assert len(dos) == 16 and len(donts) == 2

day_elem   = day_zodiac.split(")")[-1].strip()             # ธาตุดินหยาง
elem_short = day_elem.replace("ธาตุ", "")                  # ดินหยาง
zod_th     = day_zodiac.split("(")[0].strip()              # วัญชวด
chong_val  = chong_full.split("(")[0].lstrip("ปี่").strip() # มะเมี่ย
south      = re.search(r"ทิศ(\S+)", dir_line).group(0)     # ทิศใต้
sua_label  = P[i0+40]                                      # ทิศซัวะ
month_th   = month_line.split(" ")[0].lstrip("เดือน")      # กุน
month_el   = month_line.split(" ", 1)[1]                   # ธาตุดินหยิน
jantr      = P[i0+5].rstrip("จีน")                         # จันทรคติ
t = P[i0+1].split(" ", 1)[1]
t = t.lstrip("วัน")
t = re.sub(r"^(.{1,6})ที้", r"\1", t)
title = t

# CJK (typed reliably)
DAY_GZ, YEAR_GZ, MONTH_GZ = "戊子", "丙午", "辛丑"
DAY_BR = DAY_GZ[1]  # 子
Ox = "วัว"          # Thai animal for 丑 (not on page; standard)

# yang marker 'หยาง' from page (4 codepoints) — never typed
yang = P[i0+10][-4:]

# color swatch backgrounds
BG = {"แดง": "#d64545", "ชมพู่": "#e88fb0", "ม่วง": "#8e5aa8", "เหลือง": "#e8c547",
      "น้้้้ำตาล": "#8b5e34", "เขี๊่ยว": "#2e7d4f", "ขาว": "#f2f2f2", "ทอง": "#d4a94e",
      "เงิิน": "#b8bcc4", "ด้าม": "#1a1a1a", "น้้้้ำเงิิน": "#9fb4c7"}
def sk(s): return re.sub(r"[^\u0e01-\u0e3a]", "", s)
SK = {sk(k): v for k, v in BG.items()}
def bg(n): return SK.get(sk(n), "#999")
def parsec(s): return [x.strip() for x in s.split("/")]
def sw(n): return f'<div class="sw"><div class="dot" style="background:{bg(n)}"></div><div class="nm">{n}</div></div>'
seem_sw  = "".join(sw(n) for n in parsec(seem))
kha_sw   = "".join(sw(n) for n in parsec(kha))
avoid_sw = "".join(sw(n) for n in parsec(avoid))

def extract_labels(html):
    def g(pat):
        m = re.search(pat, html, flags=re.S)
        return m.group(1).strip() if m else None
    L = {}
    L["kicker"]       = g(r'class="kicker">([^<]+)<')
    L["lunar_label"]  = g(r'class="card lunar"><div class="label">([^<]+)<')
    m = re.search(r'<div class="card"><div class="label">([^<]+)</div><div class="cjk big">丙午', html)
    L["year_label"]   = m.group(1) if m else "ปี่"
    m = re.search(r'<div class="card"><div class="label">([^<]+)</div><div class="cjk big">壬辰', html)
    L["month_label"]  = m.group(1) if m else "เดือน"
    L["year_th"]      = g(r'<div class="cjk big">丙午</div><div class="th">([^<]+)<')
    L["year_el"]      = g(r'<div class="cjk big">丙午</div><div class="th">[^<]+</div><div class="el">([^<]+)<')
    L["ritual_label"] = g(r'<div class="card"><div class="label">([^<]+)</div><div class="th" style="font-size:')
    L["ritual_th"]    = g(r'<div class="th" style="font-size:[^"]*;">([^<]+)</div><div class="el">黑道')
    L["ritual_el"]    = g(r'<div class="el">(黑道[^<]+)</div>')
    L["ritual_tag"]   = g(r'<div class="tag gray">([^<]+)</div>')
    L["dos_label"]    = g(r'class="card dos"><div class="label">([^<]+)<')
    L["chong_label"]  = g(r'class="card chong"><div class="label">([^<]+)<')
    L["colors_label"] = g(r'class="card colors"><div class="label">([^<]+)</div>')
    gl = re.findall(r'<div class="glabel">([^<]+)<span class="en">([^<]+)</span></div>', html)
    L["g_seem"], L["en_seem"]   = gl[0]
    L["g_kha"],  L["en_kha"]    = gl[1]
    L["g_avoid"],L["en_avoid"]  = gl[2]
    L["logic_label"] = g(r'class="card logic"><div class="label">([^<]+)</div>')
    rels = re.findall(r'<div class="rel">([^<]+)</div>', html)
    L["r_seem"], L["r_kha"], L["r_avoid"] = rels[0], rels[1], rels[2]
    L["chip_fire"]  = g(r'<div class="chip fire">([^<]+)</div>')
    L["chip_earth"] = g(r'<div class="chip earth">([^<]+)</div>')
    L["chip_wood"]  = g(r'<div class="chip wood">([^<]+)</div>')
    # 20260411 is a wood day (no fire/earth chips) -> source from 20261004 (metal day)
    s1004 = open(os.path.join(BASE, "chinese-almanac-20261004", "infographic.html"), encoding="utf-8").read()
    if not L["chip_fire"]:
        m = re.search(r'<div class="chip fire">([^<]+)</div>', s1004)
        L["chip_fire"] = m.group(1) if m else "ไฟ"
    if not L["chip_earth"]:
        m = re.search(r'<div class="chip earth">([^<]+)</div>', s1004)
        L["chip_earth"] = m.group(1) if m else "ดิน"
    # colors/logic labels: 20260411 has wood-day labels (乙 ไม้ Wood);
    # my day is earth (戊 ดิน) -> rebuild from 20261004 (metal-day) template, swap metal->earth
    mc = re.search(r'class="card colors"><div class="label">([^<]+)</div>', s1004)
    L["colors_label"] = mc.group(1).replace("โลหะ", L["chip_earth"]).replace("Metal", "Earth").replace("辛", "戊")
    ml = re.search(r'class="card logic"><div class="label">([^<]+)</div>', s1004)
    L["logic_label"]  = ml.group(1).replace("โลหะ", L["chip_earth"]).replace("辛", "戊")
    cexs = re.findall(r'<div class="cex">([^<]+)</div>', html)
    L["leiyang"]    = cexs[-1].split("→")[-1].strip() if cexs else "เลี่่่ยง"
    # hero: fixed token + water word from source 20261004 (day 亥 = water yin)
    i = html.index('class="elem">')
    seg = html[i + len('class="elem">'): html.index('<br>', i)]
    L["hero_tok0"] = seg.split()[0]
    s1004 = open(os.path.join(BASE, "chinese-almanac-20261004", "infographic.html"), encoding="utf-8").read()
    i2 = s1004.index('class="elem">')
    seg2 = s1004[i2 + len('class="elem">'): s1004.index('<br>', i2)]
    L["water_word"] = seg2.split()[2][:3]
    L["seal_small_src"] = g(r'class="small">([^<]+)</div>')
    L["ritual_fs"] = re.search(r'font-size:(\d+)px;margin-top:2px', html).group(1)
    return L

def build_body(lbl, layout):
    dos_lis  = "".join(f"<li>{d}</li>" for d in dos)
    dont_lis = "".join(f"<li>{d}</li>" for d in donts)
    branch_elem = lbl["water_word"] + yang                 # 'น้้้้ำหยาง'
    seal_small  = lbl["seal_small_src"][:3] + elem_short   # 'วัญ' + 'ดินหยาง'

    header = (f'<div class="header">\n'
              f'<div><div class="kicker">{lbl["kicker"]}</div>'
              f'<div class="title">{title}<span class="sub">2026-11-10 · {jantr} {lunar_note}</span></div></div>\n'
              f'<div class="seal"><div class="big cjk">{DAY_GZ}</div><div class="small">{seal_small}</div></div>\n'
              f'</div>')
    hero = (f'<div class="row">\n'
            f'<div class="card hero"><div class="ganzhi cjk">{DAY_GZ}</div>'
            f'<div class="meta"><div class="zod">{zod_th} ({DAY_BR})</div>'
            f'<div class="elem">{lbl["hero_tok0"]} {DAY_BR} {branch_elem} · 天干 戊<br><b>{elem_short}</b></div></div></div>\n'
            f'<div class="card lunar"><div class="label">{lbl["lunar_label"]}</div>'
            f'<div class="num">10 <span>/ 2</span></div><div class="note">{lunar_note}</div></div>\n'
            f'</div>')
    trio = (f'<div class="row trio">\n'
            f'<div class="card"><div class="label">{lbl["year_label"]}</div>'
            f'<div class="cjk big">{YEAR_GZ}</div><div class="th">{lbl["year_th"]}</div><div class="el">{lbl["year_el"]}</div></div>\n'
            f'<div class="card"><div class="label">{lbl["month_label"]}</div>'
            f'<div class="cjk big">{MONTH_GZ}</div><div class="th">{month_th} ({Ox})</div><div class="el">{month_el}</div></div>\n'
            f'<div class="card"><div class="label">{lbl["ritual_label"]}</div>'
            f'<div class="th" style="font-size:{lbl["ritual_fs"]};margin-top:2px;">{lbl["ritual_th"]}</div>'
            f'<div class="el">{lbl["ritual_el"]}</div><div class="tag gray">{lbl["ritual_tag"]}</div></div>\n'
            f'</div>')

    # chong card with the 2 donts folded in (uses vertical slack next to tall dos)
    chong_card = (f'<div class="card chong"><div class="label">{lbl["chong_label"]}</div>'
                  f'<div class="val">{chong_val}</div><div class="dir">{sua_label}: <b>{south}</b></div>'
                  f'<div class="donts-in"><div class="dlabel">{dont_label}</div><ul>{dont_lis}</ul></div></div>')
    dos_card = (f'<div class="card dos"><div class="label">{lbl["dos_label"]}</div><ul>{dos_lis}</ul></div>')
    colors = (f'<div class="card colors"><div class="label">{lbl["colors_label"]}</div><div class="groups">\n'
              f'<div class="cg"><div class="glabel">{lbl["g_seem"]}<span class="en">{lbl["en_seem"]}</span></div><div class="swatches">{seem_sw}</div></div>\n'
              f'<div class="cg"><div class="glabel">{lbl["g_kha"]}<span class="en">{lbl["en_kha"]}</span></div><div class="swatches">{kha_sw}</div></div>\n'
              f'<div class="cg"><div class="glabel">{lbl["g_avoid"]}<span class="en">{lbl["en_avoid"]}</span></div><div class="swatches">{avoid_sw}</div></div>\n'
              f'</div></div>')
    logic = (f'<div class="card logic"><div class="label">{lbl["logic_label"]}</div><div class="logicrows">\n'
             f'<div class="lrow"><div class="chip fire">{lbl["chip_fire"]}</div><div class="rel">{lbl["r_seem"]}</div><div class="chip earth on">{lbl["chip_earth"]}</div><div class="cex">{seem}</div></div>\n'
             f'<div class="lrow"><div class="chip earth">{lbl["chip_earth"]}</div><div class="rel">{lbl["r_kha"]}</div><div class="chip earth on">{lbl["chip_earth"]}</div><div class="cex">{kha}</div></div>\n'
             f'<div class="lrow"><div class="chip wood">{lbl["chip_wood"]}</div><div class="rel">{lbl["r_avoid"]}</div><div class="chip earth on">{lbl["chip_earth"]}</div><div class="cex">{avoid} → {lbl["leiyang"]}</div></div>\n'
             f'</div></div>')

    if layout == "landscape":
        main_left = f'{header}\n{hero}\n{trio}'
        body = (f'<div class="canvas">\n'
                f'<div class="col left">\n{main_left}\n</div>\n'
                f'<div class="col right">\n'
                f'<div class="row">{dos_card}{chong_card}</div>\n'
                f'{colors}\n{logic}\n'
                f'</div>\n</div>')
        return body

    body = (f'<div class="canvas">\n{header}\n{hero}\n{trio}\n'
            f'<div class="row">{dos_card}{chong_card}</div>\n'
            f'{colors}\n{logic}\n</div>')
    return body

# donts-in css (folded into chong card) + earth.on chip
def dont_css(layout):
    if layout == "landscape":
        return (
            '\n  .chip.earth.on { background:#a9713f; }\n'
            '  .donts-in { margin-top:14px; border-top:1px solid rgba(255,255,255,.18); padding-top:10px; }\n'
            '  .donts-in .dlabel { font-size:13px; color:#c98f8f; letter-spacing:2px; margin-bottom:6px; }\n'
            '  .donts-in ul { list-style:none; display:flex; flex-direction:column; gap:6px; }\n'
            '  .donts-in li { font-size:14px; color:#f5efe0; font-weight:600; display:flex; align-items:center; gap:8px; }\n'
            '  .donts-in li::before { content:"\\2717 "; color:#d64545; font-size:14px; font-weight:700; }\n')
    return (
        '\n  .chip.earth.on { background:#a9713f; }\n'
        '  .donts-in { margin-top:18px; border-top:1px solid rgba(255,255,255,.18); padding-top:14px; }\n'
        '  .donts-in .dlabel { font-size:20px; color:#c98f8f; letter-spacing:2px; margin-bottom:10px; }\n'
        '  .donts-in ul { list-style:none; display:flex; flex-direction:column; gap:10px; }\n'
        '  .donts-in li { font-size:22px; color:#f5efe0; font-weight:600; display:flex; align-items:center; gap:10px; }\n'
        '  .donts-in li::before { content:"\\2717 "; color:#d64545; font-size:22px; font-weight:700; }\n')

SIZES = [
    ("infographic.html",            "portrait",  19),
    ("infographic-1080x1380.html",  "square",    19),
    ("infographic-1380x1080.html",  "landscape", 16),
]

for fname, layout, dos_fs in SIZES:
    src = os.path.join(SRC, fname)
    html = open(src, encoding="utf-8").read()
    lbl = extract_labels(html)
    body = build_body(lbl, layout)
    head = html[:html.index("</style>") + len("</style>")]
    # shrink dos font so 16 (longer) items fit one line
    head = re.sub(r'(\.dos li \{ font-size:)\d+(px)', rf'\g<1>{dos_fs}\2', head)
    head = re.sub(r'(\.dos li::before \{ content:"[^"]*"; color:#2e7d4f; font-size:)\d+(px)', rf'\g<1>{dos_fs}\2', head)
    head = head.replace("</style>", dont_css(layout) + "</style>")
    out = head + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    dest = os.path.join(OUT, fname)
    open(dest, "w", encoding="utf-8").write(out)
    print("wrote", dest, len(out), "bytes")
print("DONE")
