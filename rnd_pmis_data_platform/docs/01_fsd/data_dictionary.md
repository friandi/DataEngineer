# Data Dictionary
## PMIS Data Platform

---

### Document Information

| Item | Description |
|-----|-------------|
| Document Name | Data Dictionary |
| System Name | PMIS Data Platform |
| Version | 1.0 |
| Status | Draft |
| Classification | Public / Reference |
| Owner | Data Engineering |
| Last Updated | YYYY-MM-DD |

---

## 1. Overview

This Data Dictionary defines **data elements**, **business meanings**, **rules**, and **technical metadata** used in the PMIS Data Platform.  
It supports:
- Consistent interpretation of metrics/fields
- ETL/ELT development
- Data quality validation
- Governance and auditability

---

## 2. Naming Conventions

### 2.1 Table Naming
- `STG_` : staging/raw standardized
- `INT_` : intermediate/conformed
- `MART_`: analytics-ready marts
- `DIM_` : dimension tables
- `FACT_`: fact tables

### 2.2 Column Naming
- Use `snake_case`
- Prefix dates with `dt_` (e.g., `dt_created`, `dt_updated`)
- Prefix boolean with `is_` (e.g., `is_active`)
- Use clear units for numeric fields (e.g., `_pct`, `_amount`, `_qty`)

---

## 3. Domain / Reference Lists

> Fill these for controlled values to prevent inconsistent inputs.

### 3.1 Project Status Codes

| Code | Name | Definition |
|------|------|------------|
| PLN | Planned | Project is approved but not started |
| OGN | Ongoing | Project is in execution |
| CMP | Completed | Project is finished and accepted |
| HLD | On Hold | Project is paused |

### 3.2 Measurement Units

| Unit | Meaning |
|------|---------|
| pct | Percentage (0–100) |
| idr | Indonesian Rupiah |
| qty | Quantity (unitless count) |

---

## 4. Data Dictionary Tables

> Use one section per dataset/table.  
> Recommended: start from `DIM_PROJECT` and a primary `FACT_PROGRESS` or `FACT_FINANCIAL`.

---

# 4.1 DIM_PROJECT

### Table Metadata

| Item | Value |
|------|-------|
| Layer | MART / DIM |
| Table Name | `DIM_PROJECT` |
| Grain | 1 row per project |
| Primary Key | `project_id` |
| Source(s) | Project Master / Contract / Planning |
| Load Type | Incremental / SCD Type 2 (optional) |
| Refresh Frequency | Daily |
| Retention | N years |
| Owner | Data Engineering |

### Columns

| Column Name | Data Type | Nullable | Key Type | Business Definition | Source Field | Transformation / Logic | Allowed Values / Domain | Example | DQ Rules | Sensitivity |
|------------|-----------|----------|---------|---------------------|-------------|------------------------|-------------------------|---------|----------|-------------|
| project_id | string | No | PK | Unique project identifier | `project_master.project_id` | Direct mapping | - | `PRJ-001` | Not null, unique | Internal |
| project_name | string | No | - | Official project name | `project_master.project_name` | Trim, normalize spaces | - | `Overhaul Unit A` | Not null | Internal |
| company_code | string | Yes | FK | Company / subsidiary code | `company_master.company_code` | Direct mapping | Domain: Company | `CMP01` | Must exist in DIM_COMPANY | Internal |
| location | string | Yes | - | Project site location | `project_master.location` | Standardize naming | Domain: Location | `Gresik` | Valid domain | Internal |
| dt_start | date | Yes | - | Project start date | `contract.start_date` | Cast to date | - | `2026-01-10` | Valid date | Internal |
| dt_end_target | date | Yes | - | Target end date | `plan.target_end_date` | Cast to date | - | `2026-12-31` | dt_end_target >= dt_start | Internal |
| project_status | string | Yes | - | High-level project status | Derived | Rule-based derivation | PLN/OGN/CMP/HLD | `OGN` | Must be in domain | Internal |
| dt_created | timestamp | No | - | Record creation timestamp | system | Load timestamp | - | `2026-02-02 10:00:00` | Not null | Internal |
| dt_updated | timestamp | No | - | Record update timestamp | system | Load timestamp | - | `2026-02-02 10:00:00` | Not null | Internal |

---

# 4.2 FACT_PROGRESS

### Table Metadata

| Item | Value |
|------|-------|
| Layer | MART / FACT |
| Table Name | `FACT_PROGRESS` |
| Grain | 1 row per project per reporting date (or per week/month) |
| Primary Key | `project_id`, `dt_report` |
| Foreign Keys | `project_id` → DIM_PROJECT |
| Source(s) | Progress reports / Planning schedule |
| Load Type | Incremental |
| Refresh Frequency | Daily |
| Owner | Data Engineering |

### Columns

| Column Name | Data Type | Nullable | Key Type | Business Definition | Source Field | Transformation / Logic | Allowed Values / Domain | Example | DQ Rules | Sensitivity |
|------------|-----------|----------|---------|---------------------|-------------|------------------------|-------------------------|---------|----------|-------------|
| project_id | string | No | FK | Project identifier | `progress.project_id` | Direct mapping | - | `PRJ-001` | Must exist in DIM_PROJECT | Internal |
| dt_report | date | No | PK | Reporting date | `progress.report_date` | Cast to date | - | `2026-02-01` | Not null | Internal |
| planned_progress_pct | decimal(5,2) | Yes | - | Planned progress percentage | `plan.progress_pct` | Standardize to 0–100 | 0–100 | 45.50 | Between 0 and 100 | Internal |
| actual_progress_pct | decimal(5,2) | Yes | - | Actual progress percentage | `actual.progress_pct` | Standardize to 0–100 | 0–100 | 42.00 | Between 0 and 100 | Internal |
| progress_variance_pct | decimal(6,2) | Yes | - | Actual - Planned | Derived | `actual_progress_pct - planned_progress_pct` | -100–100 | -3.50 | Calculated correctly | Internal |
| status_derived | string | Yes | - | Status derived from progress and dates | Derived | Rule-based | PLN/OGN/CMP/HLD | `OGN` | Must be in domain | Internal |
| dt_created | timestamp | No | - | Record creation timestamp | system | Load timestamp | - | `2026-02-02 10:00:00` | Not null | Internal |

---

# 4.3 FACT_FINANCIAL (Optional)

### Table Metadata

| Item | Value |
|------|-------|
| Layer | MART / FACT |
| Table Name | `FACT_FINANCIAL` |
| Grain | 1 row per project per reporting period |
| Primary Key | `project_id`, `period_yyyymm` |
| Source(s) | Budget / Actual / Forecast |
| Load Type | Incremental |
| Refresh Frequency | Monthly / Weekly |
| Owner | Data Engineering |

### Columns (Template)

| Column Name | Data Type | Nullable | Key Type | Business Definition | Source Field | Transformation / Logic | Allowed Values / Domain | Example | DQ Rules | Sensitivity |
|------------|-----------|----------|---------|---------------------|-------------|------------------------|-------------------------|---------|----------|-------------|
| project_id | string | No | FK | Project identifier | - | - | - | `PRJ-001` | Must exist in DIM_PROJECT | Internal |
| period_yyyymm | string | No | PK | Reporting period (YYYYMM) | - | Format YYYYMM | `YYYYMM` | `202602` | Valid format | Internal |
| budget_amount_idr | decimal(18,2) | Yes | - | Approved budget amount | - | Currency standardization | >= 0 | 1000000000.00 | Non-negative | Confidential |
| actual_amount_idr | decimal(18,2) | Yes | - | Actual spend amount | - | Currency standardization | >= 0 | 350000000.00 | Non-negative | Confidential |
| forecast_amount_idr | decimal(18,2) | Yes | - | Forecast total cost | - | Currency standardization | >= 0 | 900000000.00 | Non-negative | Confidential |

---

## 5. Data Quality Rules Catalog

> Centralized rule list so rules can be referenced consistently across tables.

| Rule ID | Rule Name | Description | Severity | Applies To | Check Type |
|--------|-----------|-------------|----------|-----------|-----------|
| DQ-01 | Not Null Key | Primary/foreign keys must not be null | High | All tables | Completeness |
| DQ-02 | Valid Date | Date fields must be valid and parseable | High | Facts, Dims | Validity |
| DQ-03 | Domain Check | Categorical fields must match domain list | Medium | Status fields | Conformity |
| DQ-04 | Range Check | Percent fields must be 0–100 | High | Progress | Validity |
| DQ-05 | Referential Integrity | FK must exist in referenced DIM | High | Facts | Integrity |

---

## 6. Change Log

| Version | Date | Changes |
|--------|------|---------|
| 1.0 | YYYY-MM-DD | Initial draft template |
