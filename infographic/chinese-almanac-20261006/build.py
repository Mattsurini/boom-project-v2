# -*- coding: utf-8 -*-
import re, os, html as h

BASE = r"E:\Boom Project\infographic"
SRC  = os.path.join(BASE, "chinese-almanac-20260411")   # proven 16-dos CSS, fits all 3 sizes
OUT  = os.path.join(BASE, "chinese-almanac-20261006")
os.makedirs(OUT, exist_ok=True)
PAGE = r"C:/Users/Turbo/AppData/Local/hermes/cache/scratch/almanac/almanac_20261006.html"

# ================= page facts (source of truth for date-specific Thai) =================
page = open(PAGE, encoding="utf-8").read()
body = page[page.index("<body"):]
txt = re.sub(r"<(div|p|li|ul|ol|h[1-6]|tr|section|header|footer|article|nav|main|aside)[^>]*>", "|", body)
txt = re.sub(r"<[^>]+>", "", txt)
txt = h.unescape(txt)
P = [p.strip() for p in txt.split("|") if p.strip()]
i0 = next(i for i, p in enumerate(P) if p == "The Chinese Almanac")

lunar_note = P[i0+3]      # จันทรคติจีนเดือน 8 วันที่ 26
year_line  = P[i0+5]      # ปีมะเมีย (ม้้า) ธาตไฟหยาง
month_line = P[i0+6]      # เดือนระกา ธาตไฟหยิน
day_zodiac = P[i0+7]      # วันฉลู่ (วัว) ธาตุน้ำหยิน
dos    = P[i0+9 : i0+25]  # 16
donts  = P[i0+27 : i0+32] # 5
chong_full = P[i0+33]     # วันน้ีชงกบคนเกดป่ีมะแม (ป่ีแพะ) ...
assert len(dos) == 16 and len(donts) == 5, (len(dos), len(donts))

# h2 labels (extracted, never typed)
dont_label = re.search(r'<h2>([^<]+)</h2>\s*<ul class="kw-list ji">', page).group(1)  # ไม่ควรรทำ
sua_label  = re.search(r'<b>([^<]+)</b>ของวันคือทิศ', page).group(1)                  # ทิศซัวะ

# color names: extracted from the page's cshirts markup (never typed);
# swatch color matched by consonant-only normalization (immune to tone-mark drift)
BG = {"แดง": "#d64545", "ชมพู่": "#e88fb0", "ม่วง": "#8e5aa8", "เหลือง": "#e8c547",
      "น้้ำตาล": "#8b5e34", "เขี๊ยว": "#2e7d4f", "ขาว": "#f2f2f2", "ทอง": "#d4a94e",
      "เงิิน": "#b8bcc4", "ดำ": "#1a1a1a", "น้้ำเงิิน": "#9fb4c7"}
def cons(s): return re.sub(r"[^\u0e01-\u0e2e\u0e30\u0e40\u0e41\u0e42\u0e43\u0e44\u0e45\u0e46]", "", s)
CONSK = {cons(k): v for k, v in BG.items()}
def bg(n): return CONSK.get(cons(n), "#999")
cshirts = re.findall(r'<b>([^<]+)</b><span>([^<]+)</span>', page)
assert len(cshirts) == 3, cshirts
seem  = [x.strip() for x in cshirts[0][1].split("/")]
kha   = [x.strip() for x in cshirts[1][1].split("/")]
avoid = [x.strip() for x in cshirts[2][1].split("/")]
assert len(seem) == 3 and len(kha) == 2 and len(avoid) == 2, (seem, kha, avoid)
assert all(bg(n) != "#999" for n in seem + kha + avoid), [n for n in seem+kha+avoid if bg(n) == "#999"]

# ================= day ganzhi (computed, verified) =================
# 2026-10-06 = 癸丑 (Gui-Chou): stem 癸 = water-yin (day element), branch 丑 = earth-yin (Ox)
DAY_GZ, YEAR_GZ, MONTH_GZ = "癸丑", "丙午", "丁酉"
DAY_BR, DAY_STEM = DAY_GZ[1], DAY_GZ[0]   # 丑, 癸

# element words extracted from siblings (never typed)
def chipword(d, el):
    s = open(os.path.join(BASE, f"chinese-almanac-{d}", "infographic.html"), encoding="utf-8").read()
    m = re.search(r'<div class="chip '+el+r'">([^<]+)</div>', s)
    return m.group(1).strip() if m else None
W_EARTH = chipword("20261110", "earth")   # ดิน
W_WATER = chipword("20260411", "water")   # น้้ำ
W_METAL = chipword("20261004", "metal")   # โลหะ
# month card (same 丁酉 as 20261004) + leiyang word (extracted, never typed)
_s1004 = open(os.path.join(BASE, "chinese-almanac-20261004", "infographic.html"), encoding="utf-8").read()
MONTH_TH = re.search(r'<div class="cjk big">丁酉</div><div class="th">([^<]+)</div>', _s1004).group(1)
_s411 = open(os.path.join(BASE, "chinese-almanac-20260411", "infographic.html"), encoding="utf-8").read()
LEIYANG = re.search(r'→ ([^<]+)</div>', _s411).group(1)

# yin marker 'หยิน' from page day element (4 codepoints) — never typed
stem_elem = day_zodiac.split(")")[-1].replace("ธาต", "").strip()   # น้้ำหยิน
yin = stem_elem[-4:]
assert len(yin) == 4, yin
branch_elem = W_EARTH + yin   # ดินหยิน (branch 丑 = earth-yin)
day_elem    = W_WATER + yin   # น้้ำหยิน (stem 癸 = water-yin) = day element

# ================= date-specific Thai (tone-mark-safe extraction) =================
WAN = "\u0e27\u0e31\u0e19"  # wan (3 codepoints, no tone marks) — never typed
zod_th     = day_zodiac.split(WAN)[-1].split("(")[0].strip()   # ฉลู่
chong_val  = re.search(r"ป(\S+) \(ป", chong_full).group(1).lstrip("\u0e35")  # มะแม
east       = re.search(r"คือ(ทิศ\S+)", chong_full).group(1)        # ทิศตะวันออก
lun_m, lun_d = (int(x) for x in re.findall(r"\d+", lunar_note))
assert len(re.findall(r"\d+", lunar_note)) == 2, lunar_note
title = P[i0+2].split(WAN)[-1]                              # อังคารท่ี 6 ตลลลคม 2569

# ================= template labels (from proven 20260411) =================
def sw(n): return f'<div class="sw"><div class="dot" style="background:{bg(n)}"></div><div class="nm">{n}</div></div>'
seem_sw  = "".join(sw(n) for n in seem)
kha_sw   = "".join(sw(n) for n in kha)
avoid_sw = "".join(sw(n) for n in avoid)

def extract_labels(html):
    def g(pat):
        m = re.search(pat, html, flags=re.S)
        return m.group(1).strip() if m else None
    L = {}
    L["kicker"]       = g(r'class="kicker">([^<]+)<')
    L["lunar_label"]  = g(r'class="card lunar"><div class="label">([^<]+)<')
    m = re.search(r'<div class="card"><div class="label">([^<]+)</div><div class="cjk big">丙午', html)
    L["year_label"]   = m.group(1) if m else "ป่ี"
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
    L["seal_wan"] = g(r'class="small">([^<]+)</div>')[:3]   # วาน
    # hero fixed tokens 'ก่ิง' + '天干' (identical across ganzhi)
    m = re.search(r'<div class="elem">([^<]+)<br>', html)
    seg = m.group(1)
    L["hero_tok0"] = seg.split()[0]                          # ก่ิง
    L["hero_stem_lbl"] = seg.split("·")[-1].strip().split()[0]  # 天干
    L["ritual_fs"] = re.search(r'font-size:(\d+)px;margin-top:2px', html).group(1)
    # colors/logic labels: 20260411 is a wood day (乙 ไม้ Wood); my day is water (癸 น้้ำ)
    L["colors_label"] = L["colors_label"].replace("ไม้", W_WATER).replace("Wood", "Water").replace("乙", DAY_STEM)
    L["logic_label"]  = L["logic_label"].replace("ไม้", W_WATER).replace("乙", DAY_STEM)
    return L

def build_body(lbl, layout):
    dos_lis  = "".join(f"<li>{d}</li>" for d in dos)
    dont_lis = "".join(f"<li>{d}</li>" for d in donts)
    seal_small = lbl["seal_wan"] + day_elem                  # วาน + น้้ำหยิน

    header = (f'<div class="header">\n'
              f'<div><div class="kicker">{lbl["kicker"]}</div>'
              f'<div class="title">{title}<span class="sub">2026-10-06 · {lunar_note}</span></div></div>\n'
              f'<div class="seal"><div class="big cjk">{DAY_GZ}</div><div class="small">{seal_small}</div></div>\n'
              f'</div>')
    hero = (f'<div class="row">\n'
            f'<div class="card hero"><div class="ganzhi cjk">{DAY_GZ}</div>'
            f'<div class="meta"><div class="zod">{WAN}{zod_th} ({DAY_BR})</div>'
            f'<div class="elem">{lbl["hero_tok0"]} {DAY_BR} {branch_elem} · {lbl["hero_stem_lbl"]} {DAY_STEM}<br><b>{day_elem}</b></div></div></div>\n'
            f'<div class="card lunar"><div class="label">{lbl["lunar_label"]}</div>'
            f'<div class="num">{lun_m} <span>/ {lun_d}</span></div><div class="note">{lunar_note}</div></div>\n'
            f'</div>')
    trio = (f'<div class="row trio">\n'
            f'<div class="card"><div class="label">{lbl["year_label"]}</div>'
            f'<div class="cjk big">{YEAR_GZ}</div><div class="th">{lbl["year_th"]}</div><div class="el">{lbl["year_el"]}</div></div>\n'
            f'<div class="card"><div class="label">{lbl["month_label"]}</div>'
            f'<div class="cjk big">{MONTH_GZ}</div><div class="th">{MONTH_TH}</div><div class="el">{month_line.split(" ")[-1]}</div></div>\n'
            f'<div class="card"><div class="label">{lbl["ritual_label"]}</div>'
            f'<div class="th" style="font-size:{lbl["ritual_fs"]};margin-top:2px;">{lbl["ritual_th"]}</div>'
            f'<div class="el">{lbl["ritual_el"]}</div><div class="tag gray">{lbl["ritual_tag"]}</div></div>\n'
            f'</div>')

    # chong card with the 5 donts folded in (uses vertical slack next to tall dos)
    chong_card = (f'<div class="card chong"><div class="label">{lbl["chong_label"]}</div>'
                  f'<div class="val">{chong_val}</div><div class="dir">{sua_label}: <b>{east}</b></div>'
                  f'<div class="donts-in"><div class="dlabel">{dont_label}</div><ul>{dont_lis}</ul></div></div>')
    dos_card = (f'<div class="card dos"><div class="label">{lbl["dos_label"]}</div><ul>{dos_lis}</ul></div>')
    colors = (f'<div class="card colors"><div class="label">{lbl["colors_label"]}</div><div class="groups">\n'
              f'<div class="cg"><div class="glabel">{lbl["g_seem"]}</div><div class="swatches">{seem_sw}</div></div>\n'
              f'<div class="cg"><div class="glabel">{lbl["g_kha"]}</div><div class="swatches">{kha_sw}</div></div>\n'
              f'<div class="cg"><div class="glabel">{lbl["g_avoid"]}</div><div class="swatches">{avoid_sw}</div></div>\n'
              f'</div></div>')
    # water-day logic: metal (mother) / water (friend) / earth (enemy) -> water (on)
    logic = (f'<div class="card logic"><div class="label">{lbl["logic_label"]}</div><div class="logicrows">\n'
             f'<div class="lrow"><div class="chip metal">{W_METAL}</div><div class="rel">{lbl["r_seem"]}</div><div class="chip water on">{W_WATER}</div><div class="cex">{" / ".join(seem)}</div></div>\n'
             f'<div class="lrow"><div class="chip water">{W_WATER}</div><div class="rel">{lbl["r_kha"]}</div><div class="chip water on">{W_WATER}</div><div class="cex">{" / ".join(kha)}</div></div>\n'
             f'<div class="lrow"><div class="chip earth">{W_EARTH}</div><div class="rel">{lbl["r_avoid"]}</div><div class="chip water on">{W_WATER}</div><div class="cex">{" / ".join(avoid)} → {LEIYANG}</div></div>\n'
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

# water.on chip + donts-in css (folded into chong card)
def dont_css(layout):
    if layout == "landscape":
        return (
            '\n  .chip.water.on { background:#3a5a80; box-shadow:0 0 0 3px rgba(212,169,78,.5); }\n'
            '  .donts-in { margin-top:14px; border-top:1px solid rgba(255,255,255,.18); padding-top:10px; }\n'
            '  .donts-in .dlabel { font-size:13px; color:#c98f8f; letter-spacing:2px; margin-bottom:6px; }\n'
            '  .donts-in ul { list-style:none; display:flex; flex-direction:column; gap:6px; }\n'
            '  .donts-in li { font-size:14px; color:#f5efe0; font-weight:600; display:flex; align-items:center; gap:8px; }\n'
            '  .donts-in li::before { content:"\\2717 "; color:#d64545; font-size:14px; font-weight:700; }\n')
    return (
        '\n  .chip.water.on { background:#3a5a80; box-shadow:0 0 0 3px rgba(212,169,78,.5); }\n'
        '  .donts-in { margin-top:16px; border-top:1px solid rgba(255,255,255,.18); padding-top:12px; }\n'
        '  .donts-in .dlabel { font-size:18px; color:#c98f8f; letter-spacing:2px; margin-bottom:8px; }\n'
        '  .donts-in ul { list-style:none; display:grid; grid-template-columns:1fr 1fr; gap:6px 14px; }\n'
        '  .donts-in li { font-size:16px; color:#f5efe0; font-weight:600; display:flex; align-items:center; gap:6px; line-height:1.3; }\n'
        '  .donts-in li::before { content:"\\2717 "; color:#d64545; font-size:16px; font-weight:700; }\n')

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
    head = re.sub(r'(\.dos li \{ font-size:)\d+(px)', rf'\g<1>{dos_fs}\2', head)
    head = re.sub(r'(\.dos li::before \{ content:"[^"]*"; color:#2e7d4f; font-size:)\d+(px)', rf'\g<1>{dos_fs}\2', head)
    head = head.replace("</style>", dont_css(layout) + "</style>")
    out = head + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    dest = os.path.join(OUT, fname)
    open(dest, "w", encoding="utf-8").write(out)
    print("wrote", dest, len(out), "bytes")

# ================= facts.json (schema matches 20261110) =================
import json
# source lines carry doubled prefixes: ปีปี / เดือนเดือน / วันวัน
PI, DEUN = "\u0e1b\u0e35", "\u0e40\u0e14\u0e37\u0e2d\u0e19"
year_th     = year_line.split(PI)[-1].split("(")[0].strip()   # มะเมีย
year_animal = re.search(r"\(([^)]+)\)", year_line).group(1)   # ม้า
year_elem   = year_line.split(" ")[-1]                         # ธาตไฟหยาง
month_branch = month_line.split(DEUN)[-1].split(" ")[0]        # ระกา
month_elem  = month_line.split(" ")[-1]                        # ธาตไฟหยิน
animal      = day_zodiac.split("(")[1].split(")")[0]           # วัว
day_elem_full = day_zodiac.split(") ")[1].split(" ")[0]        # ธาตุน้ำหยิน
facts = {
    "lunar_note": lunar_note,
    "year_th": year_th,
    "year_animal": year_animal,
    "year_elem": year_elem,
    "month_branch_th": month_branch,
    "month_elem": month_elem,
    "zod_th": WAN + zod_th,
    "animal": animal,
    "day_elem": day_elem_full,
    "dos": dos,
    "donts": donts,
    "chong_val": chong_val,
    "south": east,
    "seem": " / ".join(seem),
    "kha": " / ".join(kha),
    "avoid": " / ".join(avoid),
}
open(os.path.join(OUT, "facts.json"), "w", encoding="utf-8").write(
    json.dumps(facts, ensure_ascii=False, indent=1))
print("wrote facts.json")
print("DONE")
