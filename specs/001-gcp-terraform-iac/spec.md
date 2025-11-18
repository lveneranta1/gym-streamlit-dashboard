# Feature Specification: GCP Infrastructure as Code with Terraform

**Feature Branch**: `001-gcp-terraform-iac`  
**Created**: 2025-11-18  
**Status**: Draft  
**Input**: User description: "create new spec for implementing infrastructure as code using terraform to deploy necessary GCP resources for this project."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Complete GCP Infrastructure (Priority: P1)

As a hobby project developer, I need to provision a complete GCP environment from scratch including project, BigQuery dataset, and table so that I can start uploading and analyzing workout data immediately.

**Why this priority**: This is the complete foundation needed to run the application. A single, simple deployment should create everything needed without manual setup steps.

**Independent Test**: Can be fully tested by running infrastructure code once and verifying that a new GCP project exists with BigQuery dataset and table ready to receive workout data from the application.

**Acceptance Scenarios**:

1. **Given** no existing GCP infrastructure, **When** infrastructure code is executed with billing account ID, **Then** a new GCP project is created with billing enabled
2. **Given** the new project exists, **When** infrastructure provisioning continues, **Then** a BigQuery dataset is created with the workout data table schema
3. **Given** the infrastructure is deployed, **When** the application attempts to write data using generated credentials, **Then** data is successfully written to the BigQuery table
4. **Given** all infrastructure exists, **When** querying the BigQuery table, **Then** the table has the correct schema for workout data storage

---

### User Story 2 - Simple Service Account Setup (Priority: P2)

As a hobby project developer, I need a service account with appropriate permissions created automatically so that my application can authenticate to BigQuery without complex configuration.

**Why this priority**: Service account setup is essential for application authentication but should be simple and automatic for a single-user project.

**Independent Test**: Can be tested by using the generated service account key file to connect the application to BigQuery and successfully write workout data.

**Acceptance Scenarios**:

1. **Given** infrastructure is deployed, **When** checking created resources, **Then** a service account exists with BigQuery permissions
2. **Given** service account credentials are generated, **When** the application uses these credentials, **Then** it can write to and read from the BigQuery table
3. **Given** service account exists, **When** infrastructure is re-applied, **Then** no errors occur and credentials remain functional

---

### Edge Cases

- What happens when infrastructure provisioning fails partway through? The system should provide clear error messages and allow re-running to complete setup.
- How does the system handle resource name conflicts? The configuration should detect conflicts and fail with a clear message.
- What happens if the billing account is invalid or lacks permissions? Clear error message should indicate the billing account issue.

## Requirements *(mandatory)*

### Functional Requirements

#### Core Infrastructure Requirements

- **FR-001**: Infrastructure code MUST create a new GCP project with configurable project ID and name
- **FR-002**: Infrastructure code MUST link the project to a billing account (provided as input variable)
- **FR-003**: Infrastructure code MUST enable required GCP APIs (BigQuery API, IAM API) in the new project
- **FR-004**: Infrastructure code MUST provision a BigQuery dataset to store workout data in the Europe (Sweden) region
- **FR-005**: Infrastructure code MUST create a BigQuery table with schema matching the application's data model (date, workout_name, exercise_name, weight_kg, weight_lb, reps, notes, duration, muscle_group_level1, muscle_group_level2, upload_timestamp, data_source)

#### Identity and Access Management Requirements

- **FR-006**: Infrastructure code MUST create a service account for the application
- **FR-007**: Service account MUST be granted BigQuery Data Editor and BigQuery Job User roles at the project level
- **FR-008**: Infrastructure code MUST generate a service account key file for application authentication
- **FR-009**: Infrastructure code MUST output the path to the generated service account key file

#### Configuration Requirements

- **FR-010**: Infrastructure code MUST accept configurable input variables: billing account ID, project ID, dataset name, table name
- **FR-011**: Infrastructure code MUST use simple, descriptive resource names without complex naming conventions
- **FR-012**: Infrastructure code MUST provide output values for project ID, dataset ID, table ID, and service account email

### Key Entities

- **GCP Project**: The Google Cloud Platform project container that will be created to host all resources. Key attributes: project ID, billing account ID, enabled APIs.

- **BigQuery Dataset**: The container for the workout data table. Key attributes: dataset name, location (Europe/Sweden).

- **BigQuery Table**: The table storing workout records. Key attributes: table name, schema with columns for workout data.

- **Service Account**: The application identity for authenticating to BigQuery. Key attributes: email address, key file, assigned roles.

### Assumptions

- User has access to a GCP billing account and knows the billing account ID
- User has permissions to create new GCP projects under their organization/account
- User is running infrastructure code from a local machine with internet access
- This is a single-user hobby project - no multi-environment or team collaboration features needed
- Service account key will be stored locally and referenced in application .env file
- Infrastructure state will be stored locally (no remote state backend required for hobby project)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Infrastructure provisioning completes successfully within 5 minutes from execution start to completion
- **SC-002**: Running infrastructure code creates a complete working environment: GCP project, BigQuery dataset, BigQuery table, and service account
- **SC-003**: Zero manual steps required after infrastructure deployment - application can immediately connect and write data to BigQuery
- **SC-004**: Infrastructure setup reduces manual provisioning time by at least 80% compared to manual GCP console operations
- **SC-005**: All infrastructure outputs needed for application configuration (project ID, service account key path) are automatically provided after deployment
