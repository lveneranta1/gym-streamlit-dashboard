---
agent: speckit.tasks
---

# Workout Data Upload to BigQuery - Task List

## 🚀 Phase 1: Project Setup & Configuration System

### Task 1.1: Initialize Project Structure
- [ ] Create main project directory structure
- [ ] Initialize git repository
- [ ] Create `.gitignore` with Python/Streamlit patterns
- [ ] Create `README.md` with project overview
- [ ] Create folder structure:
  - `config/` - Configuration files
  - `modules/` - Python modules
  - `tests/` - Test files and sample data
  - `data/` - Local data storage (gitignored)

**Deliverable:** Complete folder structure with README

---

### Task 1.2: Create requirements.txt
- [ ] Add Streamlit (>=1.28.0)
- [ ] Add pandas (>=2.0.0)
- [ ] Add PyYAML (>=6.0)
- [ ] Add google-cloud-bigquery (>=3.11.0)
- [ ] Add google-auth (>=2.22.0)
- [ ] Add python-dotenv (>=1.0.0)

**Deliverable:** `requirements.txt` file

---

### Task 1.3: Create Environment Configuration
- [ ] Create `.env.example` with template variables:
  - `GCP_PROJECT_ID`
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `BQ_DATASET_ID`
  - `BQ_TABLE_ID`
- [ ] Add `.env` to `.gitignore`
- [ ] Document environment setup in README

**Deliverable:** `.env.example` file with documentation

---

### Task 1.4: Create CSV Schema Configuration
- [ ] Create `config/csv_schema.yaml`
- [ ] Define required columns (datetime, workout_name, exercise_name, weight, reps)
- [ ] Define optional columns (sets, notes, duration_minutes)
- [ ] Add column aliases for flexible matching
- [ ] Add validation rules (min/max, types, formats)
- [ ] Configure datetime format options

**Deliverable:** `config/csv_schema.yaml`

---

### Task 1.5: Create Exercise Mapping Configuration
- [ ] Create `config/exercise_mapping.yaml`
- [ ] Define muscle group hierarchies (level1, level2)
- [ ] Add chest exercises (bench press, fly, etc.)
- [ ] Add back exercises (deadlift, row, pulldown, etc.)
- [ ] Add leg exercises (squat, leg press, curl, etc.)
- [ ] Add shoulder exercises (press, raise, etc.)
- [ ] Add arm exercises (curl, extension, dip, etc.)
- [ ] Add core exercises (plank, crunch, etc.)
- [ ] Define fuzzy matching rules for unmapped exercises
- [ ] Set default mapping for unknown exercises

**Deliverable:** `config/exercise_mapping.yaml` with 50+ exercises

---

### Task 1.6: Create BigQuery Configuration
- [ ] Create `config/bigquery_config.yaml`
- [ ] Define connection settings with env var placeholders
- [ ] Define BigQuery table schema matching enriched data
- [ ] Configure upload settings (write_disposition, batch_size, timeout)
- [ ] Add table creation settings

**Deliverable:** `config/bigquery_config.yaml`

---

### Task 1.7: Implement Configuration Loader Module
- [ ] Create `modules/__init__.py`
- [ ] Create `modules/config_loader.py`
- [ ] Implement `ConfigLoader` class
- [ ] Add `load_yaml()` method with caching
- [ ] Add `_replace_env_vars()` for ${VAR} substitution
- [ ] Add convenience methods:
  - `get_csv_schema()`
  - `get_exercise_mapping()`
  - `get_bigquery_config()`
- [ ] Add error handling for missing files
- [ ] Add environment variable loading with python-dotenv

**Deliverable:** `modules/config_loader.py` with full implementation

---

## 📄 Phase 2: CSV Parsing Module

### Task 2.1: Create CSV Parser Class Structure
- [ ] Create `modules/csv_parser.py`
- [ ] Define `CSVParser` class with `__init__(schema_config)`
- [ ] Initialize instance variables for errors and warnings
- [ ] Add type hints for all methods

**Deliverable:** `modules/csv_parser.py` with class skeleton

---

### Task 2.2: Implement Column Mapping Logic
- [ ] Add `_map_columns()` method
- [ ] Implement alias matching (case-insensitive)
- [ ] Rename columns to standard names
- [ ] Track which aliases were used
- [ ] Handle missing columns gracefully

**Deliverable:** Working column mapping with alias support

---

### Task 2.3: Implement Data Type Validation
- [ ] Add `_validate_data_types()` method
- [ ] Convert datetime columns with multiple format support
- [ ] Convert numeric columns (float, integer)
- [ ] Handle conversion errors with detailed messages
- [ ] Add row-level error tracking

**Deliverable:** Data type validation with error reporting

---

### Task 2.4: Implement Constraint Validation
- [ ] Add `_validate_constraints()` method
- [ ] Check min/max values for numeric columns
- [ ] Validate datetime ranges (no future dates)
- [ ] Check for required vs optional columns
- [ ] Collect all validation errors

**Deliverable:** Constraint validation logic

---

### Task 2.5: Implement Main Parse Method
- [ ] Add `parse_csv(file)` method
- [ ] Read CSV file into pandas DataFrame
- [ ] Apply column mapping
- [ ] Apply data type validation
- [ ] Apply constraint validation
- [ ] Add default values for optional columns
- [ ] Return cleaned DataFrame

**Deliverable:** Complete `parse_csv()` implementation

---

### Task 2.6: Add Error Reporting
- [ ] Add `get_validation_errors()` method
- [ ] Format errors with row numbers and column names
- [ ] Add `get_warnings()` for non-critical issues
- [ ] Add summary statistics (total rows, errors, warnings)

**Deliverable:** Error reporting methods

---

## 💪 Phase 3: Data Enrichment Module

### Task 3.1: Create Data Enrichment Class Structure
- [ ] Create `modules/data_enrichment.py`
- [ ] Define `DataEnrichment` class with `__init__(mapping_config)`
- [ ] Initialize exercise mapping dictionary
- [ ] Parse configuration into searchable structure

**Deliverable:** `modules/data_enrichment.py` with class skeleton

---

### Task 3.2: Implement Exact Exercise Matching
- [ ] Add `_exact_match()` method
- [ ] Normalize exercise names (lowercase, strip, remove extra spaces)
- [ ] Search for exact matches in configured exercises
- [ ] Return muscle group mapping if found

**Deliverable:** Exact matching logic

---

### Task 3.3: Implement Fuzzy Exercise Matching
- [ ] Add `_fuzzy_match()` method
- [ ] Apply keyword-based fuzzy rules
- [ ] Check exclusion patterns
- [ ] Return best match based on rules

**Deliverable:** Fuzzy matching logic

---

### Task 3.4: Implement Exercise Mapping Logic
- [ ] Add `_map_exercise_to_muscles()` method
- [ ] Try exact match first
- [ ] Fall back to fuzzy match
- [ ] Apply default mapping if no match
- [ ] Track unmapped exercises

**Deliverable:** Complete exercise mapping logic

---

### Task 3.5: Implement DataFrame Enrichment
- [ ] Add `enrich_dataframe()` method
- [ ] Apply mapping to all exercises
- [ ] Add `muscle_group_level1` column
- [ ] Add `muscle_group_level2` column
- [ ] Return enriched DataFrame

**Deliverable:** DataFrame enrichment method

---

### Task 3.6: Add Unmapped Exercise Tracking
- [ ] Add `get_unmapped_exercises()` method
- [ ] Return list of exercises without matches
- [ ] Add counts for each unmapped exercise
- [ ] Suggest possible mappings based on fuzzy rules

**Deliverable:** Unmapped exercise reporting

---

## ☁️ Phase 4: BigQuery Upload Module

### Task 4.1: Create BigQuery Uploader Class Structure
- [ ] Create `modules/bigquery_uploader.py`
- [ ] Define `BigQueryUploader` class with `__init__(bq_config)`
- [ ] Initialize configuration variables
- [ ] Add error tracking

**Deliverable:** `modules/bigquery_uploader.py` with class skeleton

---

### Task 4.2: Implement BigQuery Client Initialization
- [ ] Add `initialize_client()` method
- [ ] Load credentials from file or default application credentials
- [ ] Initialize BigQuery client
- [ ] Test connection
- [ ] Handle authentication errors

**Deliverable:** Client initialization with error handling

---

### Task 4.3: Implement Table Creation Logic
- [ ] Add `create_table_if_not_exists()` method
- [ ] Convert YAML schema to BigQuery schema objects
- [ ] Check if table exists
- [ ] Create table with schema if needed
- [ ] Handle table creation errors

**Deliverable:** Automatic table creation

---

### Task 4.4: Implement Metadata Addition
- [ ] Add `_add_metadata_columns()` method
- [ ] Add `upload_timestamp` (current timestamp)
- [ ] Add `data_source` (e.g., "csv_upload")
- [ ] Ensure timezone awareness for timestamps

**Deliverable:** Metadata column addition

---

### Task 4.5: Implement Schema Validation
- [ ] Add `_validate_schema()` method
- [ ] Check DataFrame columns match BigQuery schema
- [ ] Verify data types are compatible
- [ ] Report mismatches with details

**Deliverable:** Schema validation logic

---

### Task 4.6: Implement Upload Method
- [ ] Add `upload_dataframe()` method
- [ ] Add metadata columns
- [ ] Validate schema
- [ ] Configure job settings (write disposition, timeout)
- [ ] Upload using `load_table_from_dataframe()`
- [ ] Wait for job completion
- [ ] Return upload statistics

**Deliverable:** Complete upload implementation

---

### Task 4.7: Add Upload Statistics
- [ ] Add `get_upload_stats()` method
- [ ] Track rows uploaded
- [ ] Track upload duration
- [ ] Track any errors
- [ ] Format results for display

**Deliverable:** Upload statistics tracking

---

## 🎨 Phase 5: Streamlit UI

### Task 5.1: Create Main App Structure
- [ ] Create `app.py`
- [ ] Add Streamlit page configuration
- [ ] Add title and header
- [ ] Initialize session state variables
- [ ] Create tab-based navigation

**Deliverable:** `app.py` with basic structure

---

### Task 5.2: Implement File Upload Widget
- [ ] Add file uploader in Upload tab
- [ ] Configure for CSV files only
- [ ] Add file size limit
- [ ] Store uploaded file in session state
- [ ] Show file information (name, size)

**Deliverable:** File upload interface

---

### Task 5.3: Implement CSV Preview
- [ ] Parse uploaded CSV
- [ ] Display first 10 rows in dataframe widget
- [ ] Show column names and types
- [ ] Display row count
- [ ] Handle parsing errors gracefully

**Deliverable:** CSV preview functionality

---

### Task 5.4: Implement Validation Display
- [ ] Run CSV parser validation
- [ ] Display validation results
- [ ] Show errors in expandable section
- [ ] Show warnings separately
- [ ] Add color coding (red for errors, yellow for warnings)
- [ ] Block upload if critical errors exist

**Deliverable:** Validation results display

---

### Task 5.5: Implement Data Enrichment Preview
- [ ] Run data enrichment on parsed data
- [ ] Display enriched columns (muscle groups)
- [ ] Show exercise-to-muscle mapping table
- [ ] Highlight unmapped exercises
- [ ] Allow user to review mappings

**Deliverable:** Enrichment preview

---

### Task 5.6: Implement Upload to BigQuery
- [ ] Add "Upload to BigQuery" button
- [ ] Show progress spinner during upload
- [ ] Initialize BigQuery uploader
- [ ] Create table if needed
- [ ] Upload dataframe
- [ ] Display upload statistics
- [ ] Show success/error messages
- [ ] Handle and display errors

**Deliverable:** BigQuery upload functionality

---

### Task 5.7: Create Schema Config Page
- [ ] Add Schema Config tab
- [ ] Display current CSV schema configuration
- [ ] Show required columns list
- [ ] Show optional columns list
- [ ] Display column aliases
- [ ] Display validation rules
- [ ] Add option to reload configuration

**Deliverable:** Schema configuration viewer

---

### Task 5.8: Create Exercise Mapping Page
- [ ] Add Exercise Mapping tab
- [ ] Display all mapped exercises in table
- [ ] Group by muscle group
- [ ] Add search/filter functionality
- [ ] Show exercise counts per muscle group
- [ ] Display fuzzy matching rules
- [ ] Show default mapping

**Deliverable:** Exercise mapping viewer

---

### Task 5.9: Create BigQuery Config Page
- [ ] Add BigQuery Config tab
- [ ] Display connection settings (masked sensitive info)
- [ ] Show table schema
- [ ] Add "Test Connection" button
- [ ] Display upload settings
- [ ] Show last upload statistics
- [ ] Add option to view table in BigQuery console

**Deliverable:** BigQuery configuration viewer

---

### Task 5.10: Add Sidebar Information
- [ ] Create sidebar with app information
- [ ] Add configuration status indicators
- [ ] Show BigQuery connection status
- [ ] Add links to documentation
- [ ] Display app version

**Deliverable:** Informative sidebar

---

### Task 5.11: Implement Error Handling UI
- [ ] Add global error handler
- [ ] Display errors in expandable containers
- [ ] Add "Copy error details" button
- [ ] Provide troubleshooting suggestions
- [ ] Add option to download error log

**Deliverable:** Comprehensive error display

---

## 🧪 Phase 6: Testing & Validation

### Task 6.1: Create Sample Test Data
- [ ] Create `tests/sample_workout_data.csv`
- [ ] Include all required columns
- [ ] Add variety of exercises (chest, back, legs, shoulders, arms)
- [ ] Include some unmapped exercises for testing
- [ ] Add various date formats
- [ ] Include edge cases (high weights, low reps, etc.)

**Deliverable:** `tests/sample_workout_data.csv`

---

### Task 6.2: Create Config Loader Tests
- [ ] Create `tests/test_config_loader.py`
- [ ] Test YAML file loading
- [ ] Test environment variable substitution
- [ ] Test missing file handling
- [ ] Test invalid YAML handling
- [ ] Test convenience methods

**Deliverable:** Config loader test suite

---

### Task 6.3: Create CSV Parser Tests
- [ ] Create `tests/test_csv_parser.py`
- [ ] Test valid CSV parsing
- [ ] Test column alias matching
- [ ] Test data type validation
- [ ] Test constraint validation
- [ ] Test error reporting
- [ ] Test with missing columns
- [ ] Test with invalid data types

**Deliverable:** CSV parser test suite

---

### Task 6.4: Create Data Enrichment Tests
- [ ] Create `tests/test_data_enrichment.py`
- [ ] Test exact exercise matching
- [ ] Test fuzzy matching
- [ ] Test default mapping
- [ ] Test unmapped exercise tracking
- [ ] Test case insensitivity
- [ ] Test DataFrame enrichment

**Deliverable:** Data enrichment test suite

---

### Task 6.5: Create BigQuery Uploader Tests
- [ ] Create `tests/test_bigquery_uploader.py`
- [ ] Test client initialization (mock)
- [ ] Test table creation (mock)
- [ ] Test metadata addition
- [ ] Test schema validation
- [ ] Test upload method (mock)
- [ ] Test error handling

**Deliverable:** BigQuery uploader test suite

---

### Task 6.6: Perform End-to-End Testing
- [ ] Test complete upload workflow with sample data
- [ ] Verify data in BigQuery (manual check)
- [ ] Test with various CSV formats
- [ ] Test with large files (1000+ rows)
- [ ] Test error scenarios
- [ ] Test configuration changes
- [ ] Document test results

**Deliverable:** E2E test documentation

---

### Task 6.7: Performance Testing
- [ ] Test upload performance with 10k rows
- [ ] Test upload performance with 100k rows
- [ ] Measure parsing time
- [ ] Measure enrichment time
- [ ] Measure upload time
- [ ] Identify bottlenecks
- [ ] Document performance metrics

**Deliverable:** Performance test results

---

## 📚 Phase 7: Documentation & Deployment

### Task 7.1: Write Comprehensive README
- [ ] Add project overview and purpose
- [ ] List key features
- [ ] Add prerequisites (Python version, GCP account)
- [ ] Write installation instructions
- [ ] Document environment setup
- [ ] Add usage examples with screenshots
- [ ] Document configuration options
- [ ] Add troubleshooting section
- [ ] Include contribution guidelines
- [ ] Add license information

**Deliverable:** Complete `README.md`

---

### Task 7.2: Create Configuration Guide
- [ ] Document CSV schema configuration
- [ ] Explain column aliases usage
- [ ] Document exercise mapping format
- [ ] Explain fuzzy matching rules
- [ ] Document BigQuery configuration
- [ ] Add examples for common scenarios
- [ ] Include configuration best practices

**Deliverable:** Configuration documentation in README or separate guide

---

### Task 7.3: Create GCP Setup Guide
- [ ] Document GCP project setup
- [ ] Explain service account creation
- [ ] Document required IAM permissions
- [ ] Explain credentials file setup
- [ ] Document BigQuery dataset creation
- [ ] Add troubleshooting for common GCP issues

**Deliverable:** GCP setup section in README

---

### Task 7.4: Add Code Documentation
- [ ] Add docstrings to all classes
- [ ] Add docstrings to all methods
- [ ] Add inline comments for complex logic
- [ ] Add type hints throughout
- [ ] Generate API documentation (optional: Sphinx)

**Deliverable:** Well-documented codebase

---

### Task 7.5: Create Usage Examples
- [ ] Create example CSV files with different scenarios
- [ ] Document common workflows
- [ ] Add screenshots of UI
- [ ] Create video tutorial (optional)
- [ ] Add FAQ section

**Deliverable:** Usage examples and FAQ

---

### Task 7.6: Prepare for Deployment
- [ ] Add logging throughout application
- [ ] Configure logging levels
- [ ] Add error tracking (Sentry integration optional)
- [ ] Add usage analytics (optional)
- [ ] Create deployment checklist
- [ ] Test in production-like environment

**Deliverable:** Production-ready application

---

### Task 7.7: Create CI/CD Pipeline (Optional)
- [ ] Create GitHub Actions workflow
- [ ] Add automated testing on push
- [ ] Add code quality checks (pylint, black)
- [ ] Add security scanning
- [ ] Configure deployment automation
- [ ] Add badges to README

**Deliverable:** CI/CD pipeline (optional)

---

### Task 7.8: Security Review
- [ ] Review credential handling
- [ ] Ensure .env not in git
- [ ] Check BigQuery permissions
- [ ] Review data validation for injection risks
- [ ] Add rate limiting (if public)
- [ ] Document security best practices

**Deliverable:** Security review checklist

---

## ✅ Final Checklist

### Pre-Launch
- [ ] All unit tests passing
- [ ] End-to-end testing complete
- [ ] Documentation complete
- [ ] GCP setup verified
- [ ] Sample data uploaded successfully
- [ ] Error handling tested
- [ ] Performance acceptable

### Launch
- [ ] Deploy application
- [ ] Monitor for errors
- [ ] Collect user feedback
- [ ] Document issues and improvements

### Post-Launch
- [ ] Address bug reports
- [ ] Implement user-requested features
- [ ] Optimize performance
- [ ] Update documentation

---

## 📊 Progress Tracking

**Phase 1:** ⬜⬜⬜⬜⬜⬜⬜ 0/7 tasks  
**Phase 2:** ⬜⬜⬜⬜⬜⬜ 0/6 tasks  
**Phase 3:** ⬜⬜⬜⬜⬜⬜ 0/6 tasks  
**Phase 4:** ⬜⬜⬜⬜⬜⬜⬜ 0/7 tasks  
**Phase 5:** ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/11 tasks  
**Phase 6:** ⬜⬜⬜⬜⬜⬜⬜ 0/7 tasks  
**Phase 7:** ⬜⬜⬜⬜⬜⬜⬜⬜ 0/8 tasks  

**Total Progress:** 0/52 tasks (0%)

---

## 🎯 Priority Levels

### Must Have (MVP)
- All Phase 1 tasks (Setup)
- All Phase 2 tasks (CSV Parser)
- All Phase 3 tasks (Data Enrichment)
- All Phase 4 tasks (BigQuery Upload)
- Phase 5: Tasks 5.1-5.6 (Basic UI)
- Phase 6: Tasks 6.1, 6.6 (Sample data + E2E testing)
- Phase 7: Tasks 7.1, 7.3 (README + GCP setup)

### Should Have
- Phase 5: Tasks 5.7-5.11 (Config viewers + error handling)
- Phase 6: Tasks 6.2-6.5 (Unit tests)
- Phase 7: Tasks 7.2, 7.4-7.5 (Documentation)

### Nice to Have
- Phase 6: Task 6.7 (Performance testing)
- Phase 7: Tasks 7.6-7.8 (Production prep, CI/CD, security)

---

## 📝 Notes

- Update this document as tasks are completed
- Mark tasks with ✅ when done
- Add notes for blockers or issues
- Track time spent on each phase
- Review and adjust estimates as needed