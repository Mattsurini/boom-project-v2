import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import date, timedelta

BASE = 'https://tarot.loveiseveryday.com/chinese-calendar'

def scrape_date(date_str):
    url = f'{BASE}/{date_str}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    
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
    # Find all art-section
    for sec in soup.find_all('section', class_='art-section'):
        h2 = sec.find('h2')
        if not h2:
            continue
        title = h2.get_text(strip=True)
        items = [li.get_text(strip=True) for li in sec.find_all('li')]
        if 'ควรทำ' in title:
            do = items
        elif 'ไม่ควรทำ' in title:
            dont = items
    
    # วันชง
    clash = ''
    suua = ''
    clash_sec = soup.find('h2', string=lambda t: t and 'วันชง' in t)
    if clash_sec:
        p = clash_sec.find_next('p')
        if p:
            text = p.get_text()
            import re
            m = re.search(r'ปี([^\s\(\)]+)', text)
            if m:
                clash = m.group(1)
            m2 = re.search(r'ทิศซัวะ.*?ทิศ([^\s]+)', text)
            if m2:
                suua = m2.group(1)
    
    # สีมงคล
    colors = {'เสริม':[], 'เข้ากัน':[], 'ควรเลี่ยง':[]}
    color_sec = soup.find('h2', string=lambda t: t and 'สีมงคล' in t)
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
                        vals = [v.strip() for v in val.split('/')]
                        if 'สีเสริม' in label:
                            colors['เสริม'] = vals
                        elif 'สีเข้ากัน' in label:
                            colors['เข้ากัน'] = vals
                        elif 'ควรเลี่ยง' in label:
                            colors['ควรเลี่ยง'] = vals
    
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
    start = date(2026,10,1)
    end = date(2026,10,31)
    results = []
    d = start
    while d <= end:
        ds = d.isoformat()
        try:
            res = scrape_date(ds)
            results.append(res)
            print(f'Scraped {ds}')
            time.sleep(0.5)
        except Exception as e:
            print(f'Error {ds}: {e}')
        d += timedelta(days=1)
    
    with open('E:/Boom Project/Output/Sources/Chinese-Astrology/chinese_calendar_oct2026.json','w',encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print('Saved')
