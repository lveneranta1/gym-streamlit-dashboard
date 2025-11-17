# 🏋️ Gym Workout Data Uploader to BigQuery

A Streamlit web application for uploading workout CSV data to Google BigQuery with automatic exercise-to-muscle group mapping and data enrichment.

## Features

- 📤 **CSV Upload**: Upload workout data in CSV format with flexible column mapping
- 💪 **Muscle Group Mapping**: Automatic mapping of exercises to muscle groups (two-level hierarchy)
- ☁️ **BigQuery Integration**: Direct upload to Google BigQuery with automatic table creation
- ⚙️ **Configurable Schema**: Modular configuration files for easy customization
- ✅ **Data Validation**: Comprehensive validation of data types and constraints
- 🔍 **Preview & Review**: Preview data and mappings before uploading

## Prerequisites

- Python 3.11 or higher
- Google Cloud Platform account with BigQuery enabled
- Service account with BigQuery permissions
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd gym-streamlit-dashboard
   ```

2. **Install uv (if not already installed):**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Install dependencies:**
   ```bash
   # Create virtual environment and install dependencies
   uv sync
   
   # Or install dev dependencies too
   uv sync --extra dev
   ```

4. **Set up Google Cloud credentials:**
   - Create a service account in Google Cloud Console
   - Download the JSON key file
   - Grant BigQuery permissions (BigQuery Data Editor, BigQuery Job User)
   - Save the key file (e.g., in `credentials/service-account-key.json`)
   - Update `GOOGLE_APPLICATION_CREDENTIALS` in `.env` with the correct path

5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual GCP credentials:
   # - GCP_PROJECT_ID: Your Google Cloud Project ID
   # - GOOGLE_APPLICATION_CREDENTIALS: Path to your service account JSON key file
   # - BQ_DATASET_ID: BigQuery dataset name (e.g., workout_data)
   # - BQ_TABLE_ID: BigQuery table name (e.g., workouts)
   ```
   
   **Note:** A `.env` file with dummy values is included for testing. Replace with your actual credentials before uploading to BigQuery.

## Configuration

The application uses three YAML configuration files in the `config/` directory:

### `csv_schema.yaml`
Defines the expected CSV structure, column aliases, and validation rules.

### `exercise_mapping.yaml`
Maps exercises to muscle groups with two-level classification:
- **Level 1**: upper, lower, core, full_body
- **Level 2**: chest, back, shoulders, triceps, biceps, quads, hamstrings, etc.

### `bigquery_config.yaml`
Configures BigQuery connection settings and table schema.

## Usage

1. **Start the application:**
   ```bash
   uv run streamlit run app.py
   ```

2. **Upload your CSV file:**
   - Navigate to the "Upload" tab
   - Drag and drop or select your CSV file
   - Required columns: datetime, workout_name, exercise_name, weight, reps

3. **Review the preview:**
   - Check parsed data
   - Review muscle group mappings
   - Note any validation errors or warnings

4. **Upload to BigQuery:**
   - Click the "Upload to BigQuery" button
   - Wait for confirmation
   - View upload statistics

## CSV Format

Your CSV file should contain at least these columns:

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| datetime | timestamp | Date and time of workout | Yes |
| workout_name | string | Name of workout session | Yes |
| exercise_name | string | Name of exercise | Yes |
| weight | float | Weight used (kg or lbs) | Yes |
| reps | integer | Number of repetitions | Yes |
| sets | integer | Number of sets | No |
| notes | string | Additional notes | No |
| duration_minutes | integer | Duration in minutes | No |

### Example CSV:

```csv
datetime,workout_name,exercise_name,weight,reps,sets,notes
2024-01-15 09:00:00,Push Day,Bench Press,100,8,3,Felt strong
2024-01-15 09:15:00,Push Day,Incline Bench Press,80,10,3,
2024-01-17 10:00:00,Pull Day,Deadlift,150,5,3,New PR!
```

## Muscle Group Mappings

The application automatically maps exercises to muscle groups:

- **Upper Body**: chest, back, shoulders, triceps, biceps, forearms
- **Lower Body**: quads, hamstrings, glutes, calves
- **Core**: abs, obliques, lower_back
- **Full Body**: compound movements

Over 50 common exercises are pre-mapped. Unmapped exercises use fuzzy matching rules or default mappings.

## Troubleshooting

### Authentication Errors
- Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Ensure service account has BigQuery permissions
- Check GCP project ID matches your configuration

### CSV Parsing Errors
- Verify required columns are present
- Check date format matches configuration
- Ensure numeric columns contain valid numbers

### Upload Failures
- Verify BigQuery dataset exists
- Check network connectivity
- Review BigQuery quotas and limits

## Development

### Project Structure

```
gym-streamlit-dashboard/
├── app.py                      # Main Streamlit application
├── pyproject.toml             # Project configuration and dependencies
├── .env.example               # Environment variable template
├── README.md                  # This file
├── config/
│   ├── csv_schema.yaml        # CSV input schema
│   ├── exercise_mapping.yaml  # Exercise-to-muscle mappings
│   └── bigquery_config.yaml   # BigQuery configuration
├── modules/
│   ├── __init__.py
│   ├── config_loader.py       # Configuration loader
│   ├── csv_parser.py          # CSV parsing and validation
│   ├── data_enrichment.py     # Muscle group mapping
│   └── bigquery_uploader.py   # BigQuery upload logic
└── tests/
    └── sample_workout_data.csv # Sample test data
```

### Running Tests

```bash
uv run pytest tests/
```

### Code Quality

```bash
# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
