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

# Gan-Zhi
STEMS = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
STEM_ELEMENT = {
    '甲':'wood','乙':'wood','丙':'fire','丁':'fire','戊':'earth','己':'earth',
    '庚':'metal','辛':'metal','壬':'water','癸':'water',
}
REF_DATE = datetime(1900,1,31)
def gan_zhi_day(dt):
    delta = (dt - REF_DATE).days
    stem_idx = delta % 10
    branch_idx = (4 + delta) % 12  # 1900-01-31 is 甲辰
    return STEMS[stem_idx], BRANCHES[branch_idx]

# Do/Don't lists keyed by day branch (simplified mapping from website)
DO_DONT = {
    '戌': {
        'ควรทำ': ['แต่งงาน','ตกลงหมั้น ทำข้อตกลง','สู่ขอ หมั้นหมาย','ไหว้บรรพบุรุษ บูชา','ขอพร','เดินทาง','ซ่อมแซม ต่อเติม','ขุดดิน เริ่มก่อสร้าง','ย้ายบ้าน','ขึ้นบ้านใหม่'],
        'ไม่ควรทำ': ['ฝังเข็ม','ตัดต้นไม้','ทำคาน','สร้างศาลเจ้า','จัดงานศพ','ฝังศพ']
    },
    '午': {
        'ควรทำ': ['พิธีเข้าสู่วัยผู้ใหญ่','อาบน้ำชำระกาย','เดินทาง','ซ่อมแซม ต่อเติม','ขุดดิน เริ่มก่อสร้าง','ย้ายบ้าน','ขึ้นบ้านใหม่','ขุดหลุมศพ','ฝังศพ'],
        'ไม่ควรทำ': ['แต่งงาน','เปิดร้าน เปิดกิจการ','ไหว้บรรพบุรุษ บูชา','ขอพร','ทำพิธีบวงสรวง','สู่ขอ หมั้นหมาย','ซ่อมฮวงซุ้ย']
    }
}

# Clash
HARM = [['子','未'],['丑','午'],['寅','巳'],['卯','辰'],['申','亥'],['酉','戌']]
BREAK = [['子','酉'],['午','卯'],['辰','丑'],['未','戌'],['寅','亥'],['巳','申']]
def rel(e,n):
    r=[]
    if e==n: r.append('self')
    if BRANCHES.index(e)==(BRANCHES.index(n)+6)%12: r.append('clash')
    return r

def analyze(date_str):
    y,m,d = map(int, date_str.split('-'))
    dt = datetime(y,m,d)
    zh = zhdate.ZhDate.from_datetime(dt)
    stem, branch = gan_zhi_day(dt)
    element = STEM_ELEMENT[stem]
    gen = {'wood':'water','fire':'wood','earth':'fire','metal':'earth','water':'metal'}[element]
    control = {'wood':'metal','fire':'water','earth':'wood','metal':'fire','water':'earth'}[element]
    colors = {
        'เสริม': WUXING_COLORS[gen],
        'เข้ากัน': WUXING_COLORS[element],
        'ควรเลี่ยง': WUXING_COLORS[control]
    }
    # Year branch
    year_branch_idx = (y-4) % 12
    year_branch = BRANCHES[year_branch_idx]
    clash_year = BRANCHES[(BRANCHES.index(branch)+6)%12]
    do_dont = DO_DONT.get(branch, DO_DONT['午'])
    return {
        'gregorian': date_str,
        'lunar': f"เดือน {zh.lunar_month} วันที่ {zh.lunar_day}",
        'day_ganzhi': f'{stem}{branch}',
        'day_branch_th': BRANCH_DATA[branch]['th'],
        'day_element': element,
        'ควรทำ': do_dont['ควรทำ'],
        'ไม่ควรทำ': do_dont['ไม่ควรทำ'],
        'วันชง': BRANCH_DATA[clash_year]['th'],
        'สีมงคล': colors
    }

if __name__ == '__main__':
    import sys
    ds = sys.argv[1] if len(sys.argv)>1 else '2026-10-03'
    print(json.dumps(analyze(ds), ensure_ascii=False, indent=2))
