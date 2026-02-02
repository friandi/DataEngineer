# Source-to-Target Mapping (STM)
## PMIS Data Platform

---

### Document Information

| Item | Description |
|-----|-------------|
| Document Name | Source-to-Target Mapping (STM) |
| System Name | PMIS Data Platform |
| Version | 1.0 |
| Status | Draft |
| Classification | Public / Reference |
| Owner | Data Engineering |
| Last Updated | YYYY-MM-DD |

---

## 1. Overview

This STM document defines how each **source field** maps to a **target table/column** in the PMIS Data Platform, including:
- Transformation logic
- Data type casting
- Business rules references
- Data quality checks
- Incremental strategy

---

## 2. Source Systems Register

> List all sources used in the platform.

| Source System | Source Type | Owner | Access Method | Refresh | Notes |
|--------------|------------|-------|--------------|--------|------|
| PMIS Master | Database | - | JDBC/ODBC | Daily | Project master data |
| Planning | File/API | - | CSV/API | Daily | Planned schedule/progress |
| Progress Report | File/API | - | CSV/API | Daily | Actual progress |
| Finance | Database | - | JDBC/ODBC | Monthly | Budget/actual/forecast |

---

## 3. Mapping Conventions

### 3.1 Target Layers
- **STG**: standardized raw ingestion (minimal transforms)
- **INT**: conformed/intermediate (business rules applied)
- **MART**: analytics-ready (facts/dims, aggregates)

### 3.2 Transform Notation (Example)
- `TRIM(x)` : remove leading/trailing spaces
- `UPPER(x)` : uppercase
- `CAST(x AS DATE)` : type casting
- `COALESCE(a,b)` : default handling
- `DERIVED` : calculated from multiple fields

### 3.3 Rule References
Use rule IDs from `business_rules.md`:
- `VR-*` Validation Rules
- `DR-*` Derivation Rules
- `CR-*` Calculation Rules
- `SR-*` Status Rules
- `FR-*` Financial Rules

---

# 4. STM — DIM_PROJECT

### Target Table Metadata

| Item | Value |
|------|-------|
| Target Table | `DIM_PROJECT` |
| Layer | MART |
| Grain | 1 row per project |
| Keys | PK: `project_id` |
| Load Type | Incremental / SCD Type 2 (optional) |
| Natural Key | `project_id` |
| Incremental Column | `dt_updated` (recommended) |

---

## 4.1 Field Mapping — DIM_PROJECT

| Map ID | Target Table | Target Column | Target Data Type | Source System | Source Object | Source Column | Transform Logic | Default / Null Handling | Rule Ref | DQ Checks | Notes |
|-------|--------------|--------------|------------------|--------------|--------------|--------------|-----------------|-------------------------|----------|----------|------|
| STM-DP-001 | DIM_PROJECT | project_id | string | PMIS Master | project_master | project_id | `TRIM(project_id)` | Reject if null | VR-01 | DQ-01 unique/not null | Primary identifier |
| STM-DP-002 | DIM_PROJECT | project_name | string | PMIS Master | project_master | project_name | `TRIM(NORMALIZE_SPACES(project_name))` | Null → `UNKNOWN` | - | Not null preferred | Standard naming |
| STM-DP-003 | DIM_PROJECT | company_code | string | PMIS Master | project_master | company_code | `TRIM(company_code)` | Null allowed | - | FK exists check | Join to DIM_COMPANY |
| STM-DP-004 | DIM_PROJECT | location | string | PMIS Master | project_master | location | `TRIM(location)` | Null allowed | - | Domain check | Optional domain |
| STM-DP-005 | DIM_PROJECT | dt_start | date | Contract | contract_hdr | start_date | `CAST(start_date AS DATE)` | Null allowed | VR-02 | Valid date | - |
| STM-DP-006 | DIM_PROJECT | dt_end_target | date | Planning | plan_hdr | target_end_date | `CAST(target_end_date AS DATE)` | Null allowed | VR-02 | Valid date | must be >= start |
| STM-DP-007 | DIM_PROJECT | project_status | string | DERIVED | - | - | `DERIVE_STATUS(dt_start, dt_end_target, actual_progress_pct)` | Default `HLD` | DR-01 | Domain check | Derived status |
| STM-DP-008 | DIM_PROJECT | dt_created | timestamp | SYSTEM | - | - | `CURRENT_TIMESTAMP` | Not null | - | Not null | Load time |
| STM-DP-009 | DIM_PROJECT | dt_updated | timestamp | SYSTEM | - | - | `CURRENT_TIMESTAMP` | Not null | - | Not null | Update time |

---

# 5. STM — FACT_PROGRESS

### Target Table Metadata

| Item | Value |
|------|-------|
| Target Table | `FACT_PROGRESS` |
| Layer | MART |
| Grain | 1 row per project per `dt_report` |
| Keys | PK: (`project_id`, `dt_report`) |
| Load Type | Incremental |
| Incremental Column | `dt_report` or `dt_ingested` |

---

## 5.1 Field Mapping — FACT_PROGRESS

| Map ID | Target Table | Target Column | Target Data Type | Source System | Source Object | Source Column | Transform Logic | Default / Null Handling | Rule Ref | DQ Checks | Notes |
|-------|--------------|--------------|------------------|--------------|--------------|--------------|-----------------|-------------------------|----------|----------|------|
| STM-FP-001 | FACT_PROGRESS | project_id | string | Progress Report | progress | project_id | `TRIM(project_id)` | Reject if null | VR-01 | DQ-01 + RI | Must exist in DIM_PROJECT |
| STM-FP-002 | FACT_PROGRESS | dt_report | date | Progress Report | progress | report_date | `CAST(report_date AS DATE)` | Reject if null | VR-02 | DQ-02 | Reporting grain |
| STM-FP-003 | FACT_PROGRESS | planned_progress_pct | decimal(5,2) | Planning | plan | progress_pct | `CAST(progress_pct AS DECIMAL(5,2))` | Null allowed | VR-03 | Range 0–100 | Standardize units |
| STM-FP-004 | FACT_PROGRESS | actual_progress_pct | decimal(5,2) | Progress Report | progress | progress_pct | `CAP_0_100(CAST(progress_pct AS DECIMAL(5,2)))` | Null → 0 | VR-03, CR-02 | Range 0–100 | Capping applied |
| STM-FP-005 | FACT_PROGRESS | progress_variance_pct | decimal(6,2) | DERIVED | - | - | `actual_progress_pct - planned_progress_pct` | Null-safe calc | CR-01 | Calculated check | Negative allowed |
| STM-FP-006 | FACT_PROGRESS | status_derived | string | DERIVED | - | - | `DERIVE_STATUS(...)` | Default `HLD` | DR-01 | Domain check | Same rule as DIM |
| STM-FP-007 | FACT_PROGRESS | project_health_status | string | DERIVED | - | - | `DERIVE_HEALTH(progress_variance_pct)` | Default `YELLOW` | SR-01 | Domain check | GREEN/YELLOW/RED |
| STM-FP-008 | FACT_PROGRESS | dt_created | timestamp | SYSTEM | - | - | `CURRENT_TIMESTAMP` | Not null | - | Not null | Load time |

---

# 6. STM — FACT_FINANCIAL (Optional)

### Target Table Metadata

| Item | Value |
|------|-------|
| Target Table | `FACT_FINANCIAL` |
| Layer | MART |
| Grain | 1 row per project per period |
| Keys | PK: (`project_id`, `period_yyyymm`) |
| Load Type | Incremental |
| Incremental Column | `period_yyyymm` |

---

## 6.1 Field Mapping — FACT_FINANCIAL

| Map ID | Target Table | Target Column | Target Data Type | Source System | Source Object | Source Column | Transform Logic | Default / Null Handling | Rule Ref | DQ Checks | Notes |
|-------|--------------|--------------|------------------|--------------|--------------|--------------|-----------------|-------------------------|----------|----------|------|
| STM-FF-001 | FACT_FINANCIAL | project_id | string | Finance | finance | project_id | `TRIM(project_id)` | Reject if null | VR-01 | RI | - |
| STM-FF-002 | FACT_FINANCIAL | period_yyyymm | string | Finance | finance | period | `FORMAT_YYYYMM(period)` | Reject if invalid | VR-02 | Format check | Example: 202602 |
| STM-FF-003 | FACT_FINANCIAL | budget_amount_idr | decimal(18,2) | Finance | finance | budget | `CAST(budget AS DECIMAL(18,2))` | Null → 0 | FR-01 | Non-negative | Currency standard |
| STM-FF-004 | FACT_FINANCIAL | actual_amount_idr | decimal(18,2) | Finance | finance | actual | `CAST(actual AS DECIMAL(18,2))` | Null → 0 | FR-01 | Non-negative | - |
| STM-FF-005 | FACT_FINANCIAL | forecast_amount_idr | decimal(18,2) | Finance | finance | forecast | `CAST(forecast AS DECIMAL(18,2))` | Null → 0 | FR-01, FR-02 | Non-negative, >= actual | - |

---

## 7. Incremental Load Strategy

### 7.1 Standard Incremental Pattern
- Identify incremental watermark (`dt_updated`, `dt_report`, or `period_yyyymm`)
- Extract only changed/new rows since last successful run
- Upsert into target layer:
  - `DIM` tables: SCD Type 1 or Type 2
  - `FACT` tables: Upsert by primary key (idempotent)

### 7.2 Idempotency Requirements
- Re-running the same batch should yield the same result
- Each target table must have a deterministic primary key

---

## 8. Error Handling & Reconciliation

| Scenario | Handling |
|---------|----------|
| Missing mandatory key | Reject + log to error table |
| Invalid date | Reject or nullify (configurable) |
| Domain mismatch | Flag for review |
| Duplicate keys | Deduplicate by latest timestamp |
| Reconciliation | Row counts & totals checks per batch |

---

## 9. Change Log

| Version | Date | Changes |
|--------|------|---------|
| 1.0 | YYYY-MM-DD | Initial STM template |
