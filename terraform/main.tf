# ============================================================================
# GCP Infrastructure for Workout Tracking Application
# Feature: 001-gcp-terraform-iac
# ============================================================================

# ----------------------------------------------------------------------------
# Data Sources
# ----------------------------------------------------------------------------

data "google_project" "project" {
  project_id = var.project_id
}

# ----------------------------------------------------------------------------
# Enable Required APIs
# ----------------------------------------------------------------------------

resource "google_project_service" "apis" {
  for_each = toset([
    "bigquery.googleapis.com",
    "iam.googleapis.com",
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# ----------------------------------------------------------------------------
# BigQuery Dataset
# ----------------------------------------------------------------------------

resource "google_bigquery_dataset" "workout_data" {
  dataset_id  = var.dataset_id
  location    = var.region
  description = "Workout tracking data storage"

  # Ensure APIs are enabled first
  depends_on = [google_project_service.apis]
}

# ----------------------------------------------------------------------------
# BigQuery Table with Schema
# ----------------------------------------------------------------------------

resource "google_bigquery_table" "workouts" {
  dataset_id = google_bigquery_dataset.workout_data.dataset_id
  table_id   = var.table_id

  description = "Workout exercise records with muscle group enrichment"

  schema = jsonencode([
    {
      name        = "date"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Date and time of the workout/exercise"
    },
    {
      name        = "workout_name"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Name or type of workout session"
    },
    {
      name        = "exercise_name"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Name of the exercise performed"
    },
    {
      name        = "weight_kg"
      type        = "FLOAT64"
      mode        = "REQUIRED"
      description = "Weight used in kilograms"
    },
    {
      name        = "weight_lb"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "Weight used in pounds"
    },
    {
      name        = "reps"
      type        = "INT64"
      mode        = "REQUIRED"
      description = "Number of repetitions"
    },
    {
      name        = "notes"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Additional notes about the exercise"
    },
    {
      name        = "duration"
      type        = "INT64"
      mode        = "NULLABLE"
      description = "Duration of exercise in minutes"
    },
    {
      name        = "upload_timestamp"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Timestamp when data was uploaded to BigQuery"
    },
    {
      name        = "data_source"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Source of the data (e.g., csv_upload)"
    },
  ])

  depends_on = [google_bigquery_dataset.workout_data]
}

# ----------------------------------------------------------------------------
# Service Account
# ----------------------------------------------------------------------------

resource "google_service_account" "app" {
  account_id   = var.service_account_id
  display_name = var.service_account_display_name
  description  = "Service account for workout app to access BigQuery"

  # Ensure APIs are enabled first
  depends_on = [google_project_service.apis]
}

# ----------------------------------------------------------------------------
# Service Account Key
# ----------------------------------------------------------------------------

resource "google_service_account_key" "app_key" {
  service_account_id = google_service_account.app.name
}

# ----------------------------------------------------------------------------
# IAM Role Bindings
# ----------------------------------------------------------------------------

# Grant BigQuery Data Editor role (read/write table data)
resource "google_project_iam_member" "bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.app.email}"

  depends_on = [google_service_account.app]
}

# Grant BigQuery Job User role (execute queries and load jobs)
resource "google_project_iam_member" "bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.app.email}"

  depends_on = [google_service_account.app]
}

# ----------------------------------------------------------------------------
# Save Service Account Key to Local File
# ----------------------------------------------------------------------------

resource "local_file" "service_account_key" {
  content  = base64decode(google_service_account_key.app_key.private_key)
  filename = "${path.module}/keys/service-account-key.json"

  # Set restrictive permissions (owner read/write only)
  file_permission = "0600"

  depends_on = [google_service_account_key.app_key]
}
