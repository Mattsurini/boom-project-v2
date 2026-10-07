# Chinese Astrology Scripts

This folder documents command entry points for Chinese Astrology workflows in Boom Project.

## Zi Wei natal chart

```bash
cd "E:/Boom Project"
node scripts/ziwei_chart.js "1996-11-20" 20 "女" "zh-CN"
```

## BaZi / HuangLi

Current primary workflow uses Hermes skills:

- `cantian-bazi` for BaZi chart, Liu Nian/Liu Yue/Liu Ri/Liu Shi, HuangLi
- `openfate-bazi` if OpenFate MCP is configured

Do not manually calculate pillars in prose.

## Future wrapper idea

Add a project-local wrapper later:

```txt
scripts/chinese_astrology/daily_chinese_report.py
```

Expected output:

- BaZi day/cycle data
- HuangLi good/avoid
- PAC angle
- source labels
```
