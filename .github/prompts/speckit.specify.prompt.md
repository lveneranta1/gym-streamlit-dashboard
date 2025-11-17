---
agent: speckit.specify
---

# Personal Workout Tracking Application - Specification

## 1. Application Overview

### Purpose
A Streamlit web application for tracking personal workout data through CSV uploads, storing data in a database backend, and providing comprehensive workout analytics and metrics.

### Key Objectives
- Simple CSV-based workout data upload
- Persistent database storage with historical record keeping
- Automated data enrichment with muscle group mappings
- Comprehensive workout analytics and insights
- Personal progress tracking over time

## 2. Data Model

### 2.1 Input Data Schema (CSV Format)
**Required columns:**
- `datetime` - Timestamp of the workout/exercise (format: YYYY-MM-DD HH:MM:SS or YYYY-MM-DD)
- `workout_name` - Name/type of workout session (e.g., "Push Day", "Leg Day")
- `exercise_name` - Specific exercise performed (e.g., "Bench Press", "Squat")
- `weight` - Weight used in kg or lbs (numeric)
- `reps` - Number of repetitions (integer)

**Optional columns:**
- `sets` - Number of sets (integer)
- `notes` - Any additional notes about the exercise
- `duration_minutes` - Duration of exercise or workout

### 2.2 Database Schema

**Table: workouts**
```sql
- id (PRIMARY KEY, auto-increment)
- datetime (TIMESTAMP)
- workout_name (VARCHAR)
- exercise_name (VARCHAR)
- weight (DECIMAL)
- reps (INTEGER)
- sets (INTEGER, nullable)
- notes (TEXT, nullable)
- duration_minutes (INTEGER, nullable)
- muscle_group_level1 (VARCHAR) -- upper/lower
- muscle_group_level2 (VARCHAR) -- specific muscle
- upload_timestamp (TIMESTAMP) -- when data was uploaded
- data_hash (VARCHAR) -- for deduplication
```

**Table: workout_history_snapshots**
```sql
- id (PRIMARY KEY, auto-increment)
- snapshot_timestamp (TIMESTAMP)
- snapshot_data (JSON or TEXT) -- full dataset backup
- record_count (INTEGER)
- data_hash (VARCHAR) -- hash of entire dataset
```

**Table: exercise_muscle_mapping**
```sql
- id (PRIMARY KEY, auto-increment)
- exercise_name (VARCHAR, UNIQUE)
- muscle_group_level1 (VARCHAR) -- upper/lower
- muscle_group_level2 (VARCHAR) -- specific muscle
- is_compound (BOOLEAN) -- compound vs isolation
```

### 2.3 Muscle Group Classification

**Level 1 (Primary Split):**
- `upper` - Upper body exercises
- `lower` - Lower body exercises
- `core` - Core/abs exercises
- `full_body` - Full body movements

**Level 2 (Specific Muscles):**

Upper:
- `chest` - Pectorals
- `back` - Lats, rhomboids, traps
- `shoulders` - Deltoids
- `triceps` - Triceps
- `biceps` - Biceps
- `forearms` - Forearm muscles

Lower:
- `quads` - Quadriceps
- `hamstrings` - Hamstrings
- `glutes` - Glutes
- `calves` - Calves
- `adductors` - Inner thigh

Core:
- `abs` - Abdominals
- `obliques` - Obliques
- `lower_back` - Lower back/erectors

## 3. Configuration System

### 3.1 Configuration Files

**config/csv_schema.yaml**
```yaml
required_columns:
  - name: datetime
    type: datetime
    format: ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
  - name: workout_name
    type: string
  - name: exercise_name
    type: string
  - name: weight
    type: float
    min_value: 0
  - name: reps
    type: integer
    min_value: 1

optional_columns:
  - name: sets
    type: integer
    default: 1
  - name: notes
    type: string
    default: ""
  - name: duration_minutes
    type: integer
    default: null

column_mappings:
  # Allow flexible column names
  datetime: ["datetime", "date", "timestamp", "time"]
  workout_name: ["workout_name", "workout", "session"]
  exercise_name: ["exercise_name", "exercise", "name"]
  weight: ["weight", "weight_kg", "weight_lbs"]
  reps: ["reps", "repetitions", "rep"]
```

**config/exercise_mapping.yaml**
```yaml
# Automatic muscle group mapping
exercises:
  # Chest
  - names: ["bench press", "barbell bench press", "dumbbell bench press"]
    level1: upper
    level2: chest
    compound: true
  
  - names: ["incline bench press", "incline press"]
    level1: upper
    level2: chest
    compound: true
  
  - names: ["chest fly", "dumbbell fly", "cable fly"]
    level1: upper
    level2: chest
    compound: false
  
  # Back
  - names: ["deadlift", "conventional deadlift", "romanian deadlift"]
    level1: full_body
    level2: back
    compound: true
  
  - names: ["pull up", "pullup", "chin up"]
    level1: upper
    level2: back
    compound: true
  
  - names: ["barbell row", "bent over row", "dumbbell row"]
    level1: upper
    level2: back
    compound: true
  
  - names: ["lat pulldown", "cable pulldown"]
    level1: upper
    level2: back
    compound: true
  
  # Legs
  - names: ["squat", "back squat", "front squat", "barbell squat"]
    level1: lower
    level2: quads
    compound: true
  
  - names: ["leg press"]
    level1: lower
    level2: quads
    compound: true
  
  - names: ["leg extension"]
    level1: lower
    level2: quads
    compound: false
  
  - names: ["leg curl", "hamstring curl"]
    level1: lower
    level2: hamstrings
    compound: false
  
  - names: ["lunge", "walking lunge", "reverse lunge"]
    level1: lower
    level2: quads
    compound: true
  
  # Shoulders
  - names: ["overhead press", "military press", "shoulder press"]
    level1: upper
    level2: shoulders
    compound: true
  
  - names: ["lateral raise", "side raise"]
    level1: upper
    level2: shoulders
    compound: false
  
  # Arms
  - names: ["bicep curl", "barbell curl", "dumbbell curl"]
    level1: upper
    level2: biceps
    compound: false
  
  - names: ["tricep extension", "overhead extension", "skull crusher"]
    level1: upper
    level2: triceps
    compound: false
  
  - names: ["tricep dip", "dips"]
    level1: upper
    level2: triceps
    compound: true

# Fallback rules for unmapped exercises
fallback_rules:
  - keyword: "press"
    level1: upper
    level2: chest
  - keyword: "curl"
    level1: upper
    level2: biceps
  - keyword: "squat"
    level1: lower
    level2: quads
```

**config/database.yaml**
```yaml
database:
  type: sqlite  # or postgresql, mysql
  path: data/workouts.db  # for sqlite
  # For PostgreSQL/MySQL:
  # host: localhost
  # port: 5432
  # database: workout_tracker
  # user: ${DB_USER}
  # password: ${DB_PASSWORD}

backup:
  enabled: true
  frequency: daily  # daily, weekly, on_upload
  retention_days: 90
  location: data/backups/
```

## 4. Core Features

### 4.1 Data Upload & Processing

**Upload Interface:**
- Drag-and-drop CSV file upload
- File validation before processing
- Preview of parsed data before confirming upload
- Column mapping interface (if column names differ)
- Error reporting for invalid data

**Processing Logic:**
1. Parse CSV using configured schema
2. Validate all required columns present
3. Apply data type validations
4. Enrich data with muscle group mappings
5. Calculate data hash for deduplication
6. Create snapshot of existing data (if enabled)
7. Replace full dataset in database
8. Log upload metadata

**Deduplication Strategy:**
- Check if uploaded data hash matches existing data
- Skip upload if identical
- Warn user if significant data loss detected (e.g., 20% fewer records)

### 4.2 Analytics & Metrics

**Workout Frequency Metrics:**
- Total workouts per week/month
- Average workouts per week (last 4, 8, 12 weeks)
- Workout consistency streak (consecutive weeks with ≥X workouts)
- Day of week distribution (which days you train most)
- Time of day distribution

**Rest Day Analysis:**
- Average rest days between workouts
- Longest rest period
- Rest day frequency per week
- Recovery patterns

**Muscle Group Analysis:**
- Workout frequency per muscle group (Level 1 & Level 2)
- Average days between training each muscle group
- Muscle group distribution (pie chart)
- Training balance score (even distribution vs. imbalanced)
- Muscle group volume trends over time

**Volume & Intensity Metrics:**
- Total volume per workout (weight × reps × sets)
- Volume per muscle group per week
- Average weight progression per exercise
- Personal records (max weight for each exercise)
- Training volume trends (weekly/monthly)

**Exercise-Specific Metrics:**
- Most frequently performed exercises
- Exercises by volume
- Exercise progression charts (weight over time)
- Rep range analysis per exercise
- Exercise variety score

### 4.3 Visualization Dashboard

**Overview Page:**
- Key metrics cards (total workouts, current streak, total volume)
- Workout frequency calendar heatmap
- Recent workouts table
- Weekly volume trend

**Muscle Group Page:**
- Muscle group distribution (Level 1 & 2)
- Training frequency per muscle group
- Volume per muscle group over time
- Recovery time between muscle group training

**Exercise Analysis Page:**
- Exercise selection filters (by muscle group, exercise name)
- Weight progression line charts
- Volume trends
- Personal records table
- Rep range distribution

**Calendar View:**
- Monthly calendar with workout indicators
- Click day to see workout details
- Color coding by workout type or intensity

### 4.4 Data Management

**Historical Snapshots:**
- Automatic snapshots before each upload
- Manual snapshot creation
- View snapshot history
- Restore from snapshot capability
- Export snapshots as CSV

**Data Export:**
- Export full dataset as CSV
- Export filtered data (date range, muscle group, exercise)
- Export analytics summary as PDF/CSV

## 5. Technical Implementation

### 5.1 Technology Stack
- **Frontend:** Streamlit
- **Database:** SQLite (local) or PostgreSQL (production)
- **Data Processing:** pandas, numpy
- **Visualization:** plotly, altair
- **Configuration:** PyYAML
- **Utilities:** python-dateutil, hashlib

### 5.2 Project Structure
```
gym-streamlit-dashboard/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Python dependencies
├── config/
│   ├── csv_schema.yaml            # CSV input schema
│   ├── exercise_mapping.yaml      # Exercise to muscle group mapping
│   └── database.yaml              # Database configuration
├── data/
│   ├── workouts.db                # SQLite database
│   └── backups/                   # Snapshot backups
├── modules/
│   ├── __init__.py
│   ├── database.py                # Database operations
│   ├── csv_parser.py              # CSV parsing & validation
│   ├── data_enrichment.py         # Muscle group mapping
│   ├── analytics.py               # Metrics calculation
│   ├── visualizations.py          # Chart generation
│   └── config_loader.py           # Config file handling
└── tests/
    ├── test_csv_parser.py
    ├── test_data_enrichment.py
    └── sample_data.csv
```

### 5.3 Key Classes & Functions

**CSVParser:**
- `parse_csv(file, schema_config)` - Parse and validate CSV
- `validate_schema(df, schema)` - Ensure required columns present
- `map_columns(df, mappings)` - Handle flexible column names
- `validate_data_types(df, schema)` - Type checking and conversion

**DataEnrichment:**
- `map_exercise_to_muscles(exercise_name, mapping_config)` - Get muscle groups
- `enrich_dataframe(df, mapping_config)` - Add muscle group columns
- `calculate_volume(df)` - Add volume calculations

**DatabaseManager:**
- `initialize_database()` - Create tables
- `upload_workouts(df, create_snapshot=True)` - Replace full dataset
- `create_snapshot(df)` - Save historical snapshot
- `get_workouts(filters)` - Query workouts
- `restore_snapshot(snapshot_id)` - Restore from backup

**Analytics:**
- `calculate_workout_frequency(df, period)` - Workout freq metrics
- `calculate_rest_days(df)` - Rest day analysis
- `calculate_muscle_group_frequency(df)` - Muscle group stats
- `calculate_volume_metrics(df)` - Volume calculations
- `get_personal_records(df)` - Max weights per exercise

## 6. User Interface Flow

### 6.1 Page Navigation
**Sidebar Menu:**
1. 📤 Upload Data
2. 📊 Dashboard
3. 💪 Muscle Groups
4. 🏋️ Exercises
5. 📅 Calendar
6. ⚙️ Settings
7. 💾 Data Management

### 6.2 Upload Page Workflow
1. User drops CSV file or clicks to upload
2. System validates file format
3. Display data preview table (first 10 rows)
4. Show detected columns and mappings
5. Allow user to adjust column mappings if needed
6. Show summary: X rows, date range, unique exercises
7. Confirmation button: "Upload and Replace Data"
8. Progress indicator during processing
9. Success message with upload summary

### 6.3 Dashboard Page Layout
**Top Row (Metrics Cards):**
- Total Workouts | Current Streak | Avg per Week | Total Volume

**Second Row:**
- Workout frequency chart (last 12 weeks)
- Muscle group distribution (pie chart)

**Third Row:**
- Recent workouts table (last 10)
- Rest day analysis

### 6.4 Settings Page
- Configure snapshot frequency
- Manage exercise-to-muscle mappings (add custom exercises)
- Export/import configuration
- Database statistics

## 7. Data Validation & Error Handling

### 7.1 Upload Validations
- CSV file size limit (e.g., 50MB)
- Required columns present
- Date format validity
- Numeric fields are valid numbers
- No future dates
- Weight and reps > 0
- Duplicate row detection

### 7.2 Error Messages
- Clear, actionable error messages
- Specific row/column references for data issues
- Suggestions for fixing common problems
- Option to download error report

### 7.3 Data Quality Checks
- Warn if unusual gaps in data (e.g., 30+ day gap)
- Flag potential data entry errors (e.g., 500kg bench press)
- Detect unmapped exercises (suggest adding to config)

## 8. Future Enhancements (Optional)

### Phase 2 Features
- Multi-user support with authentication
- Mobile-responsive design
- Exercise video/instruction links
- Workout planning and templates
- Goal setting and tracking
- Body measurements tracking
- Integration with fitness apps (Strava, MyFitnessPal)
- Machine learning predictions (weight progression, injury risk)
- Social features (share progress)

### Advanced Analytics
- Periodization detection
- Fatigue monitoring
- Optimal training frequency recommendations
- Exercise recommendations based on imbalances
- Progressive overload tracking

## 9. Success Criteria

### Must Have (MVP)
- ✅ CSV upload and parsing
- ✅ Database storage with full dataset replacement
- ✅ Historical snapshot creation
- ✅ Muscle group mapping from config
- ✅ Basic analytics (workout frequency, muscle group frequency)
- ✅ Simple dashboard with key metrics

### Should Have
- ✅ Advanced analytics (volume, PRs, rest days)
- ✅ Multiple visualization pages
- ✅ Calendar view
- ✅ Data export functionality
- ✅ Snapshot restoration

### Nice to Have
- ⭐ Automated anomaly detection
- ⭐ Exercise recommendations
- ⭐ Configurable workout goals
- ⭐ PDF report generation