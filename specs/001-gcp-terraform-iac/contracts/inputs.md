# Terraform Input Variables Contract

**Feature**: 001-gcp-terraform-iac  
**Date**: 2025-11-18  
**Purpose**: Define required and optional input variables for Terraform configuration

---

## Required Variables

### `project_id`

**Type**: `string`

**Description**: Existing Google Cloud Project ID where resources will be created

**Validation**:
- Must be 6-30 characters
- Must contain only lowercase letters, digits, and hyphens
- Must start with a letter
- Must be globally unique in GCP
- Project must already exist (created manually)

**Example**: `"workout-tracker-12345"`

**Usage**:
```hcl
variable "project_id" {
  description = "Existing GCP project ID (create manually in console first)"
  type        = string
  
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "Project ID must be 6-30 characters, start with letter, contain only lowercase letters, digits, and hyphens."
  }
}
```

---

### `region`

**Type**: `string`

**Description**: GCP region for BigQuery dataset

**Default**: `"europe-north1"`

**Validation**:
- Must be a valid GCP region
- Should use europe-north1 for free tier and proximity to Sweden

**Example**: `"europe-north1"`

**Usage**:
```hcl
variable "region" {
  description = "GCP region for BigQuery dataset (default: europe-north1 for free tier)"
  type        = string
  default     = "europe-north1"
  
  validation {
    condition     = can(regex("^[a-z]+-[a-z]+[0-9]$", var.region))
    error_message = "Region must be a valid GCP region (e.g., europe-north1)."
  }
}
```

---

## Optional Variables with Defaults

### `dataset_id`

**Type**: `string`

**Description**: BigQuery dataset name

**Default**: `"workout_data"`

**Validation**:
- Must be alphanumeric or underscores
- Must be 1-1024 characters

**Example**: `"workout_data"`

**Usage**:
```hcl
variable "dataset_id" {
  description = "BigQuery dataset name for workout data"
  type        = string
  default     = "workout_data"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9_]{1,1024}$", var.dataset_id))
    error_message = "Dataset ID must contain only letters, numbers, and underscores (1-1024 chars)."
  }
}
```

---

### `table_id`

**Type**: `string`

**Description**: BigQuery table name for workout records

**Default**: `"workouts"`

**Validation**:
- Must be alphanumeric or underscores
- Must be 1-1024 characters

**Example**: `"workouts"`

**Usage**:
```hcl
variable "table_id" {
  description = "BigQuery table name for workout records"
  type        = string
  default     = "workouts"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9_]{1,1024}$", var.table_id))
    error_message = "Table ID must contain only letters, numbers, and underscores (1-1024 chars)."
  }
}
```

---

### `service_account_id`

**Type**: `string`

**Description**: Service account identifier for application authentication

**Default**: `"workout-app-sa"`

**Validation**:
- Must be 6-30 characters
- Must contain only lowercase letters, digits, and hyphens
- Must start with lowercase letter

**Example**: `"workout-app-sa"`

**Usage**:
```hcl
variable "service_account_id" {
  description = "Service account ID for application authentication"
  type        = string
  default     = "workout-app-sa"
  
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.service_account_id))
    error_message = "Service account ID must be 6-30 characters, start with letter, contain only lowercase letters, digits, and hyphens."
  }
}
```

---

### `service_account_display_name`

**Type**: `string`

**Description**: Human-readable display name for service account

**Default**: `"Workout App Service Account"`

**Example**: `"Workout App Service Account"`

**Usage**:
```hcl
variable "service_account_display_name" {
  description = "Display name for service account"
  type        = string
  default     = "Workout App Service Account"
}
```

---

## Variable File Example

### `terraform.tfvars` (user creates this)

```hcl
# Required: Your GCP project ID (created manually in console)
project_id = "my-workout-tracker-2025"

# Optional: Override defaults if needed
# region                       = "europe-north1"
# dataset_id                   = "workout_data"
# table_id                     = "workouts"
# service_account_id           = "workout-app-sa"
# service_account_display_name = "Workout App Service Account"
```

---

## Environment Variables (Alternative)

Instead of `terraform.tfvars`, users can set environment variables:

```bash
export TF_VAR_project_id="my-workout-tracker-2025"
export TF_VAR_region="europe-north1"
export TF_VAR_dataset_id="workout_data"
export TF_VAR_table_id="workouts"
```

---

## Variable Precedence (Terraform Standard)

1. Command line flags: `-var project_id=...`
2. `terraform.tfvars` file
3. `terraform.tfvars.json` file
4. `*.auto.tfvars` files (alphabetical order)
5. Environment variables: `TF_VAR_*`
6. Variable defaults in configuration

---

## Security Considerations

- **Never commit `terraform.tfvars`** with real values (add to .gitignore)
- Provide `terraform.tfvars.example` with placeholder values
- Document that `project_id` should be user-specific
- Service account key generated by Terraform (not input variable)

---

## Validation Rules Summary

| Variable | Pattern | Length | Example |
|----------|---------|--------|---------|
| `project_id` | `^[a-z][a-z0-9-]{4,28}[a-z0-9]$` | 6-30 | workout-tracker-12345 |
| `region` | `^[a-z]+-[a-z]+[0-9]$` | N/A | europe-north1 |
| `dataset_id` | `^[a-zA-Z0-9_]{1,1024}$` | 1-1024 | workout_data |
| `table_id` | `^[a-zA-Z0-9_]{1,1024}$` | 1-1024 | workouts |
| `service_account_id` | `^[a-z][a-z0-9-]{4,28}[a-z0-9]$` | 6-30 | workout-app-sa |

---

## Next: See [outputs.md](./outputs.md) for Terraform output contract
