output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}

output "dataset_id" {
  description = "BigQuery dataset full ID"
  value       = google_bigquery_dataset.workout_data.id
}

output "table_id" {
  description = "BigQuery table full ID"
  value       = google_bigquery_table.workouts.id
}

output "service_account_email" {
  description = "Service account email for application authentication"
  value       = google_service_account.app.email
}

output "service_account_key_file" {
  description = "Path to service account key file (KEEP SECURE)"
  value       = local_file.service_account_key.filename
  sensitive   = true
}

output "bigquery_dataset_location" {
  description = "BigQuery dataset location/region"
  value       = google_bigquery_dataset.workout_data.location
}

output "api_enabled" {
  description = "List of enabled GCP APIs"
  value       = [for api in google_project_service.apis : api.service]
}
