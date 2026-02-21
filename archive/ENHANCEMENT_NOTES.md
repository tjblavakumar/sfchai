# Floating Chatbot Enhancement

## Overview
Moved chatbot from sidebar to a floating overlay that takes 50% of screen width for better user interaction.

## Features Implemented

### 1. Floating Chat Button
- **Location**: Bottom-right corner
- **Style**: Circular button with gradient background (purple)
- **Icon**: 🤖 robot emoji
- **Behavior**: Click to open/close chat dialog

### 2. Chat Dialog (50% Screen Width)
- Opens as modal overlay on right side
- Large dialog for comfortable interaction
- Scrollable chat history (400px height)
- Min/max toggle via close button

### 3. Enhanced AI Capabilities

#### Executive Summary Generation
- User can request: "Generate executive summary"
- AI creates 300-450 word business summary
- Based on current data and chart analysis

#### Chart Type Changes
- Change between: line, bar, pie, scatter, area, stacked bar, combo
- AI suggests best alternative if requested type doesn't fit data
- Examples:
  - "Change to bar chart"
  - "Make it a stacked area chart"
  - "Convert to pie chart"

#### Visual Customization
- **Colors**: Change series colors, backgrounds
  - "Change first line to blue"
  - "Use red for the bar series"
- **Fonts**: Adjust sizes, weights
  - "Increase font size to 14px"
  - "Make axis labels bold"
- **Line Styles**: Thickness, smoothness, patterns
  - "Make lines thicker"
  - "Use dashed lines"
- **Legend**: Position, hide/show
  - "Move legend to bottom"
  - "Hide the legend"
- **Axis Labels**: Rename, format
  - "Rename x-axis to 'Quarter'"
  - "Format y-axis as percentage"

#### Annotations

**Single Line Annotations**:
- Vertical or horizontal lines at specific values
- Customizable color (default: red)
- Examples:
  - "Add red line at 5000 labeled 'Target'"
  - "Mark peak at July 2020"
  - "Add horizontal line at average value"

**Band Annotations**:
- Shaded vertical regions for time ranges
- Light colored background
- Examples:
  - "Add band from March 2020 to Oct 2020 labeled 'COVID'"
  - "Highlight Q2 2023"
  - "Shade recession period from 2008-2009"

#### Layout Adjustments
- Grid margins and spacing
- Chart dimensions
- Tooltip positioning

## Technical Implementation

### Files Modified

1. **app.py**
   - Removed `render_chat()` from sidebar
   - Added `render_floating_chat()` with dialog-based UI
   - Added `apply_chart_modifications()` for deep merging chart changes
   - Enhanced chat response handling for all action types

2. **ai_client.py**
   - Enhanced `CHAT_SYSTEM_PROMPT` with detailed instructions for:
     - Executive summary generation
     - Chart type changes
     - Visual customization (colors, fonts, lines, legends, axes)
     - Annotations (markLine for single lines, markArea for bands)
     - Layout adjustments
   - Improved `process_chat_message()` to extract JSON from markdown blocks
   - Fixed Bedrock system prompt handling

### Key Functions

```python
# Deep merge chart modifications
apply_chart_modifications(chart_json, changes)

# Process chat with enhanced capabilities
process_chat_message(client, user_message, csv_data, chart_analysis, chart_json, summary)
```

### Response Types

1. **Text Response**: `{"action": "text", "response": "..."}`
2. **Chart Modification**: `{"action": "modify_chart", "changes": {...}}`
3. **Summary Regeneration**: `{"action": "regenerate_summary"}`

## Usage Examples

### Generate Summary
```
User: "Generate an executive summary"
AI: [Regenerates summary with latest data insights]
```

### Change Chart Type
```
User: "Change to a bar chart"
AI: [Modifies series type to 'bar']
```

### Customize Colors
```
User: "Make the first line blue and the second line red"
AI: [Updates itemStyle.color for each series]
```

### Add Line Annotation
```
User: "Add a red line at 5000 labeled 'Target'"
AI: [Adds markLine to series with yAxis: 5000]
```

### Add Band Annotation
```
User: "Add a band from March 2020 to October 2020 labeled 'COVID'"
AI: [Adds markArea to series with date range]
```

### Adjust Layout
```
User: "Move legend to the bottom"
AI: [Updates legend.bottom and legend.left properties]
```

## Chat History
- Maintained within current session only
- Not persisted across sessions
- Clear button available to reset conversation

## UI/UX Improvements
- More screen space for main chart visualization
- Comfortable 50% width for chat interaction
- Floating button always accessible
- Dialog can be closed/reopened without losing context
- Helpful capability hints in expandable section

## Future Enhancements (Optional)
- [ ] Drag-and-resize chat panel
- [ ] Multiple chat threads
- [ ] Export chat history
- [ ] Voice input support
- [ ] Chart preview in chat before applying changes
- [ ] Undo/redo for chart modifications
