# Business Rules
## PMIS Data Platform

---

### Document Information

| Item | Description |
|-----|-------------|
| Document Name | Business Rules |
| System Name | PMIS Data Platform |
| Version | 1.0 |
| Status | Draft |
| Classification | Public / Reference |
| Owner | Data Engineering |
| Last Updated | YYYY-MM-DD |

---

## 1. Overview

This document defines **business rules** applied within the PMIS Data Platform.  
Business rules govern **data validation**, **derivation**, **calculation**, and **classification** to ensure consistency and reliability across analytics and reporting.

Rules are designed to be:
- Deterministic
- Traceable
- Reusable
- Implementable in SQL, Python, or dbt

---

## 2. Rule Classification

| Category | Description |
|--------|-------------|
| VR | Validation Rule |
| DR | Derivation Rule |
| CR | Calculation Rule |
| SR | Status Rule |
| FR | Financial Rule |

---

## 3. Business Rule Catalog

> Each rule is uniquely identified and referenced across ETL, dbt models, and data quality checks.

---

# 3.1 Validation Rules (VR)

### VR-01 — Mandatory Project Identifier

| Attribute | Value |
|---------|------|
| Rule ID | VR-01 |
| Rule Name | Mandatory Project Identifier |
| Rule Type | Validation |
| Description | Every project-related record must have a valid project identifier |
| Applies To | All fact and dimension tables |
| Input Fields | `project_id` |
| Logic | `project_id IS NOT NULL` |
| Failure Handling | Reject record / log error |
| Severity | High |
| Owner | Data Engineering |

---

### VR-02 — Valid Date Format

| Attribute | Value |
|---------|------|
| Rule ID | VR-02 |
| Rule Name | Valid Date Format |
| Rule Type | Validation |
| Description | Date fields must be valid and parseable |
| Applies To | All date fields |
| Input Fields | `dt_*` |
| Logic | Date can be cast to DATE without error |
| Failure Handling | Reject record / default to NULL (configurable) |
| Severity | High |
| Owner | Data Engineering |

---

### VR-03 — Percentage Range Validation

| Attribute | Value |
|---------|------|
| Rule ID | VR-03 |
| Rule Name | Percentage Range Validation |
| Rule Type | Validation |
| Description | Percentage values must be between 0 and 100 |
| Applies To | Progress-related fields |
| Input Fields | `*_progress_pct` |
| Logic | `value BETWEEN 0 AND 100` |
| Failure Handling | Cap to boundary / reject record |
| Severity | High |
| Owner | Data Engineering |

---

# 3.2 Derivation Rules (DR)

### DR-01 — Project Status Derivation

| Attribute | Value |
|---------|------|
| Rule ID | DR-01 |
| Rule Name | Project Status Derivation |
| Rule Type | Derivation |
| Description | Derive project status based on progress and dates |
| Applies To | DIM_PROJECT, FACT_PROGRESS |
| Input Fields | `dt_start`, `dt_end_target`, `actual_progress_pct` |
| Logic | See logic table below |
| Output Field | `project_status` |
| Failure Handling | Default to `HLD` |
| Owner | Data Engineering |

**Derivation Logic**

| Condition | Derived Status |
|---------|----------------|
| `actual_progress_pct = 100` | `CMP` |
| `actual_progress_pct > 0 AND < 100` | `OGN` |
| `dt_start IS NOT NULL AND actual_progress_pct = 0` | `PLN` |
| Else | `HLD` |

---

# 3.3 Calculation Rules (CR)

### CR-01 — Progress Variance Calculation

| Attribute | Value |
|---------|------|
| Rule ID | CR-01 |
| Rule Name | Progress Variance |
| Rule Type | Calculation |
| Description | Calculate variance between actual and planned progress |
| Applies To | FACT_PROGRESS |
| Input Fields | `actual_progress_pct`, `planned_progress_pct` |
| Logic | `actual_progress_pct - planned_progress_pct` |
| Output Field | `progress_variance_pct` |
| Rounding | 2 decimal places |
| Severity | Medium |
| Owner | Data Engineering |

---

### CR-02 — Progress Capping

| Attribute | Value |
|---------|------|
| Rule ID | CR-02 |
| Rule Name | Progress Capping |
| Rule Type | Calculation |
| Description | Ensure progress does not exceed 100% |
| Applies To | FACT_PROGRESS |
| Input Fields | `actual_progress_pct` |
| Logic | `LEAST(actual_progress_pct, 100)` |
| Output Field | `actual_progress_pct` |
| Severity | High |
| Owner | Data Engineering |

---

# 3.4 Status Rules (SR)

### SR-01 — Overall Project Health Status

| Attribute | Value |
|---------|------|
| Rule ID | SR-01 |
| Rule Name | Overall Project Health |
| Rule Type | Status |
| Description | Determine project health based on variance thresholds |
| Applies To | FACT_PROGRESS |
| Input Fields | `progress_variance_pct` |
| Output Field | `project_health_status` |
| Logic | See threshold table |
| Owner | Data Engineering |

**Status Thresholds**

| Condition | Health Status |
|---------|---------------|
| `variance >= 0` | GREEN |
| `variance < 0 AND >= -5` | YELLOW |
| `variance < -5` | RED |

---

# 3.5 Financial Rules (FR)

### FR-01 — Budget Non-Negative Rule

| Attribute | Value |
|---------|------|
| Rule ID | FR-01 |
| Rule Name | Budget Non-Negative |
| Rule Type | Financial |
| Description | Financial amounts must not be negative |
| Applies To | FACT_FINANCIAL |
| Input Fields | `budget_amount_idr`, `actual_amount_idr`, `forecast_amount_idr` |
| Logic | `value >= 0` |
| Failure Handling | Reject record |
| Severity | High |
| Owner | Finance / Data Engineering |

---

### FR-02 — Forecast Consistency Rule

| Attribute | Value |
|---------|------|
| Rule ID | FR-02 |
| Rule Name | Forecast Consistency |
| Rule Type | Financial |
| Description | Forecast amount must be >= actual spend |
| Applies To | FACT_FINANCIAL |
| Input Fields | `actual_amount_idr`, `forecast_amount_idr` |
| Logic | `forecast_amount_idr >= actual_amount_idr` |
| Failure Handling | Flag record |
| Severity | Medium |
| Owner | Finance / Data Engineering |

---

## 4. Rule Traceability Matrix

| Rule ID | Target Table | Column(s) | Implementation Layer |
|--------|-------------|-----------|----------------------|
| VR-01 | All | project_id | Ingestion / Staging |
| VR-03 | FACT_PROGRESS | *_progress_pct | Transform |
| DR-01 | DIM_PROJECT | project_status | Transform |
| CR-01 | FACT_PROGRESS | progress_variance_pct | Transform |
| SR-01 | FACT_PROGRESS | project_health_status | Serving |
| FR-01 | FACT_FINANCIAL | amounts | Transform |

---

## 5. Change Log

| Version | Date | Description |
|--------|------|-------------|
| 1.0 | YYYY-MM-DD | Initial business rules definition |
