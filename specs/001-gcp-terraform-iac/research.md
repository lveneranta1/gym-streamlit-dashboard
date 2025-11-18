# Research: GCP Terraform Infrastructure for Hobby Project

**Date**: 2025-11-18  
**Feature**: 001-gcp-terraform-iac  
**Purpose**: Resolve NEEDS CLARIFICATION items and document technical decisions

---

## Research Items

### 1. GCP Free Tier Limits for BigQuery in europe-north1

**Decision**: Use BigQuery in europe-north1 (Finland) with free tier limitations

**Rationale**:
- BigQuery free tier provides:
  - **10 GB storage per month** (free)
  - **1 TB of queries per month** (free)
  - First 10 GB of storage is always free
  - First 1 TB of query data processed per month is free
- europe-north1 (Finland) is the closest EU region to Sweden with full BigQuery support
- BigQuery pricing is the same across all regions
- For a hobby workout tracking app, 10 GB storage is sufficient for years of data
  - Assuming 1 KB per workout entry
  - 10 GB = ~10 million workout entries
- 1 TB query limit is more than sufficient for hobby use

**Alternatives considered**:
- europe-north1 (Finland) - CHOSEN: Closest to Sweden, full features
- europe-west1 (Belgium) - Also good, slightly farther
- US regions - Not chosen due to data residency preferences

**Source**: [GCP BigQuery Pricing](https://cloud.google.com/bigquery/pricing)

---

### 2. Minimum Required IAM Roles for BigQuery Service Account

**Decision**: Use two minimal roles: `roles/bigquery.dataEditor` and `roles/bigquery.jobUser`

**Rationale**:
- **bigquery.dataEditor**: Allows reading and writing table data, managing table schemas
  - Includes: bigquery.tables.get, bigquery.tables.update, bigquery.tables.getData, bigquery.tables.updateData
  - Does NOT include: Creating datasets or tables (we create these with Terraform)
- **bigquery.jobUser**: Allows running queries and load jobs
  - Required to execute INSERT/SELECT queries
  - Allows creating jobs to load data
- These are the minimum roles needed for the application to function
- We avoid broader roles like `bigquery.admin` or `bigquery.user` which grant unnecessary permissions

**Alternatives considered**:
- `roles/bigquery.admin` - Too broad, grants dataset/table creation rights (not needed)
- `roles/bigquery.user` - Allows creating datasets (not needed, Terraform handles this)
- Custom role - Overkill for hobby project, harder to maintain

**Best Practice**: Grant least privilege - only what the application needs to write and read data.

**Source**: [GCP BigQuery IAM Roles](https://cloud.google.com/bigquery/docs/access-control)

---

### 3. Project Creation in Terraform vs Pre-existing Project

**Decision**: Assume pre-existing GCP project, do NOT create project in Terraform

**Rationale**:
- **Creating projects in Terraform requires**:
  - Organization or Folder resource (not available in free tier personal accounts)
  - Billing account linkage (requires billing account admin role)
  - API enablement at organization level (complex permissions)
- **For hobby projects**:
  - Users typically create projects manually via GCP Console (one-time, 5 minutes)
  - Manual project creation allows selecting billing account visually
  - Simpler to troubleshoot billing and permissions issues
- **Terraform will**:
  - Take existing project ID as input variable
  - Enable required APIs on that project
  - Create resources within the project

**Alternatives considered**:
- Create project in Terraform - Rejected: Requires organization setup, complex permissions, not hobby-friendly
- Use `google_project` resource - Rejected: Requires billing account admin, organization structure

**Implementation**:
```hcl
variable "project_id" {
  description = "Existing GCP project ID (create manually in console)"
  type        = string
}
```

**User Manual Steps** (documented in quickstart):
1. Go to GCP Console → Create new project
2. Link billing account to project
3. Copy project ID
4. Use project ID in terraform.tfvars

---

### 4. Managing Service Account Keys in Terraform for Hobby Projects

**Decision**: Generate service account key with Terraform, output to local file, add to .gitignore

**Rationale**:
- **For hobby projects**: Local key file is acceptable and simplest
- **Terraform approach**:
  - Use `google_service_account_key` resource
  - Generate private key in JSON format
  - Output key as base64, decode to file using `local_file` resource
  - Store in `terraform/keys/` directory (gitignored)
- **Security considerations**:
  - Key file never committed to git (.gitignore)
  - User responsible for securing their local machine
  - For hobby project, this is pragmatic balance of security and simplicity
- **Production alternative**: Use Workload Identity or GKE/Cloud Run service account binding (not applicable here)

**Alternatives considered**:
- Manual key creation - Rejected: Defeats purpose of Infrastructure as Code
- Secret Manager - Rejected: Overkill for single-user hobby project, adds complexity
- Workload Identity - Rejected: Requires Kubernetes/Cloud Run, not applicable to Streamlit app

**Implementation**:
```hcl
resource "google_service_account_key" "app_key" {
  service_account_id = google_service_account.app.name
}

resource "local_file" "service_account_key" {
  content  = base64decode(google_service_account_key.app_key.private_key)
  filename = "${path.module}/keys/service-account-key.json"
}
```

**Security Note in Documentation**: Keep service-account-key.json secure, never commit to git.

---

## Technology Stack Summary

| Component | Technology | Version/Constraint |
|-----------|------------|-------------------|
| IaC Tool | Terraform | >= 1.5.0 |
| Provider | Google Cloud Provider | ~> 5.0 |
| Cloud Platform | GCP | N/A |
| Region | europe-north1 | Finland (closest to Sweden) |
| Storage | BigQuery | Free tier (10 GB) |
| Authentication | Service Account Key | JSON key file |
| State Backend | Local | terraform.tfstate (local file) |

---

## Implementation Architecture

```
User's Local Machine
│
├─ Terraform Configuration (terraform/)
│  ├─ main.tf (resources)
│  ├─ variables.tf (inputs)
│  ├─ outputs.tf (project info)
│  ├─ terraform.tfvars (user values)
│  └─ terraform.tfstate (local state)
│
├─ Generated Keys (terraform/keys/)
│  └─ service-account-key.json (gitignored)
│
│
▼ terraform apply
│
│
Google Cloud Platform (GCP)
│
├─ Existing Project (manual creation)
│  ├─ Enabled APIs
│  │  ├─ BigQuery API
│  │  └─ IAM API
│  │
│  ├─ BigQuery
│  │  └─ Dataset: workout_data
│  │     └─ Table: workouts
│  │        └─ Schema (13 columns)
│  │
│  └─ Service Account
│     ├─ Email: app-sa@{project}.iam.gserviceaccount.com
│     └─ Roles:
│        ├─ bigquery.dataEditor
│        └─ bigquery.jobUser
```

---

## Cost Analysis

| Resource | Free Tier | Expected Usage | Cost |
|----------|-----------|----------------|------|
| BigQuery Storage | 10 GB/month | <100 MB | **$0** |
| BigQuery Queries | 1 TB/month | <1 GB/month | **$0** |
| Service Account | No limit | 1 account | **$0** |
| API Calls | Quota limits | Minimal | **$0** |
| **Total** | | | **$0/month** |

---

## Risk Mitigation

### Risk 1: Exceeding Free Tier
- **Likelihood**: Very Low
- **Impact**: Low ($5-10/month if exceeded)
- **Mitigation**: 
  - Set up billing alerts in GCP Console
  - Monitor BigQuery usage in console
  - For hobby project, 10 GB is 2-3 years of data

### Risk 2: Service Account Key Exposure
- **Likelihood**: Medium (if user commits key)
- **Impact**: High (unauthorized data access)
- **Mitigation**:
  - Strong .gitignore rules
  - Documentation warnings
  - Key rotation instructions in README

### Risk 3: Terraform State File Loss
- **Likelihood**: Medium (local file)
- **Impact**: Medium (resources orphaned)
- **Mitigation**:
  - Backup instructions in README
  - Resources can be imported back to Terraform
  - Document state recovery procedures

---

## Decisions Summary

1. ✅ **Use europe-north1** for BigQuery (free tier, close to Sweden)
2. ✅ **Minimum IAM**: dataEditor + jobUser roles only
3. ✅ **Pre-existing project**: User creates project manually
4. ✅ **Local service account key**: Generated by Terraform, stored locally
5. ✅ **Local state**: terraform.tfstate stored locally (no remote backend)
6. ✅ **Flat structure**: No Terraform modules, keep it simple

---

**Next Steps**: Proceed to Phase 1 - Design data model and contracts
