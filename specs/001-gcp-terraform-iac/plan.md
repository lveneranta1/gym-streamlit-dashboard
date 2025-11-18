# Implementation Plan: GCP Infrastructure as Code with Terraform

**Branch**: `001-gcp-terraform-iac` | **Date**: 2025-11-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-gcp-terraform-iac/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create minimal Terraform infrastructure to provision GCP resources for the workout data application using free tier services. The implementation will create a GCP project, enable required APIs, provision BigQuery dataset and table, and create a service account with minimal permissions for application authentication. Focus is on simplicity and using GCP free tier to minimize costs.

## Technical Context

**Language/Version**: HCL (Terraform) 1.5+ (latest stable version)  
**Primary Dependencies**: Terraform, Google Cloud Provider plugin (hashicorp/google ~> 5.0)  
**Storage**: BigQuery (free tier: 10 GB storage, 1 TB queries/month) in europe-north1 (Sweden)  
**Testing**: terraform validate, terraform plan dry-run  
**Target Platform**: Google Cloud Platform (GCP)  
**Project Type**: Infrastructure as Code (IaC) - single infrastructure module  
**Performance Goals**: Infrastructure provisioning complete within 5 minutes  
**Constraints**: Use GCP free tier services only; minimal IAM setup; local state file (no remote backend); single-user hobby project  
**Scale/Scope**: Single GCP project, 1 BigQuery dataset, 1 table, 1 service account  
**Key Unknowns**: 
- NEEDS CLARIFICATION: Specific GCP free tier limits and restrictions for BigQuery in europe-north1
- NEEDS CLARIFICATION: Minimum required IAM roles for service account to work with BigQuery
- NEEDS CLARIFICATION: Whether to use project creation in Terraform or assume pre-existing project
- NEEDS CLARIFICATION: Best practices for managing service account keys in Terraform for hobby projects

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Before Phase 0)
**Note**: The constitution.md file is a template and not yet populated with project-specific principles. For this infrastructure feature:

**Infrastructure-Specific Considerations**:
- ✅ **Simplicity**: Using minimal Terraform setup with no complex modules or abstractions
- ✅ **Single Purpose**: Infrastructure code creates GCP resources for BigQuery only
- ✅ **Testability**: Terraform plan/validate provides dry-run testing capability
- ✅ **Documentation**: Will include quickstart guide for deployment
- ✅ **Cost Awareness**: Using free tier services only

**No Constitutional Violations**: This is infrastructure code, not application logic. Standard IaC practices apply.

### Post-Design Re-evaluation (After Phase 1)

**Design Review Against Infrastructure Best Practices**:

✅ **Simplicity Maintained**:
- Flat Terraform structure (no nested modules)
- Single terraform/ directory with 4-5 core files
- No unnecessary abstractions or complex variable hierarchies

✅ **Clear Purpose & Scope**:
- Infrastructure limited to exactly what's needed: BigQuery dataset, table, service account
- No over-engineering with multi-environment setups
- No premature optimization (e.g., remote state backend)

✅ **Testability & Validation**:
- `terraform validate` checks syntax
- `terraform plan` provides dry-run preview
- Manual verification steps documented in quickstart
- Can be destroyed and recreated easily for testing

✅ **Documentation Quality**:
- ✅ research.md: All technical decisions documented with rationale
- ✅ data-model.md: Complete schema and entity relationships
- ✅ contracts/inputs.md: All variables with validation rules
- ✅ contracts/outputs.md: All outputs with usage examples
- ✅ quickstart.md: Step-by-step deployment guide with troubleshooting

✅ **Security & Cost**:
- Minimal IAM roles (dataEditor + jobUser only)
- Service account keys properly gitignored
- Free tier constraints documented
- Billing alerts recommended in quickstart

✅ **Maintainability**:
- Local state for hobby project (simple, no backend complexity)
- Clear separation of concerns (variables, outputs, main resources)
- User manual steps explicitly documented (project creation)

**Final Assessment**: ✅ **PASS** - No constitutional violations. Infrastructure design aligns with simplicity, testability, and documentation principles. Appropriate for hobby project scope.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
terraform/
├── main.tf              # Main Terraform configuration
├── variables.tf         # Input variable definitions
├── outputs.tf           # Output value definitions
├── versions.tf          # Provider version constraints
├── terraform.tfvars.example  # Example variable values
└── README.md            # Terraform-specific documentation

.gitignore               # Updated to exclude Terraform state and keys
```

**Structure Decision**: Infrastructure as Code stored in dedicated `terraform/` directory at repository root. This keeps infrastructure separate from application code. Using flat structure (no nested modules) for simplicity in a hobby project.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**N/A** - No constitutional violations or complexity concerns. This infrastructure implementation follows simplicity principles and is appropriate for the hobby project scope.

---

## Phase Completion Summary

### ✅ Phase 0: Research (Completed)
- **Output**: [research.md](./research.md)
- **Resolved**:
  - GCP free tier limits for BigQuery in europe-north1
  - Minimum IAM roles required for service account
  - Project creation approach (manual vs Terraform)
  - Service account key management strategy
- **Key Decisions**: Use europe-north1, minimal IAM roles, pre-existing project, local key storage

### ✅ Phase 1: Design & Contracts (Completed)
- **Outputs**:
  - [data-model.md](./data-model.md) - BigQuery schema and GCP resource entities
  - [contracts/inputs.md](./contracts/inputs.md) - Terraform input variables
  - [contracts/outputs.md](./contracts/outputs.md) - Terraform output values
  - [quickstart.md](./quickstart.md) - Deployment guide
- **Agent Context**: Updated with Terraform, GCP, BigQuery technologies

### ✅ Phase 2: Constitution Re-evaluation (Completed)
- **Status**: ✅ PASS - No violations
- **Assessment**: Design aligns with simplicity, testability, and documentation principles

---

## Next Steps (Not Part of /speckit.plan)

The planning phase is complete. The next phase is **implementation** using `/speckit.tasks`:

1. Create actual Terraform configuration files (`main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`)
2. Implement BigQuery table schema in Terraform
3. Configure service account and IAM roles
4. Create service account key generation logic
5. Test deployment with `terraform plan` and `terraform apply`
6. Verify infrastructure in GCP Console
7. Update application configuration files
8. Document any deployment issues or improvements

**Command to proceed**: `/speckit.tasks` (creates tasks.md with implementation checklist)
