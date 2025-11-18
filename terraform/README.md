# Terraform Infrastructure for GCP

This directory contains Terraform configuration to provision Google Cloud Platform infrastructure for the workout tracking application.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.5.0
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- Google Cloud account with billing enabled
- Existing GCP project (create manually in console)

## Quick Start

### 1. Authenticate with GCP

```bash
# Login to GCP
gcloud auth login

# Set application default credentials for Terraform
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Configure Variables

```bash
# Copy the example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your project ID
nano terraform.tfvars  # or vim, code, etc.
```

**Required**: Set `project_id` to your GCP project ID.

### 3. Initialize Terraform

```bash
terraform init
```

This downloads the Google Cloud Provider plugin.

### 4. Preview Changes

```bash
terraform plan
```

Review the resources that will be created.

### 5. Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted. Deployment takes ~2-5 minutes.

### 6. Get Outputs

```bash
# View all outputs
terraform output

# Get specific output
terraform output project_id
terraform output service_account_key_file
```

## What Gets Created

- **BigQuery Dataset**: `workout_data` in europe-north1
- **BigQuery Table**: `workouts` with 13-column schema
- **Service Account**: For application authentication
- **Service Account Key**: JSON credentials file
- **IAM Roles**: Minimal permissions (dataEditor + jobUser)
- **Enabled APIs**: BigQuery API, IAM API

**Total Resources**: 9

## Configuration

### Input Variables

See `variables.tf` for all available variables. Most have sensible defaults.

**Required**:
- `project_id`: Your GCP project ID

**Optional** (with defaults):
- `region`: Default `europe-north1`
- `dataset_id`: Default `workout_data`
- `table_id`: Default `workouts`
- `service_account_id`: Default `workout-app-sa`

### Outputs

After `terraform apply`, these values are available:

- `project_id`: GCP project ID
- `dataset_id`: Full BigQuery dataset ID
- `table_id`: Full BigQuery table ID
- `service_account_email`: Service account email
- `service_account_key_file`: Path to credentials file (sensitive)
- `bigquery_dataset_location`: Dataset region
- `api_enabled`: List of enabled APIs

## Using the Credentials

The service account key is saved to `keys/service-account-key.json`.

**For the Streamlit app**, update your `.env` file:

```bash
# Get the path to the key file
KEY_PATH=$(terraform output -raw service_account_key_file)

# Update .env (at repository root)
cat > ../.env << EOF
GCP_PROJECT_ID=$(terraform output -raw project_id)
GOOGLE_APPLICATION_CREDENTIALS=./terraform/keys/service-account-key.json
BQ_DATASET_ID=workout_data
BQ_TABLE_ID=workouts
EOF
```

## Updating Infrastructure

```bash
# Make changes to .tf files
# Preview changes
terraform plan

# Apply changes
terraform apply
```

## Destroying Infrastructure

⚠️ **Warning**: This deletes ALL resources including data!

```bash
terraform destroy
```

Type `yes` to confirm. This removes:
- BigQuery dataset and table (including all data)
- Service account and keys
- IAM role bindings

The GCP project itself is NOT deleted (it was pre-existing).

## Troubleshooting

### Error: "Project does not exist"

**Solution**: Verify `project_id` in `terraform.tfvars` matches your GCP project ID exactly.

```bash
# Check your current project
gcloud config get-value project
```

### Error: "Billing must be enabled"

**Solution**: Enable billing for your project in [GCP Console](https://console.cloud.google.com/billing).

### Error: "Permission denied"

**Solution**: Re-authenticate with gcloud:

```bash
gcloud auth application-default login
gcloud auth login
```

Ensure you have Owner or Editor role on the project.

### Error: "API not enabled"

**Solution**: Terraform should auto-enable APIs, but you can manually enable:

```bash
gcloud services enable bigquery.googleapis.com
gcloud services enable iam.googleapis.com
```

### Service Account Key Not Created

**Check Terraform state**:

```bash
terraform state list | grep service_account_key
```

**Re-run apply**:

```bash
terraform apply
```

## File Structure

```
terraform/
├── main.tf                      # All resources
├── variables.tf                 # Input variables
├── outputs.tf                   # Output values
├── versions.tf                  # Provider constraints
├── terraform.tfvars.example     # Example configuration
├── README.md                    # This file
├── keys/                        # Generated credentials (gitignored)
│   └── service-account-key.json
├── .terraform/                  # Provider plugins (gitignored)
├── terraform.tfstate            # State file (gitignored)
└── terraform.tfstate.backup     # State backup (gitignored)
```

## Cost

**Expected Cost**: $0/month (Free Tier)

- BigQuery storage: First 10 GB free
- BigQuery queries: First 1 TB/month free
- Service accounts: Free

**Recommendation**: Set up [billing alerts](https://console.cloud.google.com/billing) at $5/month as a safety net.

## Security

### Best Practices

✅ **Do**:
- Keep service account keys secure
- Never commit keys to git (already in .gitignore)
- Rotate keys periodically
- Use least privilege permissions (already configured)
- Enable billing alerts

❌ **Don't**:
- Share keys publicly
- Commit `terraform.tfvars` with real values
- Use admin roles unnecessarily
- Leave billing unmonitored

### Key Rotation

To rotate the service account key:

```bash
# Destroy current key
terraform destroy -target=google_service_account_key.app_key
terraform destroy -target=local_file.service_account_key

# Create new key
terraform apply
```

## State Management

This configuration uses **local state** (terraform.tfstate) for simplicity.

**Backup your state file**:

```bash
cp terraform.tfstate terraform.tfstate.backup.$(date +%Y%m%d)
```

**For production**, consider using [remote state](https://www.terraform.io/docs/language/state/remote.html) with GCS.

## Additional Resources

- [Terraform GCP Provider Docs](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [GCP Free Tier](https://cloud.google.com/free)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)

## Support

For issues specific to this Terraform configuration, see:
- Repository README
- `specs/001-gcp-terraform-iac/quickstart.md` for detailed deployment guide
- `specs/001-gcp-terraform-iac/research.md` for technical decisions

---

**Version**: 1.0  
**Created**: 2025-11-18  
**Feature**: 001-gcp-terraform-iac
