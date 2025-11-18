# Data Model: GCP Infrastructure Resources

**Feature**: 001-gcp-terraform-iac  
**Date**: 2025-11-18  
**Purpose**: Document GCP resources and BigQuery schema

---

## Overview

This feature provisions infrastructure resources in Google Cloud Platform. The data model includes both infrastructure entities (managed by Terraform) and data schema (BigQuery table).

---

## Infrastructure Entities

### 1. GCP Project

**Entity Type**: Pre-existing (not managed by Terraform)

**Attributes**:
- `project_id` (string, required): Unique project identifier (e.g., "workout-tracker-12345")
- `project_number` (string, read-only): Numeric project identifier
- `billing_account` (string, required): Billing account ID linked to project

**Lifecycle**: Created manually by user via GCP Console before running Terraform.

**Validation Rules**:
- Project ID must be globally unique
- Must have billing enabled
- User must have Owner or Editor role

---

### 2. Service Account

**Entity Type**: Managed by Terraform

**Attributes**:
- `account_id` (string, required): Service account identifier (e.g., "workout-app-sa")
- `email` (string, computed): Full service account email (e.g., "workout-app-sa@{project_id}.iam.gserviceaccount.com")
- `display_name` (string, optional): Human-readable name
- `description` (string, optional): Purpose description

**Relationships**:
- Belongs to: GCP Project (one-to-one)
- Has: IAM Role Bindings (one-to-many)
- Has: Service Account Key (one-to-one)

**Validation Rules**:
- Account ID must be 6-30 characters
- Account ID can contain lowercase letters, digits, hyphens
- Must start with lowercase letter

---

### 3. Service Account Key

**Entity Type**: Managed by Terraform

**Attributes**:
- `private_key` (string, sensitive): Base64-encoded JSON key
- `public_key` (string): Public key portion
- `valid_after` (timestamp): Key validity start time
- `valid_before` (timestamp): Key validity end time

**Relationships**:
- Belongs to: Service Account (many-to-one)

**Security Considerations**:
- Private key is sensitive - never logged or committed
- Key stored locally in `terraform/keys/service-account-key.json`
- Key file must be in .gitignore

**Lifecycle**: Created with Terraform apply, destroyed with Terraform destroy

---

### 4. IAM Role Binding

**Entity Type**: Managed by Terraform

**Attributes**:
- `role` (string, required): IAM role name (e.g., "roles/bigquery.dataEditor")
- `member` (string, required): Identity (e.g., "serviceAccount:{email}")
- `project` (string, required): Project to grant role on

**Relationships**:
- Belongs to: GCP Project (many-to-one)
- References: Service Account (many-to-one)

**Required Roles for Application**:
1. `roles/bigquery.dataEditor` - Read/write BigQuery table data
2. `roles/bigquery.jobUser` - Execute BigQuery jobs (queries, loads)

---

### 5. BigQuery Dataset

**Entity Type**: Managed by Terraform

**Attributes**:
- `dataset_id` (string, required): Dataset identifier (e.g., "workout_data")
- `location` (string, required): Region (e.g., "europe-north1")
- `description` (string, optional): Dataset purpose
- `default_table_expiration_ms` (integer, optional): Auto-delete old tables
- `labels` (map, optional): Key-value tags

**Relationships**:
- Belongs to: GCP Project (many-to-one)
- Contains: BigQuery Tables (one-to-many)

**Validation Rules**:
- Dataset ID must be alphanumeric + underscores
- Dataset ID max 1024 characters
- Location must be valid GCP region

**Configuration**:
- Location: europe-north1 (Finland) - free tier supported
- No expiration (data kept indefinitely)

---

### 6. BigQuery Table

**Entity Type**: Managed by Terraform

**Attributes**:
- `table_id` (string, required): Table identifier (e.g., "workouts")
- `schema` (array, required): Column definitions (see schema below)
- `clustering` (array, optional): Columns for clustering
- `time_partitioning` (object, optional): Partitioning configuration

**Relationships**:
- Belongs to: BigQuery Dataset (many-to-one)

**Validation Rules**:
- Table ID must be alphanumeric + underscores
- Schema must define at least one column
- Schema types must be valid BigQuery types

---

## BigQuery Table Schema

### Table: `workouts`

**Purpose**: Store workout exercise data with muscle group enrichment

**Schema Definition**:

| Column Name | Type | Mode | Description | Validation |
|-------------|------|------|-------------|------------|
| `datetime` | TIMESTAMP | REQUIRED | When workout was performed | Must be valid timestamp |
| `workout_name` | STRING | REQUIRED | Name of workout session | Max 255 chars |
| `exercise_name` | STRING | REQUIRED | Name of exercise | Max 255 chars |
| `weight` | FLOAT64 | REQUIRED | Weight used (kg or lbs) | >= 0 |
| `reps` | INT64 | REQUIRED | Number of repetitions | >= 1 |
| `sets` | INT64 | NULLABLE | Number of sets | >= 1 if present |
| `notes` | STRING | NULLABLE | Additional notes | Max 1000 chars |
| `duration_minutes` | INT64 | NULLABLE | Exercise duration | >= 0 if present |
| `muscle_group_level1` | STRING | REQUIRED | Primary muscle group category | Enum: upper, lower, core, full_body |
| `muscle_group_level2` | STRING | REQUIRED | Specific muscle group | See exercise mapping |
| `upload_timestamp` | TIMESTAMP | REQUIRED | When data was uploaded | Auto-set by app |
| `data_source` | STRING | NULLABLE | Source of data | e.g., "csv_upload", "manual" |

**Primary Key**: None (BigQuery is append-only)

**Indexes**: None (BigQuery automatically indexes)

**Partitioning**: None for free tier (partitioning has costs)

**Clustering**: None initially (can add later if needed)

---

## Schema Evolution

### Adding Columns
- New optional (NULLABLE) columns can be added safely
- Existing data will have NULL for new columns
- Terraform plan will show schema changes

### Modifying Columns
- Changing column type may require creating new table
- Renaming columns requires data migration
- For hobby project: Easier to add new column than modify existing

### Deleting Columns
- BigQuery doesn't support dropping columns
- Workaround: Create new table without column, copy data
- For hobby project: Leave unused columns (they don't cost storage if NULL)

---

## Data Flow

```
User Upload (CSV)
    ↓
Streamlit App (Python)
    ↓
Parse & Enrich (add muscle groups)
    ↓
Authenticate (service account key)
    ↓
BigQuery Client (google-cloud-bigquery)
    ↓
BigQuery Table (workouts)
    ↓
Data Storage (europe-north1)
```

---

## Example Data

```json
{
  "datetime": "2025-01-15T09:00:00Z",
  "workout_name": "Push Day",
  "exercise_name": "Bench Press",
  "weight": 100.0,
  "reps": 8,
  "sets": 3,
  "notes": "Felt strong today",
  "duration_minutes": null,
  "muscle_group_level1": "upper",
  "muscle_group_level2": "chest",
  "upload_timestamp": "2025-01-15T18:30:00Z",
  "data_source": "csv_upload"
}
```

---

## Storage Estimates

**Assumptions**:
- Average row size: ~200 bytes (including BigQuery metadata)
- Workouts per week: 4
- Exercises per workout: 8
- Rows per week: 32

**Growth Projection**:
- Week: 32 rows × 200 bytes = 6.4 KB
- Month: 128 rows × 200 bytes = 25.6 KB
- Year: 1,664 rows × 200 bytes = 332.8 KB
- 10 Years: 16,640 rows × 200 bytes = 3.3 MB

**Free Tier Headroom**: 10 GB free tier / 3.3 MB (10 years) = **~3000 times headroom**

**Conclusion**: Storage will never be a concern for personal hobby use.

---

## Query Patterns

### Common Queries (for future app features):

1. **Recent workouts**: 
   ```sql
   SELECT * FROM workout_data.workouts 
   WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
   ORDER BY datetime DESC
   ```

2. **Muscle group summary**:
   ```sql
   SELECT muscle_group_level1, COUNT(*) as exercise_count
   FROM workout_data.workouts
   GROUP BY muscle_group_level1
   ```

3. **Exercise progress**:
   ```sql
   SELECT datetime, exercise_name, weight, reps
   FROM workout_data.workouts
   WHERE exercise_name = 'Bench Press'
   ORDER BY datetime
   ```

**Query Cost**: All queries within 1 TB/month free tier for hobby use.

---

## Next Steps

With data model defined, proceed to:
1. Create contracts (Terraform variables and outputs)
2. Implement Terraform configuration
3. Create quickstart guide
