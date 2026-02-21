# SF CHAI - Streamlit + Chart + AI

An intelligent chart generation application that uses AI vision analysis to create beautiful, customizable charts from your data.

## Features

- 🤖 **AI-Powered Analysis**: Upload a reference chart image and CSV data - AI extracts the design
- 💬 **Chatbot Interface**: Natural language interaction for chart creation and modification
- 🎨 **Full Customization**: Colors, fonts, line styles, annotations, and more
- 📊 **Professional Charts**: Support for inline labels, reference lines, and shaded bands
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

### Example Commands
- "Change the first series color to red"
- "Make lines smooth"
- "Add horizontal line at 2.0 with label 'Target'"
- "Make axis lines thicker and black"
- "Put headline label above its line"

## Documentation

- [Features Guide](docs/FEATURES.md) - Complete feature documentation
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

Current version: 1.0

See [CHANGELOG.md](CHANGELOG.md) for version history.
