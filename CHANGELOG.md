# Changelog

## Version 1.1 - Feature Release

### New Features

#### Export Functionality
- **HTML Export**: Generate standalone HTML files that work offline
  - Embedded Plotly library for offline use
  - Includes source data and README
  - Fully interactive charts
  - Perfect for sharing with non-technical users
  
- **Python Export**: Generate editable Python scripts
  - Data embedded in code (fully standalone)
  - Complete with installation instructions
  - Commented code for easy customization
  - Great for developers and automation

- **Smart File Management**:
  - Exports saved to `downloads/` folder
  - Timestamped filenames (YYYYMMDD_HHMM_type.zip)
  - Automatic cleanup (keeps last 5 exports)
  - Each export includes chart, data, and README

#### Data Table Feature
- **Automatic Detection**: AI detects data tables in reference images
- **Period Comparisons**: Shows last N periods with values and changes
- **Color-Coded Rows**: Each series uses its chart color
- **Customizable**:
  - Show/hide table
  - Adjust number of periods
  - Change font size and family
  - Reposition table
- **Metrics**: Values, percentage change, absolute change

### Improvements
- Enhanced progress indicators throughout the workflow
- Better error handling and user feedback
- Improved modification detection with LLM
- More robust axis and grid styling options

### Bug Fixes
- Fixed table row ordering (header now appears at top)
- Fixed DataFrame validation in export function
- Improved font family support for tables
- Better handling of annotation font sizes

## Version 1.0 - Initial Release

### Overview
SF CHAI (Streamlit + Chart + AI) is an intelligent chart generation application that uses AI vision analysis to create customizable charts from CSV data and reference images.

### Core Features

#### 1. Chatbot-Driven Workflow
- Natural language interaction for chart creation
- File upload through chat interface
- Real-time feedback and progress indicators
- Conversational modification of charts

#### 2. AI-Powered Analysis
- Vision analysis of reference chart images
- Automatic extraction of chart properties (colors, styles, annotations)
- Intelligent proposal generation
- LLM-based intent detection for user requests

#### 3. Chart Generation
- Dual rendering engine (Plotly for advanced features, ECharts for compatibility)
- Support for inline middle labels (labels above/below lines)
- Smooth and straight line styles
- Customizable colors, fonts, and styling

#### 4. Customization Options

**Series Styling:**
- Line colors (hex codes)
- Line thickness (width)
- Line style (smooth/straight)
- Series names

**Legend Options:**
- Inline at line ends
- Inline in middle of chart (above/below lines)
- Box legend with positioning

**Annotations:**
- Horizontal reference lines with labels
- Vertical reference lines with labels
- Shaded bands (time periods)
- Customizable font sizes for all annotations

**Axis Styling:**
- Axis line color and thickness
- Axis label font color and size
- Axis title font color and size
- Grid line color and visibility

#### 5. Progress Indicators
- File upload progress
- AI analysis progress with detailed steps
- Chart generation progress
- Modification processing feedback

### Technical Implementation

#### Architecture
- **Frontend**: Streamlit
- **Chart Libraries**: Plotly (primary), ECharts (fallback)
- **AI Integration**: AWS Bedrock and OpenAI support
- **Database**: SQLite for session management

#### Key Components
- `app.py`: Main application with chatbot workflow
- `ai_client.py`: AI provider abstraction layer
- `plotly_chart_generator.py`: Plotly chart generation with advanced features
- `chart_generator.py`: ECharts fallback generator
- `database.py`: Session persistence

#### Data Flow
1. User uploads CSV data and reference image
2. AI analyzes reference image to extract chart properties
3. System creates proposal matching CSV data to chart design
4. User reviews and modifies proposal via chat
5. System generates chart using appropriate rendering engine
6. User can further modify generated chart

### Bug Fixes and Improvements

#### Phase 1: Foundation
- Basic UI and file upload
- Session management
- AI provider configuration

#### Phase 2: Analysis & Proposal
- Vision analysis integration
- Proposal generation from analysis
- Series name mapping from CSV columns
- None value handling

#### Phase 3: Review & Modifications
- Modification detection and parsing
- LLM-based intent detection
- Proposal update workflow
- Post-generation modifications

#### Phase 4: Advanced Features
- Plotly integration for middle-of-line labels
- Annotation font size support
- Axis styling (line color, thickness)
- Axis label font colors
- Chart line thickness control
- Grid line color customization
- Progress indicators throughout workflow
- Band annotation support

### Known Limitations
- ECharts doesn't support labels in middle of lines (Plotly used instead)
- Maximum file sizes apply for uploads
- AI analysis quality depends on reference image clarity

### Usage Examples

**Basic Workflow:**
1. Upload CSV file
2. Upload reference chart image
3. Review AI-generated proposal
4. Say "looks good" or "generate" to create chart
5. Make modifications as needed

**Modification Examples:**
- "Change the first series color to red"
- "Make lines smooth"
- "Add horizontal line at 2.0 with label 'Target'"
- "Increase font size of horizontal annotation to 16"
- "Make axis lines thicker and black"
- "Change grid color to darker gray"
- "Make chart lines thickness to 5"

### Documentation
- `README.md`: Project overview and setup
- `QUICK_START_GUIDE.md`: Getting started guide
- `TESTING_GUIDE.md`: Testing instructions
- `docs/`: Detailed feature documentation

### Future Enhancements
- Additional chart types (bar, scatter, pie)
- Export to multiple formats
- Template library
- Batch chart generation
- Advanced annotation types
- Custom color palettes
