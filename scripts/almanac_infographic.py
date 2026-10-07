"""Render a Chinese almanac day as an HTML infographic + PNG.

Usage (from E:\\Boom Project):
  .venv/Scripts/python scripts/almanac_infographic.py 2026-10-05
  .venv/Scripts/python scripts/almanac_infographic.py 2026-10-05 --size 1380x1080
  .venv/Scripts/python scripts/almanac_infographic.py 2026-10-05 --size all

Data sources:
  - Facts (ฤกษ์, ควรทำ, วันชง, ทิศซัวะ, สีมงคล): Output/Sources/Chinese-Astrology/chinese_calendar_oct2026.json cache;
    if the date is missing, scrapes tarot.loveiseveryday.com/chinese-calendar/<date>.
  - Gan-Zhi + lunar date: scripts/chinese_almanac_accurate.py (analyze()).

Templates: infographic/templates/chinese-almanac/template-1080x1920.html
           infographic/templates/chinese-almanac/template-1080x1380.html
           infographic/templates/chinese-almanac/template-1380x1080.html
Output:    infographic/chinese-almanac-YYYYMMDD/infographic.html + infographic.png
           (infographic-<size>.png when --size all)
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(r'E:\Boom Project')
TPL_DIR = ROOT / 'infographic' / 'templates' / 'chinese-almanac'
CACHE = ROOT / 'Output' / 'Sources' / 'Chinese-Astrology' / 'chinese_calendar_oct2026.json'

sys.path.insert(0, str(ROOT / 'scripts'))
from chinese_almanac_accurate import (analyze, STEMS, BRANCHES, STEM_ELEMENT,
                                      BRANCH_ELEMENT, BRANCH_DATA)

SIZE_TPL = {
    '1080x1920': 'template-1080x1920.html',
    '1080x1380': 'template-1080x1380.html',
    '1380x1080': 'template-1380x1080.html',
}

ELEM_THAI = {'wood': 'ไม้', 'fire': 'ไฟ', 'earth': 'ดิน', 'metal': 'โลหะ', 'water': 'น้ำ'}
ELEM_SEAL = {'wood': 'ไม้', 'fire': 'ไฟ', 'earth': 'ดิน', 'metal': 'ทอง', 'water': 'น้ำ'}
ELEM_EN = {'wood': 'Wood', 'fire': 'Fire', 'earth': 'Earth', 'metal': 'Metal', 'water': 'Water'}
GEN = {'wood': 'water', 'fire': 'wood', 'earth': 'fire', 'metal': 'earth', 'water': 'metal'}
CTRL = {'wood': 'metal', 'fire': 'water', 'earth': 'wood', 'metal': 'fire', 'water': 'earth'}
WUXING_COLORS = {
    'wood': ['เขียว'],
    'fire': ['แดง', 'ชมพู', 'ม่วง'],
    'earth': ['เหลือง', 'น้ำตาล'],
    'metal': ['ขาว', 'ทอง', 'เงิน'],
    'water': ['ดำ', 'น้ำเงิน'],
}
COLOR_HEX = {
    'เขียว': '#4a8f5c', 'แดง': '#d64545', 'ชมพู': '#e88fb0', 'ม่วง': '#8e5aa8',
    'เหลือง': '#e8c547', 'น้ำตาล': '#8b5e34', 'ขาว': '#f2f2f2', 'ทอง': '#d4a94e',
    'เงิน': '#b8bcc4', 'ดำ': '#2b2b33', 'น้ำเงิน': '#8a9bb5',
}

def yinyang(idx):
    return 'หยาง' if idx % 2 == 0 else 'หยิน'

def load_facts(date_str):
    if CACHE.exists():
        data = json.load(open(CACHE, encoding='utf-8'))
        for item in data:
            if item['date'] == date_str:
                return item, 'cache'
    from scrape_chinese_lookup import scrape_date
    item = scrape_date(date_str)
    return item, 'scrape'


def fkey(facts, prefix):
    """Resolve a Thai facts key by prefix (tone marks in source data vary)."""
    for k in facts:
        if k.startswith(prefix):
            return k
    raise KeyError(prefix)

def month_ganzhi(year, lunar_month):
    """五虎遁: month pillar from year stem + lunar month number (1=寅)."""
    year_stem_idx = (year - 1984) % 10
    start = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}[year_stem_idx]
    m = lunar_month  # 1..12, 1 = 寅
    branch_idx = (2 + m - 1) % 12
    stem_idx = (start + m - 1) % 10
    return STEMS[stem_idx] + BRANCHES[branch_idx]

def build_values(date_str, item, acc):
    f = item['facts']
    stem = acc['day_stem']
    branch = acc['day_branch']
    el = acc['day_element']
    stem_idx = STEMS.index(stem)
    branch_idx = BRANCHES.index(branch)
    branch_el = BRANCH_ELEMENT[branch]

    thai_date = f[fkey(f, 'วันท')].replace('วัน', '', 1).replace('ที่', ' ')
    thai_date = re.sub(r'\s+', ' ', thai_date).strip()
    lunar_th = re.sub(r'\s+', ' ', f[fkey(f, 'จันท')].replace('ที่', ' ')).strip()

    # ฤกษ์
    rik = f['ฤกษ์ของวัน']
    if rik.startswith('วันดี'):
        fortune, note, tag = 'วันดี', '黄道 · หวงเต้า', 'เหมาะเรื่่องสำคัญ'
    else:
        fortune, note, tag = 'วันธรรมดา', '黑道 · เฮยเต้า', 'เลี่่ยงเรื่่องใหญ่'

    # year / month pillars
    mz_gz = month_ganzhi(int(date_str[:4]), acc['lunar']['month'])

    def pillar(line, prefix):
        part = line[len(prefix):] if line.startswith(prefix) else line
        part = part.strip()
        if '(' in part:
            head, rest = part.split('(', 1)
            zodiac = head.strip() + ' (' + rest.split(')')[0] + ')'
            element = rest.split(')', 1)[1].strip()
            return zodiac, element, True
        tokens = part.split()
        if len(tokens) >= 2 and tokens[-1].startswith('ธา'):
            return ' '.join(tokens[:-1]), tokens[-1], False
        return part, '', False

    year_zodiac, year_element, _ = pillar(f[fkey(f, 'ปี')], 'ปี')
    month_zodiac, month_element, had_paren = pillar(f[fkey(f, 'เดือน')], 'เดือน')
    if not had_paren and not month_element:
        animal = BRANCH_DATA.get(mz_gz[1], {}).get('animal')
        if animal:
            month_zodiac += f' ({animal})'

    dos = item.get('ควรทำ', [])[:4]
    dos_items = ''.join(f'<li>{x}</li>' for x in dos)

    def swatches(names):
        return ''.join(
            f'<div class="sw"><div class="dot" style="background:{COLOR_HEX.get(n, "#cccccc")}"></div><div class="nm">{n}</div></div>'
            for n in names)

    colors = item.get('สีมงคล', {})
    gen_el, ctrl_el = GEN[el], CTRL[el]

    def lrow(chip_el, rel, cex):
        return (f'<div class="lrow"><div class="chip {chip_el}">{ELEM_THAI[chip_el]}</div>'
                f'<div class="rel">{rel}</div><div class="chip {el} on">{ELEM_THAI[el]}</div>'
                f'<div class="cex">{cex}</div></div>')

    logic_rows = '\n'.join([
        lrow(gen_el, 'เสริม (มารดา)', ' / '.join(WUXING_COLORS[gen_el])),
        lrow(el, 'เข้ากกัน (สหาย)', ' / '.join(WUXING_COLORS[el])),
        lrow(ctrl_el, 'กด (ศัตรู)', ' / '.join(WUXING_COLORS[ctrl_el]) + ' → เลี่่ยง'),
    ])

    return {
        'THAI_DATE': thai_date,
        'GREG_LUNAR_LINE': f'{date_str} · จันทรคตจิณ {lunar_th}',
        'DAY_GANZHI': acc['day_ganzhi'],
        'SEAL_ELEMENT_THAI': f'วัน{ELEM_SEAL[el]}{yinyang(stem_idx)}',
        'ZODIAC_THAI': f"{BRANCH_DATA[branch]['th']} ({BRANCH_DATA[branch]['animal']})",
        'BRANCH_LINE': f'กิง {branch} {ELEM_THAI[branch_el]}{yinyang(branch_idx)} · 天干 {stem}',
        'DAY_ELEMENT': f'{ELEM_THAI[el]}{yinyang(stem_idx)}',
        'LUNAR_MONTH': str(acc['lunar']['month']),
        'LUNAR_DAY': str(acc['lunar']['day']),
        'LUNAR_NOTE': lunar_th,
        'YEAR_GANZHI': acc['year_ganzhi'],
        'YEAR_ZODIAC': year_zodiac,
        'YEAR_ELEMENT': year_element,
        'MONTH_GANZHI': mz_gz,
        'MONTH_ZODIAC': month_zodiac,
        'MONTH_ELEMENT': month_element,
        'DAY_FORTUNE': fortune,
        'DAY_FORTUNE_NOTE': note,
        'DAY_FORTUNE_TAG': tag,
        'DOS_ITEMS': dos_items,
        'CHONG_ZODIAC': item.get('วันชง', ''),
        'CHONG_DIRECTION': item.get('ทิศซัวะ', ''),
        'COLORS_LABEL': f'สีมงคล (ตามธาตุ {stem} {ELEM_THAI[el]} {ELEM_EN[el]})',
        'COLORS_GEN_SWATCHES': swatches(colors.get('เสริม', WUXING_COLORS[gen_el])),
        'COLORS_SAME_SWATCHES': swatches(colors.get('เข้ากกัน', WUXING_COLORS[el])),
        'COLORS_AVOID_SWATCHES': swatches(colors.get('ควรเลี่่ยง', WUXING_COLORS[ctrl_el])),
        'LOGIC_LABEL': f'ธาตุของวัน: {ELEM_THAI[el]} ({stem})',
        'LOGIC_ROWS': logic_rows,
    }

def render(date_str, sizes):
    item, src = load_facts(date_str)
    acc = analyze(date_str)
    vals = build_values(date_str, item, acc)
    outdir = ROOT / 'infographic' / f'chinese-almanac-{date_str.replace("-", "")}'
    outdir.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        for size in sizes:
            w, h = map(int, size.split('x'))
            tpl = (TPL_DIR / SIZE_TPL[size]).read_text(encoding='utf-8')
            for k, v in vals.items():
                tpl = tpl.replace('{{' + k + '}}', str(v))
            leftover = re.findall(r'\{\{[A-Z_]+\}\}', tpl)
            if leftover:
                print(f'WARNING {size}: unfilled placeholders {leftover}')
            html_path = outdir / ('infographic.html' if len(sizes) == 1 else f'infographic-{size}.html')
            html_path.write_text(tpl, encoding='utf-8')
            pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
            pg.goto(html_path.as_uri())
            pg.wait_for_timeout(800)
            png_path = outdir / ('infographic.png' if len(sizes) == 1 else f'infographic-{size}.png')
            pg.screenshot(path=str(png_path), clip={'x': 0, 'y': 0, 'width': w, 'height': h})
            pg.close()
            print(f'{size}: {html_path.name} + {png_path.name}')
        b.close()
    print(f'data source: {src}')
    print(f'output dir: {outdir}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ds = sys.argv[1]
    size_arg = '1080x1920'
    if '--size' in sys.argv:
        size_arg = sys.argv[sys.argv.index('--size') + 1]
    sizes = list(SIZE_TPL.keys()) if size_arg == 'all' else [size_arg]
    render(ds, sizes)
