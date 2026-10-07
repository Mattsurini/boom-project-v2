# status-monitor-ui

Minimal status-dashboard UI style — clean flat cards on light gray, one amber accent, state colors, mono numerals. (Custom style, derived from the Gateway 9arm status page; full token spec: `DESIGN-status-page.md` in the Boom Project root.)

## Color Palette

- Background: light gray #F9FAFB (optionally near-black #09090B for a dark variant)
- Surface: white #FFFFFF cards with 1px hairline borders #E5E7EB
- Primary accent: amber #F59E0B (single accent — highlights, key numbers, CTA)
- State colors: emerald #10B981 (operational/positive), blue #3B82F6 (info/progress), red #EF4444 (error/negative)
- Tinted chips: emerald-50/700, amber-50/800, blue-50/800, red-50/700 — tinted background + dark text, never saturated fills
- Ink: #1F2937 primary, #4B5563 muted

## Visual Elements

- Flat cards, 12px rounded corners, hairline borders, tiny shadows only (no heavy elevation)
- 10px circular status dots with soft pulse on the active state
- Pill badges (fully rounded) for states/labels, tinted bg + dark text
- Progress bars: 8px tall, fully rounded, blue→indigo→emerald gradient fill
- One idea per card; rows separated by 1px dividers, not nested cards
- No hero sections, no gradient backgrounds, no decorative illustrations

## Typography

- Inter (400/500/600/700) with Noto Sans Thai fallback — load both from Google Fonts
- Small tight scale: 12px workhorse for data/labels, 14px body, 24–30px headings only
- Headings weight 600–700 with slight negative letter-spacing
- Uppercase + 0.05em tracking for small section labels
- ALL numbers (percentages, counts, timestamps, durations) in monospace — defining trait

## Best For

Status reports, uptime/health dashboards, quota & limit summaries, incident timelines, metric/KPI overflows, system health infographics
