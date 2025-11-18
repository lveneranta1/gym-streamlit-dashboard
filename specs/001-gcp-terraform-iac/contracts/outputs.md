# Terraform Output Values Contract

**Feature**: 001-gcp-terraform-iac  
**Date**: 2025-11-18  
**Purpose**: Define output values exposed after Terraform apply

---

## Overview

After `terraform apply` completes, these values are displayed and can be referenced by other systems or documentation.

---

## Output Values

### `project_id`

**Type**: `string`

**Description**: The GCP project ID where resources were created

**Sensitivity**: Non-sensitive

**Example**: `"workout-tracker-12345"`

**Usage**:
```hcl
output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}
```

**Purpose**: Confirmation of which project resources were created in

---

### `dataset_id`

**Type**: `string`

**Description**: Full BigQuery dataset identifier

**Format**: `{project_id}.{dataset_id}`

**Sensitivity**: Non-sensitive

**Example**: `"workout-tracker-12345.workout_data"`

**Usage**:
```hcl
output "dataset_id" {
  description = "BigQuery dataset full ID"
  value       = google_bigquery_dataset.workout_data.id
}
```

**Purpose**: Used in application configuration to specify dataset location

---

### `table_id`

**Type**: `string`

**Description**: Full BigQuery table identifier

**Format**: `{project_id}.{dataset_id}.{table_id}`

**Sensitivity**: Non-sensitive

**Example**: `"workout-tracker-12345.workout_data.workouts"`

**Usage**:
```hcl
output "table_id" {
  description = "BigQuery table full ID"
  value       = google_bigquery_table.workouts.id
}
```

**Purpose**: Used in application configuration to specify table for queries

---

### `service_account_email`

**Type**: `string`

**Description**: Email address of created service account

**Format**: `{service_account_id}@{project_id}.iam.gserviceaccount.com`

**Sensitivity**: Non-sensitive

**Example**: `"workout-app-sa@workout-tracker-12345.iam.gserviceaccount.com"`

**Usage**:
```hcl
output "service_account_email" {
  description = "Service account email for application authentication"
  value       = google_service_account.app.email
}
```

**Purpose**: Reference for identifying which service account is being used

---

### `service_account_key_file`

**Type**: `string`

**Description**: Local filesystem path to generated service account key JSON file

**Format**: `{terraform_dir}/keys/service-account-key.json`

**Sensitivity**: **SENSITIVE** (path reveals key location)

**Example**: `"./keys/service-account-key.json"`

**Usage**:
```hcl
output "service_account_key_file" {
  description = "Path to service account key file (KEEP SECURE)"
  value       = local_file.service_account_key.filename
  sensitive   = true
}
```

**Purpose**: Tells user where to find the key file for application configuration

**Security Note**: 
- Marked as sensitive (not displayed in terminal by default)
- User must run `terraform output -raw service_account_key_file` to view
- Key file itself must be secured and never committed to git

---

### `bigquery_dataset_location`

**Type**: `string`

**Description**: Geographic location where BigQuery dataset is stored

**Sensitivity**: Non-sensitive

**Example**: `"europe-north1"`

**Usage**:
```hcl
output "bigquery_dataset_location" {
  description = "BigQuery dataset location/region"
  value       = google_bigquery_dataset.workout_data.location
}
```

**Purpose**: Confirms dataset location for data residency verification

---

### `api_enabled`

**Type**: `list(string)`

**Description**: List of GCP APIs that were enabled

**Sensitivity**: Non-sensitive

**Example**: `["bigquery.googleapis.com", "iam.googleapis.com"]`

**Usage**:
```hcl
output "api_enabled" {
  description = "List of enabled GCP APIs"
  value       = [for api in google_project_service.apis : api.service]
}
```

**Purpose**: Documentation and verification of which APIs are active

---

## Output Display Format

After `terraform apply`, outputs display like:

```
Apply complete! Resources: 7 added, 0 changed, 0 destroyed.

Outputs:

api_enabled = [
  "bigquery.googleapis.com",
  "iam.googleapis.com",
]
bigquery_dataset_location = "europe-north1"
dataset_id = "workout-tracker-12345.workout_data"
project_id = "workout-tracker-12345"
service_account_email = "workout-app-sa@workout-tracker-12345.iam.gserviceaccount.com"
service_account_key_file = <sensitive>
table_id = "workout-tracker-12345.workout_data.workouts"
```

---

## Accessing Outputs

### View all outputs:
```bash
terraform output
```

### View specific output:
```bash
terraform output project_id
```

### View sensitive output:
```bash
terraform output -raw service_account_key_file
```

### Export to JSON:
```bash
terraform output -json > outputs.json
```

### Use in scripts:
```bash
PROJECT_ID=$(terraform output -raw project_id)
TABLE_ID=$(terraform output -raw table_id)
KEY_FILE=$(terraform output -raw service_account_key_file)
```

---

## Application Configuration Usage

After Terraform apply, user updates application `.env` file:

```bash
# From Terraform outputs
GCP_PROJECT_ID=$(terraform output -raw project_id)
GOOGLE_APPLICATION_CREDENTIALS=$(terraform output -raw service_account_key_file)
BQ_DATASET_ID="workout_data"
BQ_TABLE_ID="workouts"
```

Or manually:

```env
# .env file for Streamlit app
GCP_PROJECT_ID=workout-tracker-12345
GOOGLE_APPLICATION_CREDENTIALS=./terraform/keys/service-account-key.json
BQ_DATASET_ID=workout_data
BQ_TABLE_ID=workouts
```

---

## Output JSON Schema

For programmatic access, outputs can be exported as JSON:

```json
{
  "api_enabled": {
    "sensitive": false,
    "type": ["list", "string"],
    "value": [
      "bigquery.googleapis.com",
      "iam.googleapis.com"
    ]
  },
  "bigquery_dataset_location": {
    "sensitive": false,
    "type": "string",
    "value": "europe-north1"
  },
  "dataset_id": {
    "sensitive": false,
    "type": "string",
    "value": "workout-tracker-12345.workout_data"
  },
  "project_id": {
    "sensitive": false,
    "type": "string",
    "value": "workout-tracker-12345"
  },
  "service_account_email": {
    "sensitive": false,
    "type": "string",
    "value": "workout-app-sa@workout-tracker-12345.iam.gserviceaccount.com"
  },
  "service_account_key_file": {
    "sensitive": true,
    "type": "string",
    "value": "./keys/service-account-key.json"
  },
  "table_id": {
    "sensitive": false,
    "type": "string",
    "value": "workout-tracker-12345.workout_data.workouts"
  }
}
```

---

## Output Summary Table

| Output Name | Type | Sensitive | Purpose |
|-------------|------|-----------|---------|
| `project_id` | string | No | GCP project identifier |
| `dataset_id` | string | No | BigQuery dataset full ID |
| `table_id` | string | No | BigQuery table full ID |
| `service_account_email` | string | No | Service account identity |
| `service_account_key_file` | string | **Yes** | Path to credentials file |
| `bigquery_dataset_location` | string | No | Dataset region |
| `api_enabled` | list(string) | No | Enabled GCP APIs |

---

## Next: See [quickstart.md](../quickstart.md) for deployment instructions
