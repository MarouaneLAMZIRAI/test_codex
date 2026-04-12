# SyanaTek MVP (Windows Desktop)

SyanaTek is a Python desktop MVP for **3D guided vehicle diagnosis** with:
- database-driven vehicle selection,
- DAQ KPI dashboard with trends,
- step-by-step diagnosis,
- 3D part highlighting and isolation.

---

## 1) Recommended Stack and Why

- **Python 3.11**
- **PySide6** for desktop UI shell.
- **VTK via PyVista + PyVistaQt** for 3D rendering and interaction.
- **PostgreSQL + SQLAlchemy + psycopg** for data access.
- **pyqtgraph** for fast time-series charts.

### Can VTK satisfy requirements?
Yes. In production architecture, VTK can support:
- multi-part actors with per-part color/opacity,
- picking and hover selection,
- isolation (opacity/hide),
- subassembly visibility toggles,
- large model handling using decimation/LOD and culling.

For FBX-heavy enterprise workflows, prefer a pre-processing pipeline that converts FBX into normalized mesh bundles + metadata (UUID mapping) to avoid importer inconsistencies across vendors.

---

## 2) Architecture (MVP)

```text
syanatek/
  app/
    main.py
    config.py
    models/schema.py
    services/
      db.py
      repository.py
    ui/
      main_window.py
      dashboard_page.py
      diagnosis_page.py
    viewer/
      three_d_viewer.py
    utils/logging_config.py
  assets/
    parts_manifest.json
  database/sql/
    001_schema.sql
    002_seed_demo.sql
  scripts/
    init_db.py
    build_exe.bat
  requirements.txt
  .env.example
```

### Data flow
1. App starts -> logging initialized -> DB connect with retries.
2. Dashboard loads vehicle filters and DAQ timeseries from Repository.
3. User clicks **Recommended Actions**.
4. Diagnosis steps are loaded for selected vehicle.
5. Selecting a step fetches mapped part codes.
6. 3D viewer highlights target part(s) in red + optional isolate mode.

---

## 3) Database schema (proposed)

Core tables:
- `vehicles`
- `daq_samples`
- `parts`
- `diagnosis_steps`
- `step_part_links`

This enables many-to-many mapping (`diagnosis_steps <-> parts`) and future extension for work orders, technician sessions, and validation evidence.

---

## 4) Firm recommendation for Step <-> Part mapping

### Considered options
1. **DB-only mapping** (`step_id -> part_id`)
2. **CSV import mapping** (`step_code, part_name, file_name, transform, bbox`)
3. **Hybrid mapping** (**recommended**):
   - DB stores diagnosis logic and relationships.
   - JSON manifest stores asset metadata (file path, format, external IDs, transforms, hierarchy).

### Why hybrid wins
- DB remains clean for business logic and diagnostics.
- 3D asset teams can iterate manifests independently.
- Works for both:
  - **Case A** (single FBX with named nodes): store `external_id=node_name`.
  - **Case B** (many files): `part_code` maps directly to file entries.
- STL limitation (no sub-object names) is solved by **one-part-per-file discipline** + naming convention (`SYS_SUBSYS_PART_REV`).

### Manual vs automated
Manual:
- enforce stable naming in Blender/3dsMax,
- export transforms consistently,
- keep revisioned manifest updates.

Automated:
- validate mapping coverage,
- detect missing assets,
- generate import warnings,
- fallback to placeholder geometry.

---

## 5) User workflow

1. **Entry / Dashboard**
   - choose Manufacturer / Model / Year / Variant.
   - view KPI cards and trends.
   - filter time range.
2. **Recommended Actions** -> opens guided diagnosis.
3. **Guided module**
   - left: step list + instructions + YES/NO.
   - center/right: interactive 3D model.
   - select step -> mapped parts highlighted red.
   - optional isolate + reset camera.

---

## 6) Error handling strategy

- **DB connect failure**: retries, then offline demo mode with warning log.
- **Missing DAQ data**: non-blocking UI info message.
- **Step with no part link**: UI warning + clear highlight.
- **Missing/invalid meshes**: log technical error, load fallback primitives.
- **Logs**: `logs/syanatek.log` (rotating).

---

## 7) Phase plan

### MVP (this project)
- local Postgres integration,
- dashboard + chart trends,
- guided steps with basic validation,
- 3D highlight/isolation,
- offline demo fallback.

### V1
- robust FBX scene importer and part tree,
- alert/event timeline,
- custom date range,
- role-based authentication,
- asset integrity checker.

### V2
- cloud-hosted API,
- real-time DAQ streaming (MQTT/Kafka),
- annotations/measurement/exploded view,
- digital twin analytics and predictive diagnosis.

---

## 8) Risks and mitigations

- **Heavy CAD models** -> decimate, LOD meshes, lazy load subassemblies.
- **Naming inconsistency** -> enforce export conventions + CI validator.
- **Format variability (FBX)** -> normalize with conversion pipeline + manifest.
- **DB schema drift** -> migration tooling + contract tests.
- **Operator safety** -> hard-stop safety banners + mandatory checklist confirmations.

---

## 9) Setup & Run (exact)

## Prerequisites
- Windows 10/11
- Python **3.11.x**
- PostgreSQL running in pgAdmin (your server: `dev_serv`)

## Install
```bash
cd syanatek
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Configure DB (.env)
Edit `.env`:
```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=syanatek
DB_USER=postgres
DB_PASSWORD=12345678
```

> `dev_serv` is the pgAdmin saved server label. The app needs actual host/port/db/user/password above.

## Create schema + seed data
```bash
set PYTHONPATH=.
python scripts/init_db.py
```

Alternative with pgAdmin Query Tool:
- run `database/sql/001_schema.sql`
- then run `database/sql/002_seed_demo.sql`

## Start app
```bash
set PYTHONPATH=.
python app/main.py
```

---

## 10) Build SyanaTek.exe (Windows)

```bash
cd syanatek
.venv\Scripts\activate
scripts\build_exe.bat
```

Output executable:
- `dist/SyanaTek/SyanaTek.exe`

---

## 11) Notes on FBX/OBJ/STL strategy (production)

- OBJ/STL can load directly per-file in current MVP when listed in manifest.
- FBX support should use one of two paths:
  1. direct VTK FBX importer for scene-level loading,
  2. recommended: pre-convert FBX assets to normalized mesh package and keep part UUID mapping in manifest.

`assets/parts_manifest.json` is the contract point for future import pipeline upgrades.
