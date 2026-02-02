# System Context Diagram – Outline
## PMIS Data Platform

---

## 1. Purpose

This document describes the **system boundary** and **integration context** of the PMIS Data Platform, including:
- External source systems
- Internal platform components
- Downstream consumers
- High-level data flows

---

## 2. System Boundary

**PMIS Data Platform** is responsible for:
- Ingesting project-related data
- Transforming and validating data
- Storing analytics-ready datasets
- Serving data to reporting and analytics tools

---

## 3. Actors / Users

| Actor | Description |
|-----|-------------|
| Business Users | Consume dashboards and reports |
| Data Engineer | Develops and operates pipelines |
| Data Analyst | Performs analytics and ad-hoc queries |
| Auditor / Compliance | Reviews controls, lineage, and documentation |

---

## 4. External Systems

### 4.1 Source Systems (Upstream)

| System | Data Provided | Interface |
|------|--------------|-----------|
| Project Master System | Project reference data | DB / File / API |
| Planning System | Planned schedules & targets | File / API |
| Progress Reporting System | Actual progress updates | File / API |
| Finance System *(Optional)* | Budget, actual, forecast | DB / API |

---

### 4.2 Consumption Systems (Downstream)

| System | Purpose |
|------|---------|
| BI / Dashboard Tool | Visualization and KPI reporting |
| Analytics Tools | Ad-hoc analysis |
| Notification Channel *(Future)* | Alerts for DQ / pipeline status |

---

## 5. Internal Components (PMIS Data Platform)

1. **Ingestion Layer**
   - Data extraction
   - Schema validation
   - Landing zone

2. **Staging Layer (STG)**
   - Raw standardized data
   - Minimal transformation

3. **Transformation Layer (INT)**
   - Business rule application
   - Data conformance

4. **Warehouse / Mart Layer (MART)**
   - Facts and dimensions
   - Analytics-ready data

5. **Orchestration**
   - Workflow scheduling
   - Dependency management

6. **Data Quality & Logging**
   - Rule validation
   - Error logging
   - Audit trail

---

## 6. High-Level Data Flow


Orchestration controls all processing stages.
Source Systems
↓
Ingestion Layer
↓
Staging (STG)
↓
Transform (INT)
↓
Warehouse / Mart (MART)
↓
BI / Analytics
---

## 7. Non-Functional Considerations

- **Security**: Role-based access control
- **Compliance**: No client-identifying data
- **Reliability**: Restartable pipelines
- **Lineage**: STG → INT → MART traceability
- **Idempotency**: Safe reprocessing

---

## 8. Diagram Notes (for Visual Diagram)

When drawing the diagram:
- Place PMIS Data Platform at the center
- External systems on the left (sources)
- Consumers on the right
- Use directional arrows to show data flow
- Label flows with data type (Master, Progress, Financial)

---

## 9. Related Documents

- FSD.md
- ERD Outline
- Business Rules
- Source-to-Target Mapping

---

## 10. Revision History

| Version | Date | Description |
|--------|------|-------------|
| 1.0 | YYYY-MM-DD | Initial system context outline |
