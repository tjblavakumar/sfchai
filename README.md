# SF CHAI - Streamlit + eChart + AI

**S**treamlit + **F**Charts + **C**harts + **H**elper + **AI**

A production-ready local web application that generates Apache ECharts visualizations from CSV data by analyzing reference chart images using AI vision models.

## Features

- 📊 **CSV Data Upload** - Load your data from CSV files
- 🖼️ **Reference Chart Analysis** - Upload a PNG image of the chart you want to replicate
- 🤖 **AI-Powered Generation** - Uses AWS Bedrock (Claude) or OpenAI (GPT-4o) vision models
- 📈 **Interactive ECharts** - Render beautiful, interactive Apache ECharts visualizations
- 📝 **Executive Summaries** - Auto-generated business summaries from your data
- 💬 **Natural Language Chat** - Ask questions and modify charts via chat
- 💾 **Session Persistence** - Save and load work sessions with SQLite

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- **AWS Bedrock**: Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- **OpenAI** (fallback): Set `OPENAI_API_KEY`

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
SFCHAI/
├── app.py              # Main Streamlit application (Phase 1)
├── database.py         # SQLite session management
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── README.md           # This file
├── sessions/           # Saved session files (created at runtime)
└── sessions.db         # SQLite database (created at runtime)
```

## Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Complete | Skeleton + UI basics |
| Phase 2 | ✅ Complete | Data loading & Vision analysis |
| Phase 3 | ✅ Complete | Chart generation & rendering |
| Phase 4 | ✅ Complete | Executive summary generation |
| Phase 5 | ✅ Complete | Chat interface & dynamic updates |
| Phase 6 | ✅ Complete | Session save/load + exports |
| Phase 7 | ✅ Complete | Final touches & samples |

## Usage Flow

1. **Upload Files**: Upload a CSV data file and a reference PNG chart image
2. **Generate**: Click "Generate Chart" to analyze the reference and create an ECharts visualization
3. **Review**: View the interactive chart and executive summary
4. **Interact**: Ask questions or request modifications via the chat interface
5. **Save**: Your work is automatically saved to SQLite for later

## Supported Chart Types

- Line charts
- Bar charts
- Stacked bar charts
- Line + bar combination charts

## Tech Stack

- **Python 3.11+**
- **Streamlit** - Web framework
- **streamlit-echarts** - ECharts rendering
- **pandas** - Data manipulation
- **Pillow** - Image processing
- **boto3** - AWS Bedrock SDK
- **OpenAI** - GPT-4o API
- **SQLite** - Session persistence

## License

MIT
