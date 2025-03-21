# InterviewBooster

InterviewBooster is an application that generates personalized feedback reports for job candidates based on their survey responses. The application fetches data from Google Sheets, analyzes it using an LLM (Large Language Model), and generates both text and PDF reports.

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Cloud Service Account with access to Google Sheets API
- DeepSeek API key

### Setup

1. Clone the repository:

```bash
git clone https://github.com/Harsimran-19/InterviewBoosterDemo.git
cd InterviewBoosterDemo
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up Google Cloud Service Account:
   - Create a service account in the Google Cloud Console
   - Enable the Google Sheets API
   - Create and download a JSON key file
   - Rename the key file to `credentials.json` and place it in the root directory of the project

4. Create a `.env` file in the root directory with the following variables:

```
DEEPSEEK_API_KEY=your_deepseek_api_key
SHEET_IDS=sheet_id_1,sheet_id_2,...
CREDENTIALS_PATH=credentials.json
```

## Running the Application

### Local Development

To run the application locally:

```bash
python tools/ui.py
```

This will start a Streamlit server, and you can access the application at http://localhost:8501.

### Streamlit Cloud Deployment

For Streamlit Cloud deployment:

1. Add your Google Cloud Service Account credentials to Streamlit secrets:
   - Go to your Streamlit Cloud dashboard
   - Navigate to your app's settings
   - Add the following to the secrets section:

```toml
[google]
credentials = """your_json_credentials_here"""
```

2. Add your DeepSeek API key and Sheet IDs to Streamlit secrets:

```toml
DEEPSEEK_API_KEY = "your_deepseek_api_key"
SHEET_IDS = "sheet_id_1,sheet_id_2,..."
```

## How It Works

### Architecture

The application follows a modular architecture:

1. **Core Module** (`src/core/booster.py`): The main class that orchestrates the entire process.
2. **Google Sheets Integration** (`src/utils/sheets.py`): Handles fetching data from Google Sheets.
3. **LLM Integration** (`src/llm/client.py`): Communicates with the DeepSeek API to generate feedback.
4. **PDF Generation** (`src/utils/pdf.py`): Creates PDF reports from the generated feedback.
5. **UI** (`tools/ui.py`): Streamlit interface for user interaction.

### Data Flow

1. User enters a candidate's email in the UI
2. The application fetches all responses for that email from configured Google Sheets
3. The data is formatted and sent to the LLM for analysis
4. The LLM generates a personalized feedback report
5. The report is converted to both markdown and PDF formats
6. The user can view the report in the UI and download the PDF

### Configuration

The application uses a settings module (`src/config/settings.py`) that supports both local development (using `.env` file) and Streamlit Cloud deployment (using Streamlit secrets).

The `get_credentials_dict()` method in the settings module handles retrieving Google Cloud Service Account credentials from either Streamlit secrets or a local file.

### Prompt Engineering

The system prompt (`src/prompts/system_prompt.py`) defines how the LLM should analyze the survey responses and structure the feedback report. It includes:

- Question type identification and scoring rules
- Section weight distribution
- Report structure guidelines
- Style and tone instructions

## Troubleshooting

### Google Sheets Authentication Issues

If you encounter authentication issues with Google Sheets:

1. Ensure your credentials.json file is properly formatted
2. Check that your service account has access to the Google Sheets
3. Verify that the SHEET_IDS in your .env file or Streamlit secrets are correct

### DeepSeek API Issues

If you encounter issues with the DeepSeek API:

1. Verify your API key is correct
2. Check your internet connection
3. Ensure you're not exceeding API rate limits
