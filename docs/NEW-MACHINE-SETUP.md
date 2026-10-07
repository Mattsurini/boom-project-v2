# ย้าย Boom Project ไปเครื่องใหม่ (ผ่าน GitHub)

เครื่องใหม่ได้ "สกิลแบบเดิม + การทำงานแบบเดิม" ได้ ถ้าทำ 4 ขั้นนี้ครบ

| ขั้น | อะไรมา | มาจาก |
|---|---|---|
| 1 | โค้ด + สกิล 158 ตัว + `.hermes.md` | `git clone` |
| 2 | venv + dependency + upstream repos + alias | `bash setup-boom.sh` |
| 3 | API key + login + PDF 1GB + cron/memory/vault | copy ด้วยมือ (git ทำแทนไม่ได้) |
| 4 | ตรวจว่าเหมือนเดิม | `boom-check` → 14/14 |

---

## ขั้นที่ 1 — clone (ทำบนเครื่องใหม่)

ต้องมีก่อน: `git`, Hermes (login ครั้งแรกให้เสร็จ เพื่อให้ `%HERMES_HOME%` ถูกสร้าง), และว่าง path `E:\Boom Project`

```bash
git clone https://github.com/Mattsurini/boom-project-v2.git "E:/Boom Project"
cd "E:/Boom Project"
```

clone ได้ ~43MB / ~1200 ไฟล์

> **ใช้ `boom-project-v2`** — repo `boom-project` เดิมถูกลบแล้วเพราะเคยมี API key
> หลุดใน commit (ดูหัวข้อ "เหตุการณ์ credential" ท้ายเอกสาร)

## ขั้นที่ 2 — setup (บนเครื่องใหม่)

```bash
cd "E:/Boom Project"
bash setup-boom.sh
```

สคริปต์นี้ทำให้อัตโนมัติ:

1. สร้าง `.venv` (Python 3.11 — wheel ของ pyswisseph/kerykeion สร้างจาก 3.11)
2. ติดตั้ง dependency ตาม `requirements.txt` (pin ไว้ทุกตัว)
3. `npm install` (iztro, crc-32)
4. clone upstream repo ที่ถูก git-ignore ไว้: `stellium`, `power-design`, `frontend-slides`, `Deep-Research-skills`
5. สร้าง `.env` จาก `.env.example`
6. mirror สกิล `.agents/skills` (tier0) → `%LOCALAPPDATA%\hermes\skills` (tier1)
7. สร้าง index + registry (libby → build-output-index → project_index → memory_db sync)
8. เขียน alias `boom-*` ลง `~/.bashrc`

alias ที่ได้:

```
boom-check      # core.validator + core.tests  ← ใช้ตรวจหลัง setup
boom-update     # รัน pipeline อัปเดต index ทั้งชุด
boom-transits   # transit_timeline_v3.py  (v3 คือ canonical)
boom-natal / boom-tarot / boom-eclipses
```

## ขั้นที่ 3 — copy สิ่งที่ git ทำแทนไม่ได้

| อะไร | ต้นทาง | หมายเหตุ |
|---|---|---|
| API key | `%LOCALAPPDATA%\hermes\.env` (เครื่องเก่า) | 18 ตัวแปร · ห้าม commit |
| Login | login ใหม่ | `auth.json` ผูกกับเครื่อง |
| PDF 1GB | `Knowledge\Astrology-Database\` (217 ไฟล์) + `Tarot Knowledge\` | git-ignore ตั้งใจ — GitHub เก็บโค้ด ไม่เก็บหนังสือ |
| Memory | `%HERMES_HOME%\memories\MEMORY.md`, `USER.md` | เป็น context ของ agent |
| Cron | `%HERMES_HOME%\cron\jobs.json` | งานที่ตั้งเวลาไว้ |
| Vault | `%HERMES_HOME%\vault\` | เข้ารหัส + ผูกเครื่อง ต้องใส่ใหม่ |

## ขั้นที่ 4 — ตรวจ

```bash
source ~/.bashrc
boom-check
```

ต้องได้ `14/14 criteria passed — VALID` และ core.tests ผ่าน 100%

ถ้าไม่ผ่าน มักเป็น 2 เรื่อง:
- **no-drift FAIL** → mirror ไม่ครบ รัน `bash setup-boom.sh` ซ้ำ (ขั้น 6 เท่านั้น)
- **loadable / registry FAIL** → venv ไม่ครบ รัน `pip install -r requirements.txt` ซ้ำ

---

## ทำไมถึงไม่ commit บางอย่าง

`.gitignore` ตัดไว้ 4 กลุ่ม เพราะมันไม่ควรอยู่ใน git:

- **`Knowledge/Astrology-Database/`** — PDF 217 ไฟล์ ~1GB. เกิน soft limit ของ GitHub (50MB เตือน, 100MB บล็อก) และ clone ช้าเปล่าๆ
- **`stellium/` `power-design/` `frontend-slides/` `Deep-Research-skills/`** — ของ upstream คนอื่น มี remote อยู่แล้ว การ vendor เข้า repo ทำให้เอาอัปเดตไม่ได้
- **`cache/`** — runtime DB + backup (sqlite, WAL) สร้างใหม่ได้เสมอ
- **`.agents/skills/.hub/` `.usage.json` `.curator_*`** — state ของ skill runtime เขียนทับทุกวัน commit แล้ว git จะขึ้น conflict ตลอด

ที่เหลือ commit หมด: สกิล 158 ตัว, `core/`, `scripts/`, index, `Output/`, `wiki/`, `AGENTS.md`, `.hermes.md`

## เรื่องที่เจอตอนตั้งค่า (แก้ให้แล้ว)

- **skills ไม่ได้ drift จริง** — ต่างกันแค่ CRLF/LF ที่ไฟล์ `research/arxiv/SKILL.md` (`core/validator.py` normalize newline อยู่แล้ว) ตอนตรวจจึงต้องเทียบ content ไม่ใช่ byte
- **`setup-boom.sh` เดิมตั้ง `HERMES_HOME` เป็นโฟลเดอร์โปรเจกต์** ทำให้ skills mirror / cron / memories / vault ชี้ผิดที่ ตอนนี้ชี้ `%LOCALAPPDATA%\hermes` ถูกต้อง
- **`boom-transits` เดิมชี้ `transit_timeline_v2.py`** ซึ่งถูกลบไปแล้ว (v3 คือ canonical) แก้เป็น v3
- **ไม่มี `requirements.txt`** ที่ root เครื่องใหม่จะไม่รู้ว่าต้องติดตั้งอะไร สร้างจาก `pip freeze` แล้ว (131 แพ็กเกจ)

## เหตุการณ์ credential (2026-10-07)

ระหว่างตั้งค่า git พบว่ามี credential หลุดในไฟล์ที่ถูก track — แก้แล้ว แต่ต้องจำไว้:

| ไฟล์ | มีอะไร | จัดการ |
|---|---|---|
| `sessions/*.json` (12 ไฟล์) | `Authorization: Bearer *** จริง | ลบออกจากทุก commit |
| `config.yaml` (root) | `api_key: nvapi-…` จริง | untrack + scrub + แทนด้วย `local-hermes-config.example.yaml` |
| `config.yaml.bak.20260905_164712` | key เดียวกัน | ลบออกจากทุก commit |
| `auth.json` | `credential_pool` (มีแต่ชื่อ env + sha2 fingerprint) | ลบออกจากทุก commit |

repo เดิม `boom-project` ถูกลบทิ้งแล้วเพราะ GitHub เก็บ object เก่าไว้ แม้ force-push แล้วก็ยังเข้าถึง commit ที่มี key ได้ (`gh api …/contents/config.yaml?ref=<old-sha>` ยังคืนไฟล์) เลยต้องสร้าง repo ใหม่ที่ชื่อ `boom-project-v2`

**NVIDIA key ต้อง rotate** — มันเคยอยู่ใน git ที่ push แล้ว ไม่ว่าจะลบ history ยังไง ก็ถือว่ารั่วแล้ว
