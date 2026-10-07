# ขั้นตอนลง Windows ใหม่ — Boom Project + Hermes

ทำตามลำดับนี้ ไม่ต้องข้ามขั้น ถ้าขั้นไหนล้มก็หยุดตรงนั้น

**เวลารวม: ~30-45 นาที** (ไม่นับเวลาติดตั้ง Windows + อัปเดต Windows)

---

## ⚠️ ขั้นที่ 0 — ทำก่อนฟอร์แมตเครื่องเก่า (ห้ามข้าม!)

ฟอร์แมตแล้วไฟล์เหล่านี้หายถาวร กู้คืนไม่ได้

### 0.1 เอาโฟลเดอร์ hermes-state ไปที่อื่นก่อน

ผมรัน `export-hermes-state.sh` ให้แล้ว ผลลัพธ์อยู่ที่:

```
E:\Boom Project\hermes-state\     187KB, 26 ไฟล์
```

**เอาไปเก็บที่อื่นทันที** — USB, external disk, หรือ copy ไปโฟลเดอร์อื่นในเครื่อง

ห้ามเก็บใน OneDrive / Google Drive / iCloud (มันจะ sync credential ขึ้น cloud)
ห้าม commit ขึ้น GitHub

### 0.2 Copy PDF 1GB

จาก `E:\Boom Project\`:

```
Knowledge\Astrology-Database\     217 ไฟล์ ~1GB
Tarot Knowledge\
```

### 0.3 Copy โฟลเดอร์โปรเจกต์ทั้งก้อน (ทางเลือก — ถ้าอยากมีของเต็มในเครื่องใหม่)

`E:\Boom Project` ทั้งโฟลเดอร์ (รวม PDF) — ถ้า copy ทั้งก้อน ขั้น 4 จะไม่ต้อง copy PDF ซ้ำ
แต่ถ้า copy ทั้งก้อน **อย่า clone ทับ** ให้ไปที่ `E:\` แล้ว setup เฉพาะ venv/skills แทน

### 0.4 จดหมายเหตุ

เขียนไว้ในสมอง/กระดาษ 2 อย่าง:
- NVIDIA key เดิม (จะ rotate ทิ้ง) — ไม่ต้องจด
- บัญชี GitHub: `Mattsurini`
- Telegram: bot token อยู่ใน `hermes-state\auth.json` (ไม่ต้องจด)

---

## ขั้นที่ 1 — ติดตั้ง Git + Hermes

### 1.1 Git

ดาวน์โหลดจาก https://git-scm.com/download/win ติดตั้ง (Next → Next → ... → Install)

เช็คว่าเปิด Git Bash แล้วพิมพ์:
```bash
git --version
```

### 1.2 Hermes Desktop (วิธีที่เครื่องเก่าใช้)

ดาวน์โหลด installer จาก https://hermes-agent.nousresearch.com แล้วรัน

เครื่องเก่าติดตั้งแบบ `Install method: git` — installer จะ clone `NousResearch/hermes-agent` มาลง `%LOCALAPPDATA%\hermes`

> ถ้าอยากลงแบบ command-line ไม่เอา Desktop (Windows):
> ```powershell
> iex (irm https://hermes-agent.nousresearch.com/install.ps1)
> ```

### 1.3 เช็คว่า Hermes มาแล้ว

เปิด Git Bash:
```bash
hermes --version
```
ต้องขึ้น `Hermes Agent v0.21.x`

### 1.4 Login

```bash
hermes setup --portal
```
เปิดเบราว์เซอร์ login → ครบแล้ว `auth.json` จะถูกสร้าง

### 1.5 ปิด Hermes ให้หมด

ปิดทุกหน้าต่าง Hermes / terminal ที่รัน Hermes (สำคัญ — ตอน copy state ต้องไม่มีอะไรกำลังเขียนไฟล์)

---

## ขั้นที่ 2 — กู้ state ของ Hermes กลับ

ทั้งหมดมาจาก `E:\Boom Project\hermes-state\` (หรือที่ USB ไปวางไว้)
ปลายทางคือ `%LOCALAPPDATA%\hermes\` = `C:\Users\<ชื่อผู้ใช้>\AppData\Local\hermes\`

Git Bash:

```bash
S="$LOCALAPPDATA/hermes"
SRC="E:/Boom Project/hermes-state"      # เปลี่ยนถ้าย้ายไปที่อื่น

cp "$SRC/.env"                  "$S/.env"
cp "$SRC/auth.json"             "$S/auth.json"
cp "$SRC/config.yaml"           "$S/config.yaml"
cp "$SRC/SOUL.md"               "$S/SOUL.md"
cp "$SRC/channel_directory.json" "$S/channel_directory.json"
cp "$SRC/memories/MEMORY.md"    "$S/memories/MEMORY.md"
cp "$SRC/memories/USER.md"      "$S/memories/USER.md"
cp "$SRC/cron/jobs.json"        "$S/cron/jobs.json"
cp -r "$SRC/plugins/karpathy-guidelines" "$S/plugins/"
```

เช็ค:
```bash
ls -la "$LOCALAPPDATA/hermes/.env" "$LOCALAPPDATA/hermes/memories/"
```

---

## ขั้นที่ 3 — เปิด Hermes แล้วสลับ NVIDIA key

### 3.1 สร้าง key ใหม่

ไปที่ https://build.nvidia.com → เมนู API Keys → สร้างใหม่ → เอา value ไว้

(ของเดิมหลุดใน git ที่ถูกทิ้งไปแล้ว ถือว่ารั่ว — ต้องเปลี่ยน)

### 3.2 ใส่ key ใหม่

แก้ `%LOCALAPPDATA%\hermes\.env`:
```
NVIDIA_API_KEY=<key ใหม่>
```

### 3.3 ทดสอบว่า Hermes ใช้ได้

เปิด Hermes (Desktop หรือ `hermes` ใน terminal) ถามอะไรสักอย่าง
ถ้าเรียกโมเดลได้ → ใช้ได้

---

## ขั้นที่ 4 — clone โปรเจกต์

> ถ้าทำขั้น 0.3 (copy ทั้งก้อน) ให้ข้ามขั้นนี้ แล้วไปทำขั้น 5 ต่อ

Git Bash:
```bash
git clone https://github.com/Mattsurini/boom-project-v2.git "E:/Boom Project"
cd "E:/Boom Project"
```

ผลลัพธ์: 1,197 ไฟล์, 158 สกิล, ~43MB

> ⚠️ ใช้ชื่อ **`boom-project-v2`** ไม่ใช่ `boom-project`
> repo เดิมถูกทิ้งเพราะเคยมี API key อยู่ใน commit

---

## ขั้นที่ 5 — setup

```bash
cd "E:/Boom Project"
bash setup-boom.sh
```

ทำอัตโนมัติ 7 อย่าง:
1. สร้าง `.venv` (Python 3.11)
2. ติดตั้ง dependency จาก `requirements.txt` (131 แพ็กเกจ)
3. `npm install`
4. clone upstream repo 4 ตัว (`stellium`, `power-design`, `frontend-slides`, `Deep-Research-skills`)
5. สร้าง `.env` จาก `.env.example`
6. mirror สกิล `.agents/skills` → `%LOCALAPPDATA%\hermes\skills`
7. สร้าง index + registry

ถ้าขึ้น `[WARN] .../hermes/.env MISSING` แปลว่าขั้น 2 ยังไม่ครบ — กลับไปทำขั้น 2

---

## ขั้นที่ 6 — ใส่ PDF (ถ้ายังไม่ได้ทำตอน clone)

ถ้าข้ามขั้น 4 เพราะ copy ทั้งก้อนมาแล้ว ก็ข้ามขั้นนี้

คัดลอก `Knowledge\Astrology-Database\` + `Tarot Knowledge\` กลับเข้า `E:\Boom Project\`

---

## ขั้นที่ 7 — ตรวจ

```bash
source ~/.bashrc
boom-check
```

ต้องได้:
```
14/14 criteria passed — VALID
routing accuracy: 28/28 (100%)
```

**ถ้าไม่ผ่าน:**
- `no-drift FAIL` → รัน `bash setup-boom.sh` ซ้ำ
- `loadable FAIL` → `.venv/Scripts/python -m pip install -r requirements.txt`
- ไม่มีคำสั่ง `boom-check` → `source ~/.bashrc` (alias ถูกเขียนตอน setup)

---

## ขั้นที่ 8 — ทดสอบว่าใช้ได้จริง

```bash
cd "E:/Boom Project"
.venv/Scripts/python -m core.router "ทำนาย transits สัปดาห์นี้"
```
ควร route ไปที่ skill ที่ถูกต้อง

เปิด Hermes ถามว่า "อ่านโปรเจกต์นี้ให้หน่อย" — ต้องเห็นทั้ง 158 สกิล

---

## ทำอะไรไม่ได้ถ้าไม่ทำ

| ของ | ทำไม่ได้ | ทางแก้ |
|---|---|---|
| API key ของ provider | อยู่ใน `auth.json`/`.env` ที่ผูกเครื่อง | ขั้น 2 |
| Telegram chat | ผูกกับ chat id ของคุณ | ขั้น 2 (`channel_directory.json`) |
| memory ของ agent | อยู่ใน `memories/` | ขั้น 2 |
| หนังสือ PDF | git ไม่เก็บ (1GB) | ขั้น 0.2 / 6 |
| NVIDIA key เดิม | หลุดใน git ที่ถูกทิ้ง | ต้อง rotate (ขั้น 3) |

---

## สรุป

```
เครื่องเก่า:  export state (ทำแล้ว) → copy PDF → เก็บ USB → ฟอร์แมต
เครื่องใหม่: git + Hermes → login → ปิด → copy state → เปิด → rotate key
             → clone → setup → boom-check → ทดสอบ
```

ถ้าติดที่ไหนบอกได้ จะช่วยจุดนั้น
