# Implementation Plan: Workout Analytics Views & BigQuery Enhancements

**Branch**: `002-workout-analytics-views` | **Date**: 2025-11-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-workout-analytics-views/spec.md`

## Summary

This feature adds comprehensive workout analytics visualization to the Streamlit application, enabling users to track training frequency across different time periods and view exercise performance trends. The implementation includes: (1) uploading exercise mapping configuration to BigQuery as a reference table, (2) creating and maintaining BigQuery views for pre-computed analytics, (3) building a new Analytics page with tabbed interfaces for summary metrics and detailed visualizations, (4) implementing rest day analysis by muscle groups and exercises across multiple time periods, and (5) creating an interactive exercise performance dashboard with configurable KPIs and visualization options.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Streamlit 1.28+, pandas 2.0+, google-cloud-bigquery 3.11+, plotly 5.0+ (for visualizations), pyyaml 6.0+  
**Storage**: Google BigQuery (existing: `workouts` table; new: `exercise_muscle_mapping` table, analytical views)  
**Testing**: pytest (existing test framework)  
**Target Platform**: Web application (Streamlit Cloud or local deployment)  
**Project Type**: Single web application (Python/Streamlit frontend + BigQuery backend)  
**Performance Goals**: Page load <2s for analytics, metric calculations <1s, BigQuery view refresh <30s post-upload  
**Constraints**: BigQuery query costs minimized via materialized views, UI responsive with datasets up to 50k workout records  
**Scale/Scope**: Personal workout tracking (single user), 100-10k workout records, 50-200 unique exercises

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASSED (No constitution constraints defined)

The project constitution file is a template with no specific constraints. This feature:
- Extends existing Streamlit application architecture (no architectural changes)
- Uses established patterns (modules/, config/, existing BigQuery integration)
- Adds new page and visualizations (additive feature, no breaking changes)
- Follows existing code structure and conventions

**No violations or complexity justifications required.**

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
gym-streamlit-dashboard/
├── app.py                          # Main Streamlit app (ADD: Analytics page)
├── requirements.yaml               # Dependencies (ADD: plotly)
├── config/
│   ├── csv_schema.yaml            # Existing CSV schema
│   ├── exercise_mapping.yaml      # Existing exercise mappings
│   └── bigquery_config.yaml       # Existing BQ config (UPDATE: add views config)
├── modules/
│   ├── __init__.py
│   ├── config_loader.py           # Existing config loader
│   ├── csv_parser.py              # Existing CSV parser
│   ├── data_enrichment.py         # Existing data enrichment
│   ├── bigquery_uploader.py       # UPDATE: add mapping table upload
│   ├── analytics.py               # NEW: Analytics calculations
│   ├── bigquery_views.py          # NEW: BigQuery view management
│   └── visualizations.py          # NEW: Plotly chart generators
├── pages/                          # NEW: Streamlit multi-page structure
│   └── Analytics.py               # NEW: Analytics dashboard page
├── sql/                            # NEW: BigQuery view definitions
│   ├── views/
│   │   ├── workout_frequency_by_muscle_group.sql
│   │   ├── workout_frequency_by_exercise.sql
│   │   ├── rest_days_analysis.sql
│   │   └── exercise_performance_metrics.sql
│   └── README.md                  # SQL documentation
└── tests/
    ├── test_analytics.py          # NEW: Analytics tests
    ├── test_bigquery_views.py     # NEW: View management tests
    └── test_visualizations.py     # NEW: Visualization tests
```

**Structure Decision**: Using Streamlit's native multi-page app structure. The `pages/` directory enables automatic page routing. All analytical logic is modularized in `modules/`, with SQL view definitions maintained separately in `sql/views/` for version control and clarity.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitution violations

---

## Phase 0: Research & Technology Decisions ✅

**Status**: COMPLETED  
**Output**: [research.md](./research.md)

**Key Decisions Made**:
1. **View Management**: Use CREATE OR REPLACE VIEW via BigQuery Python client (simple, idempotent)
2. **Page Navigation**: Streamlit native multi-page apps with pages/ directory
3. **Visualizations**: Plotly for interactive charts with hover, zoom, pan capabilities
4. **Rest Days Calculation**: Pairwise consecutive workout gaps averaging
5. **Time Filtering**: BigQuery WHERE clauses for efficient query pruning
6. **1RM Formula**: Brzycki formula for estimated one-rep max calculations
7. **View Refresh Timing**: Immediate after upload, non-blocking on failure

**Dependencies Added**: plotly>=5.0.0

---

## Phase 1: Data Model & Contracts ✅

**Status**: COMPLETED  
**Outputs**: 
- [data-model.md](./data-model.md)
- [contracts/inputs.md](./contracts/inputs.md)
- [contracts/outputs.md](./contracts/outputs.md)
- [quickstart.md](./quickstart.md)

**Data Structures Defined**:
1. **BigQuery Table**: `exercise_muscle_mapping` (reference table from YAML config)
2. **BigQuery Views**: 
   - `workout_frequency_by_muscle_group` - rest days by muscle groups
   - `workout_frequency_by_exercise` - rest days by exercises
   - `exercise_performance_metrics` - KPIs over time with trend calculations
3. **Python Models**: RestDaysMetric, ExercisePerformance, AnalyticsSummary

**API Contracts**:
- Input: Time period filters, category selection, exercise/KPI/x-axis selection
- Output: DataFrames, Plotly charts, BigQuery view results, upload status messages

---

## Phase 2: Implementation Tasks

**Status**: NOT STARTED (use `/speckit.tasks` command)  
**Next Step**: Run `/speckit.tasks` to generate detailed implementation checklist

**Estimated Timeline**: 12-14 hours total
- BigQuery schema extensions: 1-2 hours
- View management module: 2 hours  
- Analytics module: 3 hours
- Visualization module: 2 hours
- Analytics page UI: 3-4 hours
- Integration & testing: 1 hour

**Priority Order**:
1. **P1 - Core Analytics** (User Stories 1-3): Summary view with rest days analysis
2. **P2 - Visualizations** (User Story extension): Exercise performance charts
3. **P3 - BigQuery Infrastructure** (User Stories 4-5): Mapping table + views automation

---

## Post-Design Constitution Re-Check

**Status**: ✅ PASSED

Design maintains compliance with all principles:
- No architectural changes to existing system
- Follows established module patterns
- Additive features only (no breaking changes)
- SQL views stored as version-controlled files
- Clear separation of concerns (analytics, views, visualizations)

**No new complexity introduced.**

---

## Implementation Readiness

✅ All research completed - no outstanding clarifications  
✅ Data model designed and documented  
✅ Input/output contracts defined  
✅ Quickstart guide created with step-by-step implementation  
✅ Constitution compliance verified  

**Ready to proceed with implementation.**

---

## References

- **Feature Spec**: [spec.md](./spec.md)
- **Research Decisions**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Contracts**: [contracts/](./contracts/)
- **Quickstart**: [quickstart.md](./quickstart.md)
- **Original Application Plan**: [../001-gcp-terraform-iac/plan.md](../001-gcp-terraform-iac/plan.md)
