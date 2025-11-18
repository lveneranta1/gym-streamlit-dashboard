# Task List: Workout Analytics Views & BigQuery Enhancements

**Feature**: 002-workout-analytics-views  
**Branch**: `002-workout-analytics-views`  
**Created**: 2025-11-18

## Overview

This task list organizes implementation by user story to enable independent development, testing, and delivery. Each user story phase is a complete, testable increment.

---

## Phase 1: Setup (Project Initialization)

### Setup Tasks

- [X] T001 Install plotly dependency in requirements.yaml
- [X] T002 Create sql/views/ directory structure per plan.md
- [X] T003 [P] Create tests/ structure for new test files (test_analytics.py, test_bigquery_views.py, test_visualizations.py)
- [X] T004 Verify BigQuery connection and permissions for view creation

**Acceptance**: All dependencies installed, directory structure created, BigQuery permissions verified

---

## Phase 2: Foundational (Blocking Prerequisites)

### BigQuery Infrastructure Tasks

- [X] T005 [P] Create sql/views/workout_frequency_by_muscle_group.sql with full SQL definition from data-model.md
- [X] T006 [P] Create sql/views/workout_frequency_by_exercise.sql with full SQL definition from data-model.md
- [X] T007 [P] Create sql/views/exercise_performance_metrics.sql with full SQL definition from data-model.md
- [X] T008 Update config/bigquery_config.yaml with views section per contracts/inputs.md
- [X] T009 Implement BigQueryViewManager class in modules/bigquery_views.py with load_view_sql(), create_or_update_view(), refresh_all_views()
- [X] T010 Extend BigQueryUploader.upload_exercise_mapping() in modules/bigquery_uploader.py to parse YAML and upload to exercise_muscle_mapping table
- [X] T011 Implement _parse_exercise_mapping() helper in modules/bigquery_uploader.py to convert YAML to DataFrame
- [X] T012 Write unit tests for BigQueryViewManager in tests/test_bigquery_views.py
- [ ] T013 Write unit tests for upload_exercise_mapping in tests/test_bigquery_uploader.py

**Independent Test**: Run tests and manually verify views can be created in BigQuery, exercise_muscle_mapping table schema is correct

**Acceptance**: All 3 SQL view files created, BigQueryViewManager working, exercise mapping upload functional, tests passing

---

## Phase 3: User Story 1 - View Workout Frequency Analytics (P1)

**Goal**: Display overall average days between workouts

### US1 Analytics Module Tasks

- [X] T014 [P] [US1] Create modules/analytics.py with TimePeriod type and get_time_filter() function
- [X] T015 [P] [US1] Implement get_rest_days_by_muscle_group() in modules/analytics.py querying workout_frequency_by_muscle_group view
- [X] T016 [P] [US1] Implement get_rest_days_by_exercise() in modules/analytics.py querying workout_frequency_by_exercise view
- [X] T017 [US1] Write unit tests for analytics functions in tests/test_analytics.py

### US1 Analytics Page Tasks

- [X] T018 [US1] Create pages/Analytics.py with page config and BigQuery client initialization
- [X] T019 [US1] Add page header, title, and time period selector (all/last_7/last_14/last_30/last_90) in pages/Analytics.py
- [X] T020 [US1] Create Summary tab with rest days table display in pages/Analytics.py
- [X] T021 [US1] Add category type selector (muscle_group vs exercise) in pages/Analytics.py Summary tab
- [X] T022 [US1] Implement load_rest_days() cached function calling analytics module in pages/Analytics.py
- [X] T023 [US1] Add overall metrics cards (avg rest days, most trained, needs attention) in pages/Analytics.py Summary tab
- [X] T024 [US1] Add empty state handling ("No data available") in pages/Analytics.py
- [X] T025 [US1] Style and format the Summary tab table with proper column labels and sorting

**Independent Test**: Navigate to Analytics page, select time periods, switch between muscle groups and exercises, verify metrics display correctly

**Acceptance**: Analytics page accessible, time period filtering works, category switching works, metrics accurate, empty states handled

---

## Phase 4: User Story 2 - Filter Analytics by Muscle Group (P2)

**Goal**: Analyze training frequency per muscle group

### US2 Integration Tasks

- [ ] T026 [P] [US2] Add muscle group filtering logic to get_rest_days_by_muscle_group() in modules/analytics.py
- [ ] T027 [US2] Update Summary tab to properly filter and display muscle group Level 1 and Level 2 in pages/Analytics.py
- [ ] T028 [US2] Add muscle group selector/filter UI component in pages/Analytics.py
- [ ] T029 [US2] Implement caching for muscle group queries with proper cache keys in pages/Analytics.py
- [ ] T030 [US2] Add "No workouts for this muscle group" message handling in pages/Analytics.py

**Independent Test**: Select different muscle groups, verify average rest days update, confirm all muscle groups are available

**Acceptance**: Muscle group filtering fully functional, metrics update correctly per selection, proper empty state for unmapped groups

---

## Phase 5: User Story 3 - Filter Analytics by Exercise Name (P2)

**Goal**: Track frequency for specific exercises

### US3 Exercise Filtering Tasks

- [ ] T031 [P] [US3] Add exercise name filtering logic to get_rest_days_by_exercise() in modules/analytics.py
- [ ] T032 [US3] Implement get_available_exercises() query function in modules/analytics.py
- [ ] T033 [US3] Add exercise selector populated from BigQuery in pages/Analytics.py Summary tab
- [ ] T034 [US3] Update Summary tab to display exercise-specific rest days when exercise filter active
- [ ] T035 [US3] Add "Not enough data for this exercise" handling (< 2 workouts) in pages/Analytics.py
- [ ] T036 [US3] Sort exercise dropdown alphabetically in pages/Analytics.py

**Independent Test**: Select different exercises from dropdown, verify rest days calculations are exercise-specific, test with single-workout exercise

**Acceptance**: Exercise dropdown populated, filtering works, insufficient data handled gracefully, alphabetical sorting applied

---

## Phase 6: Exercise Performance Visualization (P2 Extension)

**Goal**: Interactive charts showing exercise performance over time

### Visualization Module Tasks

- [X] T037 [P] Create modules/visualizations.py with KPI and XAxis type definitions
- [X] T038 [P] Implement create_exercise_performance_chart() in modules/visualizations.py with bar chart generation
- [X] T039 Extend create_exercise_performance_chart() to add trend line overlay when show_trend=True in modules/visualizations.py
- [X] T040 Add KPI mapping logic (1rm/total_volume/max_weight) in modules/visualizations.py
- [X] T041 Add x-axis mapping logic (index/week/month/year) in modules/visualizations.py
- [X] T042 Implement proper chart layout with dual y-axes in modules/visualizations.py
- [X] T043 Add hover templates for interactivity in modules/visualizations.py
- [X] T044 Write unit tests for visualization functions in tests/test_visualizations.py

### Analytics Module Extension

- [X] T045 [P] Implement get_exercise_performance() in modules/analytics.py querying exercise_performance_metrics view
- [X] T046 Add parameterized query with exercise_name filter in modules/analytics.py get_exercise_performance()
- [X] T047 Add time period filtering to exercise performance queries in modules/analytics.py

### UI Implementation

- [X] T048 Create "Exercise Performance" tab in pages/Analytics.py
- [X] T049 Add exercise selector (dropdown) in Exercise Performance tab
- [X] T050 Add KPI selector (1RM/Total Volume/Max Weight) in Exercise Performance tab
- [X] T051 Add x-axis selector (Index/Week/Month/Year) in Exercise Performance tab
- [X] T052 Add "Show % Change" checkbox in Exercise Performance tab
- [X] T053 Implement load_performance() cached function in pages/Analytics.py
- [X] T054 Call create_exercise_performance_chart() and display with st.plotly_chart() in pages/Analytics.py
- [X] T055 Add empty state handling for exercises with no data in Exercise Performance tab
- [X] T056 Add chart title and labels formatting in Exercise Performance tab

**Independent Test**: Select exercise, change KPI, change x-axis, toggle trend line, verify chart updates correctly and interactivity works

**Acceptance**: Chart displays correctly, all filters work, trend line toggles properly, hover shows details, empty states handled

---

## Phase 7: User Story 4 - Exercise Mapping in BigQuery (P3)

**Goal**: Exercise mapping table automatically uploaded to BigQuery

### US4 Integration Tasks

- [X] T057 [US4] Integrate upload_exercise_mapping() call into main upload workflow in app.py
- [X] T058 [US4] Add exercise mapping table creation to upload success flow in app.py
- [X] T059 [US4] Update upload success message to show mapping table upload status in app.py
- [X] T060 [US4] Add error handling for mapping table upload failures in app.py (non-blocking)
- [X] T061 [US4] Add logging for exercise mapping upload in modules/bigquery_uploader.py

**Independent Test**: Upload workout CSV, verify exercise_muscle_mapping table created in BigQuery with correct schema and data

**Acceptance**: Exercise mapping uploads successfully, proper logging, errors don't block main upload, success message accurate

---

## Phase 8: User Story 5 - Automated BigQuery Views (P3)

**Goal**: Views automatically refresh after data upload

### US5 View Automation Tasks

- [X] T062 [US5] Integrate BigQueryViewManager into upload workflow in app.py
- [X] T063 [US5] Call refresh_all_views() after successful workout data upload in app.py
- [X] T064 [US5] Add view names loading from config/bigquery_config.yaml in app.py
- [X] T065 [US5] Update upload success message to show view refresh status in app.py
- [X] T066 [US5] Add graceful error handling for view refresh failures (log warning, don't fail upload) in app.py
- [ ] T067 [US5] Add retry logic for view refresh failures in modules/bigquery_views.py

**Independent Test**: Upload data, verify all 3 views are refreshed in BigQuery, test view refresh failure doesn't break upload

**Acceptance**: Views refresh automatically post-upload, failures logged but don't block upload, success message shows refresh status

---

## Phase 9: Polish & Cross-Cutting Concerns

### Final Integration Tasks

- [X] T068 [P] Update requirements.yaml with final dependency versions
- [X] T069 Add comprehensive error messages for BigQuery connection failures in pages/Analytics.py
- [X] T070 Add loading spinners for long-running queries in pages/Analytics.py
- [X] T071 Optimize BigQuery query caching in pages/Analytics.py (set proper TTL)
- [ ] T072 Add user instructions/help text in Analytics page for first-time users
- [X] T073 Format numbers and dates consistently across all views (1 decimal for floats, YYYY-MM-DD for dates)
- [X] T074 Add SQL view documentation in sql/README.md

### Testing & Validation Tasks

- [ ] T075 Run integration test: Upload CSV → Verify all views created → Navigate to Analytics → Verify data displays
- [ ] T076 Test with empty BigQuery database (no data scenario)
- [ ] T077 Test with single workout (insufficient data scenario)
- [ ] T078 Test all time period filters (7/14/30/90 days, all-time)
- [ ] T079 Test all KPI options (1RM, volume, max weight)
- [ ] T080 Test all x-axis options (index, week, month, year)
- [ ] T081 Verify chart interactivity (hover, zoom, pan)
- [ ] T082 Test category switching (muscle group ↔ exercise) performance
- [ ] T083 Load test with large dataset (10k+ workout records)
- [ ] T084 Verify BigQuery query costs are reasonable (check billing)

**Independent Test**: Run full test suite, perform manual testing checklist, verify performance targets met

**Acceptance**: All tests passing, performance acceptable (<2s page load, <1s metric calculations), no regressions

---

## Dependencies

### Story Completion Order

```
Setup (Phase 1)
  ↓
Foundational (Phase 2) ← MUST complete before user stories
  ↓
├─→ US1 (Phase 3) ← Can start immediately after Phase 2
│   ├─→ US2 (Phase 4) ← Depends on US1
│   └─→ US3 (Phase 5) ← Depends on US1
│
├─→ Visualizations (Phase 6) ← Can start after Phase 2, independent of US1-3
│
├─→ US4 (Phase 7) ← Can start after Phase 2, independent of other stories
│
└─→ US5 (Phase 8) ← Depends on Phase 2, can run parallel to UI work

Polish (Phase 9) ← After all user stories complete
```

### Parallel Execution Opportunities

**Can work simultaneously**:
- Phase 2 tasks (T005-T007 are independent SQL files)
- Phase 3 tasks (T014-T016 are independent analytics functions)
- Phase 6 tasks (T037-T044 visualization module independent of analytics page)
- Phase 7 + Phase 8 (both are backend integration tasks)

**Sequential dependencies**:
- Phase 2 → Phase 3 (views must exist before analytics queries)
- Phase 3 → Phase 4, Phase 5 (US1 Summary tab must exist before adding filters)
- All phases → Phase 9 (polish requires complete features)

---

## Implementation Strategy

### MVP Scope (Recommended First Delivery)

**Include**:
- Phase 1: Setup ✅
- Phase 2: Foundational ✅
- Phase 3: User Story 1 (basic analytics) ✅
- Phase 7: Exercise mapping upload ✅
- Phase 8: View automation ✅

**Delivers**: Working analytics page with overall metrics, automated backend infrastructure

**Defer to v2**:
- Phase 4: Muscle group filtering
- Phase 5: Exercise filtering  
- Phase 6: Performance visualizations

### Incremental Delivery Plan

**Sprint 1 (MVP)**: T001-T025, T057-T067 → Basic analytics + automation  
**Sprint 2 (Filtering)**: T026-T036 → Muscle group and exercise filters  
**Sprint 3 (Visualizations)**: T037-T056 → Performance charts  
**Sprint 4 (Polish)**: T068-T084 → Testing, optimization, documentation

---

## Task Format Reference

- `[ ]` = Not started
- `[P]` = Parallelizable (can work independently)
- `[USX]` = User Story X (1-5)
- Task ID = Sequential (T001, T002, ...)

---

## Progress Tracking

**Setup**: 4/4 tasks (100%) ✅  
**Foundational**: 8/9 tasks (89%)  
**US1 - Analytics**: 12/12 tasks (100%) ✅  
**US2 - Muscle Groups**: 0/5 tasks (0%)  
**US3 - Exercises**: 0/6 tasks (0%)  
**Visualizations**: 20/20 tasks (100%) ✅  
**US4 - Mapping Table**: 5/5 tasks (100%) ✅  
**US5 - View Automation**: 5/6 tasks (83%)  
**Polish**: 6/17 tasks (35%)  

**Total**: 60/84 tasks (71%)

---

## Time Estimates

| Phase | Tasks | Hours | Priority |
|-------|-------|-------|----------|
| Setup | T001-T004 | 0.5 | P0 |
| Foundational | T005-T013 | 2-3 | P0 |
| US1 (Analytics) | T014-T025 | 4-5 | P1 |
| US2 (Muscle Groups) | T026-T030 | 1 | P2 |
| US3 (Exercises) | T031-T036 | 1 | P2 |
| Visualizations | T037-T056 | 4-5 | P2 |
| US4 (Mapping) | T057-T061 | 1 | P3 |
| US5 (Views) | T062-T067 | 1 | P3 |
| Polish | T068-T084 | 2-3 | P4 |
| **Total** | **84 tasks** | **16-21h** | |

---

## Success Criteria

**MVP Complete When**:
- ✅ Analytics page accessible from navigation
- ✅ Overall rest days displayed
- ✅ Time period filtering works
- ✅ Exercise mapping table uploads
- ✅ Views refresh automatically
- ✅ All MVP tests passing

**Feature Complete When**:
- ✅ All 84 tasks completed
- ✅ All 5 user stories implemented
- ✅ All acceptance criteria met
- ✅ Performance targets achieved
- ✅ Documentation complete

---

## Next Actions

1. **Review this task list** with team/stakeholders
2. **Start with MVP scope** (Phases 1-3, 7-8)
3. **Create feature branch** (already on 002-workout-analytics-views)
4. **Begin Phase 1** (T001-T004) - Setup tasks
5. **Track progress** by updating checkboxes as tasks complete
