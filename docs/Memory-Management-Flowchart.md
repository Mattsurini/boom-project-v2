---
title: "Memory Management Flowchart"
date: '2026-08-23'
type: "note"
stage: "Knowledge"
topic: "memory-management"
tags:
- ml-ai
---

```mermaid
flowchart TD
    %% ===== INPUT CLASSIFICATION =====
    A([ข้อมูลใหม่เข้ามา]) --> B{BooM สั่งชัด?<br/>\"จำไว้ว่า\", \"บันทึกว่า\"}
    B -->|ใช่| C[Approved Auto-Patch]
    B -->|ไม่ใช่| D{สรุปจากบริบท/<br/>คาดเดา/ไม่แน่ชัด?}
    D -->|ใช่| E[Review First → ถาม BooM]
    D -->|ไม่ใช่| F{Task progress,<br/>ID หมดอายุ, Secrets,<br/>คุยทั่วไป?}
    F -->|ใช่| G[Do Not Store]
    F -->|ไม่ใช่| H[Review First → ถาม BooM]

    %% ===== WRITE PATH =====
    C --> I[Classify: category, tags,<br/>source=user-stated, lifecycle=active]
    E -->|BooM approve| I
    H -->|BooM approve| I
    I --> J{Target layer?}
    J -->|Identity, Preferences,<br/>Durable rules| K[Hermes Native Memory<br/>MEMORY.md]
    J -->|Structured facts,<br/>FTS search, Trust score| L[Holographic fact_store<br/>SQLite + FTS5]
    J -->|Conversational context,<br/>Semantic recall| M[Honcho<br/>PostgreSQL]
    J -->|Project knowledge,<br/>Evidence, Artifacts| N[Project Files<br/>E:\Boom Project\]

    %% ===== CONFLICT CHECK =====
    K --> O[Conflict Check:<br/>search existing facts]
    L --> O
    O --> P{Conflict with<br/>existing fact?}
    P -->|ใช่| Q[Ask BooM → Supersede/Archive old]
    P -->|ไม่| R[Write & Verify]

    %% ===== VERIFICATION =====
    R --> S[Verify: search/probe<br/>fact returns correctly]
    S --> T{Verify OK?}
    T -->|ไม่| U[Fix & Retry]
    T -->|ใช่| V[Done ✓]

    %% ===== MAINTENANCE LOOP =====
    W([Scheduled Maintenance<br/>Weekly/Monthly]) --> X{Native > 80%<br/>or Facts > 15-20?}
    X -->|ใช่| Y[Cleanup Routine]
    X -->|ไม่| Z[Skip]

    Y --> Y1[fact_store list / memory read all]
    Y1 --> Y2{Duplicate/Stale/Wrong?}
    Y2 -->|Duplicate| Y3[Update → merge →<br/>mark old superseded]
    Y2 -->|Stale| Y4[Update status=archived<br/>keep provenance]
    Y2 -->|Wrong| Y5[Update correct content<br/>source=corrected]
    Y2 -->|OK| Y6[Keep]

    Y3 --> Y7[Backup → Write → Verify]
    Y4 --> Y7
    Y5 --> Y7
    Y7 --> V

    %% ===== BACKUP =====
    V -.-> BA[Backup: hermes backup<br/>--quick --label after-cleanup]

    %% ===== STYLING =====
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef action fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef storage fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    classDef warn fill:#ffebee,stroke:#c62828,stroke-width:2px;
    classDef done fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;

    class B,D,F,J,P,T,X,Y2 decision;
    class C,E,G,H,I,O,Q,R,S,U,Y1,Y3,Y4,Y5,Y6,Y7 action;
    class K,L,M,N storage;
    class G warn;
    class V,BA done;
```