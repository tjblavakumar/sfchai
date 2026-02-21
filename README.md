# SF CHAI - Streamlit + Chart + AI

An intelligent chart generation application that uses AI vision analysis to create beautiful, customizable charts from your data.

## Features

- 🤖 **AI-Powered Analysis**: Upload a reference chart image and CSV data - AI extracts the design
- 💬 **Chatbot Interface**: Natural language interaction for chart creation and modification
- 🎨 **Full Customization**: Colors, fonts, line styles, annotations, and more
- 📊 **Professional Charts**: Support for inline labels, reference lines, and shaded bands
- 📋 **Data Tables**: Automatic comparison tables showing period-over-period changes
- 💾 **Export Options**: Download as standalone HTML or editable Python scripts
- ⚡ **Real-time Updates**: See changes instantly as you modify your chart
- 💾 **Session Management**: Save and load your work

## Quick Start

### Prerequisites
- Python 3.8+
- AWS Bedrock or OpenAI API access

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tjblavakumar/sfchai.git
cd sfchai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your AI provider:
   - Copy `.env.example` to `.env`
   - Add your AWS credentials or OpenAI API key

4. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Upload Files**: Upload your CSV data and a reference chart image
2. **Review Proposal**: AI analyzes your files and shows a chart proposal
3. **Modify**: Use natural language to request changes
4. **Generate**: Say "looks good" or "generate" to create your chart
5. **Refine**: Continue modifying until perfect
6. **Export**: Download as HTML or Python for sharing

### Example Commands
- "Change the first series color to red"
- "Make lines smooth"
- "Add horizontal line at 2.0 with label 'Target'"
- "Make axis lines thicker and black"
- "Put headline label above its line"
- "Show data table"
- "Export as HTML"

## Export Features

### HTML Export
- Standalone file that works offline
- Open in any browser
- Fully interactive (zoom, pan, hover)
- Perfect for sharing with non-technical users

### Python Export
- Complete Python script with embedded data
- Fully editable and customizable
- Includes installation instructions
- Great for developers and automation

**Usage:**
```
"Export as HTML"
"Export as Python"
```

Files are saved to the `downloads/` folder with timestamps.

## Documentation

- [Features Guide](docs/FEATURES.md) - Complete feature documentation
- [Export Guide](docs/EXPORT_FEATURE.md) - Export functionality details
- [Data Table Guide](docs/DATA_TABLE_FEATURE.md) - Data table feature
- [Quick Start Guide](QUICK_START_GUIDE.md) - Detailed getting started guide
- [Testing Guide](TESTING_GUIDE.md) - How to test the application
- [Changelog](CHANGELOG.md) - Version history and changes

## Architecture

- **Frontend**: Streamlit
- **Chart Libraries**: Plotly (primary), ECharts (fallback)
- **AI**: AWS Bedrock Claude / OpenAI GPT-4 Vision
- **Database**: SQLite for session persistence

## Key Components

- `app.py` - Main application with chatbot workflow
- `ai_client.py` - AI provider abstraction
- `plotly_chart_generator.py` - Advanced chart generation
- `table_generator.py` - Data table calculations
- `export_manager.py` - HTML and Python export
- `database.py` - Session management

## Requirements

See `requirements.txt` for full list. Key dependencies:
- streamlit
- plotly
- pandas
- boto3 (for AWS Bedrock)
- openai (for OpenAI)
- Pillow

## Configuration

Configure AI provider in the sidebar:
- **AWS Bedrock**: Requires AWS credentials with Bedrock access
- **OpenAI**: Requires OpenAI API key

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

## Version

Current version: 1.1

See [CHANGELOG.md](CHANGELOG.md) for version history.

## What's New in v1.1

- 📋 Data table feature with period comparisons
- 📦 Export to HTML (standalone, offline-capable)
- 🐍 Export to Python (editable scripts)
- 🎨 Enhanced customization options
- 🔧 Bug fixes and improvements
