import requests
from bs4 import BeautifulSoup
import json
import time

BASE = 'https://tarot.loveiseveryday.com/chinese-calendar'

def scrape_date(date_str):
    url = f'{BASE}/{date_str}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Facts table
    facts = {}
    table = soup.find('table', class_='facts')
    if table:
        for tr in table.find_all('tr'):
            th = tr.find('th')
            td = tr.find('td')
            if th and td:
                facts[th.get_text(strip=True)] = td.get_text(strip=True)
    
    # ควรทำ/ไม่ควรทำ
    do = []
    dont = []
    cdo = soup.find('div', class_='cdo')
    if cdo:
        sections = cdo.find_all('section')
        for sec in sections:
            h2 = sec.find('h2')
            if h2:
                txt = h2.get_text(strip=True)
                items = [li.get_text(strip=True) for li in sec.find_all('li')]
                if 'ควรทำ' in txt:
                    do = items
                elif 'ไม่ควรทำ' in txt:
                    dont = items
    
    # วันชง
    clash = ''
    suua = ''
    clash_sec = soup.find('h2', string='วันชง')
    if clash_sec:
        p = clash_sec.find_next('p')
        if p:
            clash_text = p.get_text()
            # extract ปี...
            import re
            m = re.search(r'ปี([^\s\(]+)', clash_text)
            if m:
                clash = m.group(1)
            m2 = re.search(r'ทิศซัวะ.*?ทิศ([^\s]+)', clash_text)
            if m2:
                suua = m2.group(1)
    
    # สีมงคล
    colors = {'เสริม':[], 'เข้ากัน':[], 'ควรเลี่ยง':[]}
    color_sec = soup.find('h2', string='สีมงคลแบบจีนวันนี้')
    if color_sec:
        ul = color_sec.find_next('ul', class_='cshirts')
        if ul:
            for li in ul.find_all('li'):
                b = li.find('b')
                if b:
                    label = b.get_text(strip=True)
                    span = li.find('span')
                    if span:
                        val = span.get_text(strip=True)
                        if 'สีเสริม' in label:
                            colors['เสริม'] = [v.strip() for v in val.split('/')]
                        elif 'สีเข้ากัน' in label:
                            colors['เข้ากัน'] = [v.strip() for v in val.split('/')]
                        elif 'ควรเลี่ยง' in label:
                            colors['ควรเลี่ยง'] = [v.strip() for v in val.split('/')]
    
    return {
        'date': date_str,
        'facts': facts,
        'ควรทำ': do,
        'ไม่ควรทำ': dont,
        'วันชง': clash,
        'ทิศซัวะ': suua,
        'สีมงคล': colors
    }

if __name__ == '__main__':
    dates = ['2026-10-01','2026-10-02','2026-10-03','2026-10-04','2026-10-05']
    results = []
    for d in dates:
        try:
            res = scrape_date(d)
            results.append(res)
            print(f'Scraped {d}')
            time.sleep(1)
        except Exception as e:
            print(f'Error {d}: {e}')
    with open('E:/Boom Project/Output/Sources/Chinese-Astrology/chinese_calendar_lookup.json','w',encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print('Saved')
