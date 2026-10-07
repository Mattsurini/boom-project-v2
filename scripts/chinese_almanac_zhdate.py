import zhdate
from datetime import datetime
import json

# Tables from chong.B7uNF4vp.js
BRANCHES = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
BRANCH_DATA = {
    '子':{'th':'ชวด','animal':'หนู','el':'water'},
    '丑':{'th':'ฉลู','animal':'วัว','el':'earth'},
    '寅':{'th':'ขาล','animal':'เสือ','el':'wood'},
    '卯':{'th':'เถาะ','animal':'กระต่าย','el':'wood'},
    '辰':{'th':'มะโรง','animal':'มังกร','el':'earth'},
    '巳':{'th':'มะเส็ง','animal':'งู','el':'fire'},
    '午':{'th':'มะเมีย','animal':'ม้า','el':'fire'},
    '未':{'th':'มะแม','animal':'แพะ','el':'earth'},
    '申':{'th':'วอก','animal':'ลิง','el':'metal'},
    '酉':{'th':'ระกา','animal':'ไก่','el':'metal'},
    '戌':{'th':'จอ','animal':'หมา','el':'earth'},
    '亥':{'th':'กุน','animal':'หมู','el':'water'},
}
WUXING_COLORS = {
    'wood':['เขียว'],
    'fire':['แดง','ชมพู','ม่วง'],
    'earth':['เหลือง','น้ำตาล'],
    'metal':['ขาว','ทอง','เงิน'],
    'water':['ดำ','น้ำเงิน'],
}

# Gan-Zhi stem-branch for day
STEMS = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
STEM_ELEMENT = {
    '甲':'wood','乙':'wood','丙':'fire','丁':'fire','戊':'earth','己':'earth',
    '庚':'metal','辛':'metal','壬':'water','癸':'water',
}

REF_DATE = datetime(1900,1,31)
REF_STEM_IDX = 0  # 甲
REF_BRANCH_IDX = 4  # 辰 (1900-01-31 is 甲辰, idx 4)

def gan_zhi_day(dt):
    delta = (dt - REF_DATE).days
    stem_idx = (REF_STEM_IDX + delta) % 10
    branch_idx = (REF_BRANCH_IDX + delta) % 12
    return STEMS[stem_idx], BRANCHES[branch_idx]

def analyze(date_str):
    y,m,d = map(int, date_str.split('-'))
    dt = datetime(y,m,d)
    zh = zhdate.ZhDate.from_datetime(dt)
    # Day Gan-Zhi
    stem, branch = gan_zhi_day(dt)
    element = STEM_ELEMENT[stem]
    # Colors
    gen = {'wood':'water','fire':'wood','earth':'fire','metal':'earth','water':'metal'}[element]
    control = {'wood':'metal','fire':'water','earth':'wood','metal':'fire','water':'earth'}[element]
    colors = {
        'เสริม': WUXING_COLORS[gen],
        'เข้ากัน': WUXING_COLORS[element],
        'ควรเลี่ยง': WUXING_COLORS[control]
    }
    return {
        'gregorian': date_str,
        'lunar': {'year': zh.lunar_year, 'month': zh.lunar_month, 'day': zh.lunar_day, 'leap': zh.leap_month},
        'day_ganzhi': f'{stem}{branch}',
        'day_branch': branch,
        'day_branch_th': BRANCH_DATA[branch]['th'],
        'day_element': element,
        'colors': colors,
        'chinese_str': str(zh)
    }

if __name__ == '__main__':
    import sys
    ds = sys.argv[1] if len(sys.argv)>1 else '2026-10-03'
    print(json.dumps(analyze(ds), ensure_ascii=False, indent=2))
