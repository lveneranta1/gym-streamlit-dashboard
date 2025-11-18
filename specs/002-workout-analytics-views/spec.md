# Feature Specification: Workout Analytics Views & BigQuery Enhancements

**Feature Branch**: `002-workout-analytics-views`  
**Created**: 2025-11-18  
**Status**: Draft  
**Input**: User description: "implement new page to the streamlit application for summarization and visualization of the workout data. the page should contain different views using st.tabs to define multiple sub pages. user should be shown average number of days between workouts. user should be given possibility to choose between showing these numbers either using muscle groups or by exercise name. other improvements: upload the exercise mapping as a table to big query; implement SQL queries that create views on big query based on the source table; create pipeline that executes and updates the views in big query after data has been updated"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Workout Frequency Analytics (Priority: P1)

A user navigates to a new Analytics page in the Streamlit application where they can see average days between workouts. The user wants to understand their training consistency and identify whether they're training frequently enough.

**Why this priority**: This is the core value proposition - providing actionable insights about workout frequency. It directly answers the question "How often am I training?" which is fundamental to any workout tracking application.

**Independent Test**: Can be fully tested by navigating to the Analytics page and observing calculated average days between workouts displayed on screen, delivering immediate value without requiring any other features.

**Acceptance Scenarios**:

1. **Given** workout data exists in the database, **When** user navigates to the Analytics page, **Then** the page displays the average number of days between all workouts
2. **Given** user is on the Analytics page, **When** the page loads, **Then** the interface provides tabbed views for different analysis perspectives
3. **Given** insufficient workout data (less than 2 workouts), **When** user views Analytics page, **Then** system displays a message indicating more data is needed for analysis

---

### User Story 2 - Filter Analytics by Muscle Group (Priority: P2)

A user wants to analyze their training frequency for specific muscle groups (e.g., "How often do I train chest?" or "Am I training legs frequently enough?"). The user selects a muscle group filter and sees the average days between workouts targeting that specific muscle group.

**Why this priority**: Enables users to identify training imbalances and ensure adequate recovery time for specific muscle groups. This is critical for effective training program management.

**Independent Test**: Can be tested independently by selecting different muscle groups from a dropdown/selector and verifying that displayed metrics update to show muscle-group-specific frequency data.

**Acceptance Scenarios**:

1. **Given** user is on the Analytics page muscle group tab, **When** user selects a specific muscle group (e.g., "chest"), **Then** the display shows average days between workouts that include that muscle group
2. **Given** user has selected a muscle group filter, **When** no workouts exist for that muscle group, **Then** system displays a message indicating no data available for the selected muscle group
3. **Given** workout data with muscle group mappings, **When** user views muscle group analytics, **Then** all available muscle groups are presented as selectable options

---

### User Story 3 - Filter Analytics by Exercise Name (Priority: P2)

A user wants to track how frequently they perform specific exercises (e.g., "How often do I bench press?" or "When was the last time I did squats?"). The user selects an exercise from a list and sees the average days between performances of that specific exercise.

**Why this priority**: Helps users ensure exercise variety and adequate frequency for compound movements. This complements muscle group analysis by providing exercise-specific insights.

**Independent Test**: Can be tested by selecting different exercises from a dropdown/selector and verifying that displayed metrics update to show exercise-specific frequency data.

**Acceptance Scenarios**:

1. **Given** user is on the Analytics page exercise tab, **When** user selects a specific exercise (e.g., "Bench Press"), **Then** the display shows average days between performances of that exercise
2. **Given** user has selected an exercise filter, **When** fewer than 2 instances of that exercise exist, **Then** system displays a message indicating insufficient data
3. **Given** workout data with various exercises, **When** user views exercise analytics, **Then** all unique exercise names are presented as selectable options in alphabetical order

---

### User Story 4 - Exercise Mapping Available in BigQuery (Priority: P3)

The exercise-to-muscle-group mapping configuration is automatically uploaded to BigQuery as a dedicated table, enabling advanced query capabilities and ensuring the mapping data is available alongside workout data for comprehensive analytics.

**Why this priority**: Enables more sophisticated data analysis and reporting within BigQuery, supporting future analytics needs and data warehouse best practices. While valuable, it's not required for the primary user-facing analytics features.

**Independent Test**: Can be tested by verifying the exercise mapping table exists in BigQuery with all expected mapping data, independently of other features.

**Acceptance Scenarios**:

1. **Given** exercise mapping configuration exists, **When** data upload pipeline runs, **Then** exercise mapping data is uploaded to BigQuery as a separate table
2. **Given** exercise mapping table exists in BigQuery, **When** queried, **Then** table contains columns for exercise name, muscle group level 1, muscle group level 2, and compound flag
3. **Given** exercise mapping configuration is updated, **When** next data sync occurs, **Then** BigQuery exercise mapping table reflects the updated mappings

---

### User Story 5 - Automated BigQuery Views for Analytics (Priority: P3)

Predefined BigQuery views (SQL queries) are created to calculate common analytics metrics (e.g., workout frequency by muscle group, exercise frequency). These views are automatically updated whenever new workout data is uploaded.

**Why this priority**: Improves query performance and provides reusable analytics logic in BigQuery. This is valuable for advanced users and future integrations but not essential for the immediate Streamlit analytics page.

**Independent Test**: Can be tested by querying the BigQuery views and verifying they return correct aggregated metrics, independently of the Streamlit interface.

**Acceptance Scenarios**:

1. **Given** workout data exists in BigQuery, **When** BigQuery views are queried, **Then** views return pre-calculated analytics metrics (e.g., average days between workouts by muscle group)
2. **Given** new workout data is uploaded, **When** upload completes, **Then** pipeline automatically refreshes BigQuery views with updated data
3. **Given** BigQuery views exist, **When** queried from any client, **Then** views provide consistent results matching raw data calculations

---

### Edge Cases

- What happens when a user has only performed an exercise once? System displays "Not enough data" with minimum requirement message (need at least 2 occurrences to calculate days between)
- How does the system handle workouts with multiple muscle groups? Each muscle group is counted separately in muscle group frequency analysis
- What if exercise names have inconsistent casing or spelling variations? System displays exact exercise names as entered; assumes data cleaning happens during upload (outside scope of this feature)
- How are workouts on the same day handled in frequency calculations? Multiple workouts on the same day count as separate data points but don't contribute to "days between" calculations (0 days between is excluded from averages)
- What happens if BigQuery views fail to update after data upload? Pipeline logs the error and retries; Streamlit application continues using existing view data until successful update

## Requirements *(mandatory)*

### Functional Requirements

#### Analytics Page Requirements

- **FR-001**: System MUST provide a new dedicated Analytics page accessible from the Streamlit navigation menu
- **FR-002**: Analytics page MUST use tabbed interface to organize different analysis views (overview, muscle groups, exercises)
- **FR-003**: System MUST calculate and display the overall average number of days between all workouts
- **FR-004**: System MUST provide a muscle group selector/filter that allows users to view frequency metrics for specific muscle groups
- **FR-005**: System MUST calculate and display average days between workouts for the selected muscle group
- **FR-006**: System MUST provide an exercise name selector/filter that allows users to view frequency metrics for specific exercises
- **FR-007**: System MUST calculate and display average days between performances of the selected exercise
- **FR-008**: System MUST handle cases with insufficient data gracefully, displaying informative messages when calculations cannot be performed
- **FR-009**: Analytics calculations MUST exclude same-day workout pairs from average calculations (only count gaps of 1+ days)
- **FR-010**: System MUST sort muscle group and exercise selectors alphabetically for easy navigation

#### BigQuery Enhancement Requirements

- **FR-011**: System MUST upload exercise mapping configuration to BigQuery as a dedicated table named `exercise_muscle_mapping`
- **FR-012**: Exercise mapping table MUST include columns: exercise_name, muscle_group_level1, muscle_group_level2, is_compound
- **FR-013**: System MUST create BigQuery views for common analytics queries including workout frequency by muscle group and exercise frequency
- **FR-014**: System MUST include a pipeline step that executes and refreshes BigQuery views after workout data is uploaded
- **FR-015**: Pipeline MUST handle view update failures gracefully with logging and retry logic
- **FR-016**: BigQuery views MUST use the exercise mapping table to join workout data with muscle group classifications

### Key Entities

- **Workout Frequency Metric**: Calculated metric representing average days between workouts, can be filtered by muscle group or exercise name
- **Exercise Mapping Entry**: Mapping between exercise name and muscle group classifications (level 1, level 2, compound flag)
- **BigQuery View**: Predefined SQL query stored in BigQuery that calculates analytics metrics from source tables
- **Analytics Tab**: UI component organizing different analysis perspectives (overview, muscle groups, exercises)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can navigate to the Analytics page and see overall workout frequency metrics displayed within 2 seconds of page load
- **SC-002**: Users can switch between muscle group and exercise analysis tabs without page refresh
- **SC-003**: Selecting a different muscle group or exercise updates displayed metrics within 1 second
- **SC-004**: Exercise mapping data is successfully uploaded to BigQuery whenever workout data is uploaded, maintaining data consistency
- **SC-005**: BigQuery views refresh automatically within 30 seconds of workout data upload completion
- **SC-006**: Analytics calculations produce accurate results matching manual calculations on the same dataset (100% accuracy)
- **SC-007**: System displays appropriate messages for edge cases (insufficient data, no matching workouts) 100% of the time

## Assumptions

- Workout data already exists in BigQuery with necessary fields (datetime, exercise_name, muscle group mappings)
- Exercise mapping configuration file is already defined and maintained (as shown in existing `config/exercise_mapping.yaml`)
- Users understand basic workout terminology (muscle groups, exercise names)
- BigQuery authentication and connection are already configured in the application
- The Streamlit application already has a navigation structure where a new page can be added
- Average days between workouts is calculated as: (total days from first to last workout) / (number of workouts - 1), or alternatively as average of all individual gaps between consecutive workouts
- "Days between workouts" refers to calendar days, not training days or weighted by workout intensity
