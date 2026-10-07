// Zi Wei Dou Shu chart calculator using iztro
// Usage: node scripts/ziwei_chart.js <birthDate> <birthHour> <gender> <lang>
// Example: node scripts/ziwei_chart.js "1996-11-20" 20 "女" "zh-CN"
// birthHour = actual hour (0-23), auto-converted to Chinese timeIndex (时辰)

const iztro = require('iztro');

const args = process.argv.slice(2);
const birthDate = args[0];
const actualHour = parseInt(args[1]);
const gender = args[2] || '女';
const lang = args[3] || 'zh-CN';

if (!birthDate || isNaN(actualHour)) {
    console.error('Usage: node scripts/ziwei_chart.js <YYYY-MM-DD> <birthHour> <gender> <lang>');
    console.error('birthHour = actual clock hour (0-23)');
    console.error('Example: node scripts/ziwei_chart.js "1996-11-20" 20 "女" "zh-CN"');
    process.exit(1);
}

// Convert hour to Chinese time index (时支)
// 子=23:00-00:59=0, 丑=1, 寅=2, 卯=3, 辰=4, 巳=5, 午=6, 未=7, 申=8, 酉=9, 戌=10, 亥=11
const CHINESE_HOURS = [
    { name: '子', range: [23, 0], index: 0 },
    { name: '丑', range: [1, 2], index: 1 },
    { name: '寅', range: [3, 4], index: 2 },
    { name: '卯', range: [5, 6], index: 3 },
    { name: '辰', range: [7, 8], index: 4 },
    { name: '巳', range: [9, 10], index: 5 },
    { name: '午', range: [11, 12], index: 6 },
    { name: '未', range: [13, 14], index: 7 },
    { name: '申', range: [15, 16], index: 8 },
    { name: '酉', range: [17, 18], index: 9 },
    { name: '戌', range: [19, 20], index: 10 },
    { name: '亥', range: [21, 22], index: 11 },
];

function hourToTimeIndex(h) {
    for (const ch of CHINESE_HOURS) {
        const [lo, hi] = ch.range;
        if (lo === 23) {
            if (h === 23 || h === 0) return ch.index;
        } else if (h >= lo && h <= hi) {
            return ch.index;
        }
    }
    return 0;
}

const timeIndex = hourToTimeIndex(actualHour);
const chineseName = CHINESE_HOURS.find(ch => ch.index === timeIndex).name;

// Calculate Zi Wei chart
const astrolabe = iztro.astro.bySolar(birthDate, timeIndex, gender, true, lang);

// Extract structured data
const result = {
    input: {
        birthDate,
        birthHour: actualHour,
        chineseHour: `${chineseName}时 (index ${timeIndex})`,
        gender,
        lang,
    },
    // Chinese calendar info
    lunarDate: astrolabe.lunarDate,
    chineseDate: astrolabe.chineseDate,
    
    // Five Elements (五行局)
    fiveElements: astrolabe.fiveElements,
    
    // 12 Palaces with their stars
    palaces: astrolabe.palaces.map(p => ({
        name: p.name,
        index: p.index,
        isBodyPalace: p.isBodyPalace,
        isOriginalPalace: p.isOriginalPalace,
        heavenlyStem: p.heavenlyStem,
        earthlyBranch: p.earthlyBranch,
        majorStars: p.majorStars.map(s => ({
            name: s.name,
            type: s.type,
            brightness: s.brightness,
        })),
        minorStars: p.minorStars.map(s => ({
            name: s.name,
            type: s.type,
            brightness: s.brightness,
        })),
        adjectiveStars: p.adjectiveStars.map(s => ({
            name: s.name,
            type: s.type,
            brightness: s.brightness,
        })),
    })),
};

console.log(JSON.stringify(result, null, 2));
