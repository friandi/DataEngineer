# Entity Relationship Diagram (ERD) – Outline
## PMIS Data Platform

---

## 1. Purpose

This document defines the **conceptual and logical data model** for the PMIS Data Platform.  
The ERD ensures:
- Clear data grain definition
- Proper entity relationships
- Referential integrity across analytics datasets
- Alignment with FSD, STM, and Business Rules

---

## 2. Modeling Approach

- Modeling style: **Star Schema**
- Focus: **Analytical / Reporting Use Case**
- Separation between:
  - Dimension tables (descriptive)
  - Fact tables (measures / metrics)

---

## 3. Entity Overview

### 3.1 Dimension Entities

#### 3.1.1 DIM_PROJECT
- **Primary Key**: `project_id`
- **Grain**: 1 row per project
- **Description**: Master reference for all projects

**Key Attributes**
- project_id
- project_name
- company_code
- location / location_code
- dt_start
- dt_end_target
- project_status
- dt_created
- dt_updated

---

#### 3.1.2 DIM_COMPANY
- **Primary Key**: `company_code`
- **Grain**: 1 row per company
- **Description**: Reference for company / subsidiary hierarchy

**Key Attributes**
- company_code
- company_name
- parent_company_code
- company_type
- is_active

---

#### 3.1.3 DIM_LOCATION *(Optional)*
- **Primary Key**: `location_code`
- **Grain**: 1 row per standardized location
- **Description**: Location normalization reference

---

#### 3.1.4 DIM_DATE
- **Primary Key**: `date_key` (YYYYMMDD)
- **Grain**: 1 row per calendar date
- **Description**: Date dimension for reporting flexibility

**Key Attributes**
- date_key
- date
- year
- quarter
- month
- month_name
- week
- day_name

---

### 3.2 Fact Entities

#### 3.2.1 FACT_PROGRESS
- **Primary Key**: (`project_id`, `date_key`)
- **Grain**: 1 row per project per reporting date
- **Description**: Planned vs actual project progress metrics

**Measures**
- planned_progress_pct
- actual_progress_pct
- progress_variance_pct
- project_health_status

---

#### 3.2.2 FACT_FINANCIAL *(Optional / Phase 2)*
- **Primary Key**: (`project_id`, `period_yyyymm`)
- **Grain**: 1 row per project per period
- **Description**: Financial metrics for budget, actual, and forecast

**Measures**
- budget_amount_idr
- actual_amount_idr
- forecast_amount_idr
- variance_amount_idr

---

## 4. Relationships & Cardinality

| Parent Entity | Child Entity | Cardinality | Relationship |
|--------------|-------------|-------------|--------------|
| DIM_COMPANY | DIM_PROJECT | 1 : N | One company owns many projects |
| DIM_PROJECT | FACT_PROGRESS | 1 : N | One project has many progress records |
| DIM_DATE | FACT_PROGRESS | 1 : N | One date maps to many progress rows |
| DIM_PROJECT | FACT_FINANCIAL | 1 : N | One project has many financial periods |
| DIM_LOCATION | DIM_PROJECT | 1 : N | One location maps to many projects |

---

## 5. Grain Summary (Critical)

| Table | Grain Definition |
|-----|-----------------|
| DIM_PROJECT | 1 row per project |
| FACT_PROGRESS | 1 row per project per report date |
| FACT_FINANCIAL | 1 row per project per period |

---

## 6. Design Notes

- All fact tables must reference **DIM_PROJECT**
- Facts must be **idempotent** (safe to reload)
- Historical tracking may be applied using SCD (optional)
- No business logic embedded in BI layer

---

## 7. Related Documents

- FSD.md
- data_dictionary.md
- business_rules.md
- source_to_target_mapping.md

---

## 8. Revision History

| Version | Date | Description |
|--------|------|-------------|
| 1.0 | YYYY-MM-DD | Initial ERD outline |
