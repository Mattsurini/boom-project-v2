import lunardate
from datetime import date

# Gan-Zhi tables
STEMS = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
BRANCHES = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']

STEM_ELEMENT = {
    '甲':'wood','乙':'wood','丙':'fire','丁':'fire','戊':'earth','己':'earth',
    '庚':'metal','辛':'metal','壬':'water','癸':'water',
}
BRANCH_ELEMENT = {
    '子':'water','丑':'earth','寅':'wood','卯':'wood','辰':'earth','巳':'fire',
    '午':'fire','未':'earth','申':'metal','酉':'metal','戌':'earth','亥':'water',
}
BRANCH_DATA = {
    '子':{'th':'ชวด','animal':'หนู'},
    '丑':{'th':'ฉลู','animal':'วัว'},
    '寅':{'th':'ขาล','animal':'เสือ'},
    '卯':{'th':'เถาะ','animal':'กระต่าย'},
    '辰':{'th':'มะโรง','animal':'มังกร'},
    '巳':{'th':'มะเส็ง','animal':'งู'},
    '午':{'th':'มะเมีย','animal':'ม้า'},
    '未':{'th':'มะแม','animal':'แพะ'},
    '申':{'th':'วอก','animal':'ลิง'},
    '酉':{'th':'ระกา','animal':'ไก่'},
    '戌':{'th':'จอ','animal':'หมา'},
    '亥':{'th':'กุน','animal':'หมู'},
}

WUXING_COLORS = {
    'wood':['เขียว'],
    'fire':['แดง','ชมพู','ม่วง'],
    'earth':['เหลือง','น้ำตาล'],
    'metal':['ขาว','ทอง','เงิน'],
    'water':['ดำ','น้ำเงิน'],
}

# Chinese New Year anchor: known dates, compute day offset
CHINESE_NEW_YEAR = {
    2025: date(2025,1,29),
    2026: date(2026,2,17),
    2027: date(2027,2,6),
}

def days_since_epoch(d):
    return (d - date(1900,1,1)).days

# Stem-branch for any Gregorian date: day stem-branch
# Reference: 1900-01-31 is 甲子日
REF_DATE = date(1900,1,31)
REF_STEM = 0  # 甲
REF_BRANCH = 4  # 辰 (1900-01-31 is 甲辰, idx 4)

def gan_zhi_day(d):
    delta = (d - REF_DATE).days
    stem_idx = (REF_STEM + delta) % 10
    branch_idx = (REF_BRANCH + delta) % 12
    stem = STEMS[stem_idx]
    branch = BRANCHES[branch_idx]
    return stem, branch

def gan_zhi_year(y):
    # Year stem branch: 1984 甲子
    year_stem_idx = (y - 1984) % 10
    year_branch_idx = (y - 1984) % 12
    return STEMS[year_stem_idx], BRANCHES[year_branch_idx]

def lunar_from_gregorian(y,m,d):
    ld = lunardate.LunarDate.from_solar_date(y,m,d)
    return ld.year, ld.month, ld.day, ld.isLeapMonth

def analyze(date_str):
    y,m,d = map(int, date_str.split('-'))
    gdate = date(y,m,d)
    
    # Lunar
    ly, lm, ld, leap = lunar_from_gregorian(y,m,d)
    
    # Gan-Zhi day
    stem, branch = gan_zhi_day(gdate)
    element = STEM_ELEMENT[stem]
    branch_el = BRANCH_ELEMENT[branch]
    
    # Year
    ystem, ybranch = gan_zhi_year(y)
    
    # Colors based on day stem element
    def colors_for(el):
        gen = {'wood':'water','fire':'wood','earth':'fire','metal':'earth','water':'metal'}[el]
        control = {'wood':'metal','fire':'water','earth':'wood','metal':'fire','water':'earth'}[el]
        return {
            'เสริม': WUXING_COLORS[gen],
            'เข้ากัน': WUXING_COLORS[el],
            'ควรเลี่ยง': WUXING_COLORS[control]
        }
    colors = colors_for(element)
    
    return {
        'gregorian': date_str,
        'lunar': {'year':ly,'month':lm,'day':ld,'leap':leap},
        'day_ganzhi': f'{stem}{branch}',
        'day_stem': stem,
        'day_branch': branch,
        'day_branch_th': BRANCH_DATA[branch]['th'],
        'day_element': element,
        'year_ganzhi': f'{ystem}{ybranch}',
        'year_branch': ybranch,
        'colors': colors
    }

if __name__ == '__main__':
    import sys
    ds = sys.argv[1] if len(sys.argv)>1 else '2026-10-03'
    import json
    print(json.dumps(analyze(ds), ensure_ascii=False, indent=2))
