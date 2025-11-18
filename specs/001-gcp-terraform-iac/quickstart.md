# Quickstart Guide: Deploy GCP Infrastructure with Terraform

**Feature**: 001-gcp-terraform-iac  
**Date**: 2025-11-18  
**Estimated Time**: 15-20 minutes

---

## Overview

This guide walks you through deploying the complete GCP infrastructure for the workout tracking application using Terraform. You'll create a BigQuery dataset, table, and service account with minimal setup.

---

## Prerequisites

### Required
- ✅ Google Cloud account (free tier eligible)
- ✅ [Terraform installed](https://www.terraform.io/downloads) (version >= 1.5.0)
- ✅ [gcloud CLI installed](https://cloud.google.com/sdk/docs/install)
- ✅ Basic terminal/command line knowledge

### Verify Installations
```bash
# Check Terraform version
terraform version
# Should show: Terraform v1.5.0 or higher

# Check gcloud CLI
gcloud --version
# Should show: Google Cloud SDK version
```

---

## Step 1: Create GCP Project (Manual - One Time)

**Why Manual**: Creating projects in Terraform requires organization-level permissions. Manual creation is simpler for hobby projects.

### 1.1 Login to GCP Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Sign in with your Google account

### 1.2 Create New Project
1. Click the project dropdown (top left, next to "Google Cloud")
2. Click "New Project"
3. Enter project details:
   - **Project Name**: `Workout Tracker` (display name)
   - **Project ID**: `workout-tracker-12345` (must be globally unique)
   - **Location**: Leave as "No organization" or select your org
4. Click "Create"
5. Wait for project creation (~30 seconds)

### 1.3 Enable Billing
1. Navigate to **Billing** in the left menu
2. Link a billing account (credit card required, but we'll stay in free tier)
3. Confirm billing is enabled for your project

### 1.4 Copy Your Project ID
```bash
# You'll need this exact project ID for Terraform
# Example: workout-tracker-12345
```

---

## Step 2: Authenticate gcloud CLI

### 2.1 Login
```bash
gcloud auth login
```
- This opens a browser for authentication
- Select your Google account
- Grant permissions

### 2.2 Set Application Default Credentials
```bash
gcloud auth application-default login
```
- This creates credentials for Terraform to use
- Opens browser again
- Grant permissions

### 2.3 Set Default Project
```bash
gcloud config set project YOUR_PROJECT_ID
# Replace YOUR_PROJECT_ID with your actual project ID
# Example: gcloud config set project workout-tracker-12345
```

### 2.4 Verify Authentication
```bash
gcloud config list
# Should show:
#   account = your-email@gmail.com
#   project = workout-tracker-12345
```

---

## Step 3: Clone Repository and Navigate to Terraform

```bash
# If you haven't already cloned the repo
git clone https://github.com/yourusername/gym-streamlit-dashboard.git
cd gym-streamlit-dashboard

# Switch to the infrastructure branch
git checkout 001-gcp-terraform-iac

# Navigate to Terraform directory
cd terraform
```

---

## Step 4: Configure Terraform Variables

### 4.1 Create terraform.tfvars File
```bash
# Copy the example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your favorite editor
nano terraform.tfvars
# Or: vim terraform.tfvars
# Or: code terraform.tfvars
```

### 4.2 Set Your Project ID
Edit `terraform.tfvars`:
```hcl
# Required: Your GCP project ID (from Step 1)
project_id = "workout-tracker-12345"  # ← Change this to YOUR project ID

# Optional: Override defaults (usually not needed)
# region                       = "europe-north1"
# dataset_id                   = "workout_data"
# table_id                     = "workouts"
# service_account_id           = "workout-app-sa"
```

**⚠️ Important**: Replace `workout-tracker-12345` with YOUR actual project ID!

### 4.3 Verify .gitignore
Ensure these lines exist in `.gitignore` (should already be there):
```gitignore
# Terraform
terraform/.terraform/
terraform/.terraform.lock.hcl
terraform/terraform.tfstate
terraform/terraform.tfstate.backup
terraform/*.tfvars
terraform/keys/

# Service account keys
*.json
!config/*.json
```

---

## Step 5: Initialize Terraform

### 5.1 Initialize
```bash
# From the terraform/ directory
terraform init
```

**Expected Output**:
```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/google versions matching "~> 5.0"...
- Installing hashicorp/google v5.x.x...

Terraform has been successfully initialized!
```

### 5.2 What This Does
- Downloads Google Cloud Provider plugin
- Sets up local backend for state file
- Prepares working directory

---

## Step 6: Preview Infrastructure Changes

### 6.1 Run Terraform Plan
```bash
terraform plan
```

**Expected Output** (summary):
```
Terraform will perform the following actions:

  # google_bigquery_dataset.workout_data will be created
  # google_bigquery_table.workouts will be created
  # google_project_service.bigquery will be created
  # google_project_service.iam will be created
  # google_service_account.app will be created
  # google_service_account_key.app_key will be created
  # google_project_iam_member.bigquery_data_editor will be created
  # google_project_iam_member.bigquery_job_user will be created
  # local_file.service_account_key will be created

Plan: 9 to add, 0 to change, 0 to destroy.
```

### 6.2 Review Changes
- Read through the plan
- Ensure project ID is correct
- Verify resources look right

---

## Step 7: Apply Infrastructure

### 7.1 Apply Changes
```bash
terraform apply
```

**Prompt**: 
```
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value:
```

**Type**: `yes` (then press Enter)

### 7.2 Wait for Completion
- Takes ~2-5 minutes
- You'll see progress for each resource
- Watch for any errors

### 7.3 Expected Success Output
```
Apply complete! Resources: 9 added, 0 changed, 0 destroyed.

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

## Step 8: Verify Infrastructure in GCP Console

### 8.1 Check BigQuery Dataset
1. Go to [BigQuery Console](https://console.cloud.google.com/bigquery)
2. You should see `workout_data` dataset in the left sidebar
3. Expand it to see `workouts` table
4. Click the table to view schema (13 columns)

### 8.2 Check Service Account
1. Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. You should see `workout-app-sa@...` service account
3. Click it to view roles:
   - ✅ BigQuery Data Editor
   - ✅ BigQuery Job User

### 8.3 Check Service Account Key File
```bash
# From terraform/ directory
ls -la keys/
# Should show: service-account-key.json

# View path (sensitive output)
terraform output -raw service_account_key_file
# Shows: ./keys/service-account-key.json
```

---

## Step 9: Configure Application

### 9.1 Copy Service Account Key
```bash
# From repository root
cd ..  # Go back to project root
mkdir -p .credentials
cp terraform/keys/service-account-key.json .credentials/
```

### 9.2 Create .env File
```bash
# Create .env file at project root
cat > .env << 'EOF'
# GCP Configuration
GCP_PROJECT_ID=workout-tracker-12345
GOOGLE_APPLICATION_CREDENTIALS=./.credentials/service-account-key.json

# BigQuery Configuration
BQ_DATASET_ID=workout_data
BQ_TABLE_ID=workouts
EOF
```

**⚠️ Important**: Replace `workout-tracker-12345` with YOUR project ID!

### 9.3 Update config/bigquery_config.yaml
Edit `config/bigquery_config.yaml`:
```yaml
connection:
  project_id: "${GCP_PROJECT_ID}"
  dataset_id: "workout_data"
  table_id: "workouts"
  credentials_path: "${GOOGLE_APPLICATION_CREDENTIALS}"
```

---

## Step 10: Test Connection (Optional)

### 10.1 Test with Python Script
```bash
# Create quick test script
cat > test_bigquery.py << 'EOF'
from google.cloud import bigquery
import os
from dotenv import load_dotenv

load_dotenv()

client = bigquery.Client.from_service_account_json(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)

project_id = os.getenv("GCP_PROJECT_ID")
dataset_id = os.getenv("BQ_DATASET_ID")
table_id = os.getenv("BQ_TABLE_ID")

table_ref = f"{project_id}.{dataset_id}.{table_id}"
table = client.get_table(table_ref)

print(f"✅ Connected to BigQuery!")
print(f"📊 Table: {table_ref}")
print(f"📝 Columns: {len(table.schema)}")
print(f"📦 Rows: {table.num_rows}")
EOF

# Run test
python test_bigquery.py
```

**Expected Output**:
```
✅ Connected to BigQuery!
📊 Table: workout-tracker-12345.workout_data.workouts
📝 Columns: 13
📦 Rows: 0
```

---

## Troubleshooting

### Error: "Project ID does not exist"
**Solution**: Double-check project ID in `terraform.tfvars` matches GCP Console

### Error: "Billing must be enabled"
**Solution**: Go to GCP Console → Billing → Enable billing for project

### Error: "Permission denied"
**Solution**: 
```bash
# Re-authenticate
gcloud auth application-default login
gcloud auth login
```

### Error: "API not enabled"
**Solution**: Terraform should auto-enable APIs, but you can manually enable:
```bash
gcloud services enable bigquery.googleapis.com
gcloud services enable iam.googleapis.com
```

### Service Account Key Not Created
**Solution**:
```bash
# Check Terraform state
terraform state list | grep service_account_key

# Re-run apply
terraform apply
```

---

## Maintenance

### View Infrastructure State
```bash
# List all resources
terraform state list

# Show specific resource
terraform show
```

### Update Infrastructure
```bash
# Make changes to .tf files
# Preview changes
terraform plan

# Apply changes
terraform apply
```

### Destroy Infrastructure (⚠️ Destructive)
```bash
# ⚠️ This deletes ALL resources including data!
terraform destroy

# Type 'yes' to confirm
```

---

## Cost Monitoring

### Set Up Billing Alerts
1. Go to [Billing](https://console.cloud.google.com/billing)
2. Click "Budgets & alerts"
3. Create budget:
   - Amount: $5/month
   - Alert threshold: 50%, 90%, 100%
4. Add your email for alerts

### Monitor Usage
```bash
# Check BigQuery storage
gcloud alpha bq datasets describe workout_data --project=YOUR_PROJECT_ID

# View BigQuery queries (last 7 days)
gcloud logging read "resource.type=bigquery_resource" --limit 50
```

### Expected Costs
- **Free Tier**: $0/month for typical hobby use
- **Storage**: 10 GB free (we use <100 MB)
- **Queries**: 1 TB/month free (we use <1 GB)

---

## Security Best Practices

### ✅ Do
- Keep service account key secure
- Add keys to .gitignore
- Enable billing alerts
- Use least privilege roles (already configured)
- Rotate service account keys periodically

### ❌ Don't
- Commit service account keys to git
- Share keys publicly
- Use admin roles unnecessarily
- Leave billing unmonitored

---

## Next Steps

1. ✅ Infrastructure deployed
2. ▶️ Run Streamlit app: `streamlit run app.py`
3. ▶️ Upload workout data via UI
4. ▶️ Verify data in BigQuery console

---

## Getting Help

- **Terraform Docs**: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- **BigQuery Docs**: https://cloud.google.com/bigquery/docs
- **GCP Free Tier**: https://cloud.google.com/free

---

**🎉 Congratulations! Your GCP infrastructure is now live!**
