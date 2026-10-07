---
topic: ml-ai
subtopic: hermes-training-improvement
domain: ML-AI
stage: Plawan
created_utc: 2026-08-09T15:40:00Z
---
# Research Blueprint: วิธีทำให้ Hermes เก่งขึ้น

## Pipeline subject
วิธีปรับปรุง Hermes ให้ทำงานกับ BooM ได้ถูกขึ้น สม่ำเสมอขึ้น ปลอดภัยขึ้น และตรวจสอบได้—not merely selecting a model.

## Core hypothesis
ประสิทธิภาพที่เพิ่มขึ้นในระยะแรกจะมาจาก evaluation, tool contracts, skills, memory policy, context retrieval และ routing มากกว่าการเปลี่ยน model weights การทำ SFT/DPO/RL ควรเกิดหลังจากระบบมี baseline และพบ behavior gap ที่คงที่จริง

## Decision questions
1. Hermes-native skills, memory, tools, routing และ fallback เปลี่ยนอะไรได้จริง และเปลี่ยนอะไรไม่ได้
2. จะวัดว่า Hermes เก่งขึ้นอย่างไรโดยไม่หลงกับ prompt overfitting
3. failure แบบใดควรแก้ด้วย skill/context/memory และแบบใดจึงควร train model
4. trace SFT, DPO หรือ RL/RFT แบบใดเหมาะกับ Thai style, tool loops, coding และ research
5. safety, privacy, provider drift และ rollback gate ต้องวางตรงไหน

## Success markers
- accepted-result rate ดีขึ้นบน holdout ที่ไม่เคยใช้เขียน skill
- tool-call correctness และ file verification ดีขึ้น
- Thai/PAC style score ดีขึ้นโดย factuality ไม่ตก
- citation/support accuracy ดีขึ้น
- memory recall ถูก scope และไม่ปนข้อมูล
- latency, retries, cost per accepted result และ safety ไม่แย่ลง

## Constraints
ห้าม train secrets/client data; ห้ามให้ learned policy ข้าม approval boundary; ต้อง pin model/provider/tool versions และเก็บ baseline ก่อนทุกการเปลี่ยนแปลง
