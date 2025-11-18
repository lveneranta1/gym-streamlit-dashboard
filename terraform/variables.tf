variable "project_id" {
  description = "Existing GCP project ID (create manually in console first)"
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "Project ID must be 6-30 characters, start with letter, contain only lowercase letters, digits, and hyphens."
  }
}

variable "region" {
  description = "GCP region for BigQuery dataset (default: europe-north1 for free tier)"
  type        = string
  default     = "europe-north1"

  validation {
    condition     = can(regex("^[a-z]+-[a-z]+[0-9]$", var.region))
    error_message = "Region must be a valid GCP region (e.g., europe-north1)."
  }
}

variable "dataset_id" {
  description = "BigQuery dataset name for workout data"
  type        = string
  default     = "workout_data"

  validation {
    condition     = can(regex("^[a-zA-Z0-9_]+$", var.dataset_id)) && length(var.dataset_id) >= 1 && length(var.dataset_id) <= 1024
    error_message = "Dataset ID must contain only letters, numbers, and underscores (1-1024 chars)."
  }
}

variable "table_id" {
  description = "BigQuery table name for workout records"
  type        = string
  default     = "workouts"

  validation {
    condition     = can(regex("^[a-zA-Z0-9_]+$", var.table_id)) && length(var.table_id) >= 1 && length(var.table_id) <= 1024
    error_message = "Table ID must contain only letters, numbers, and underscores (1-1024 chars)."
  }
}

variable "service_account_id" {
  description = "Service account ID for application authentication"
  type        = string
  default     = "workout-app-sa"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.service_account_id))
    error_message = "Service account ID must be 6-30 characters, start with letter, contain only lowercase letters, digits, and hyphens."
  }
}

variable "service_account_display_name" {
  description = "Display name for service account"
  type        = string
  default     = "Workout App Service Account"
}
