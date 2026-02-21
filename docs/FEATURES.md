# SF CHAI Features Documentation

## Table of Contents
1. [Chart Customization](#chart-customization)
2. [Annotations](#annotations)
3. [Styling Options](#styling-options)
4. [Natural Language Commands](#natural-language-commands)

## Chart Customization

### Series Styling

#### Line Colors
Change the color of any data series:
- "Change the first series color to red"
- "Make headline series blue"
- "Set core color to #0066cc"

#### Line Thickness
Adjust the thickness of chart lines:
- "Make chart lines thicker"
- "Set line thickness to 5"
- "Make first line thicker"

**Default:** 2px

#### Line Style
Switch between smooth curves and straight lines:
- "Make lines smooth"
- "Make first line straight"
- "Smooth all lines"

**Options:** smooth, straight

### Legend Options

#### Inline at Line Ends
Labels appear at the right end of each line:
- "Use inline legend"
- "Labels at line ends"

#### Inline in Middle (Above/Below)
Labels appear in the middle of lines, positioned above or below:
- "Put headline label above its line"
- "Put core label below its line"
- "Labels in middle of chart"

**Note:** This is the recommended option for clarity and follows professional charting standards.

#### Box Legend
Traditional legend box with positioning:
- "Use box legend on the right"
- "Legend box at top"

**Positions:** top, bottom, left, right

## Annotations

### Horizontal Reference Lines
Add horizontal lines with labels:
- "Add horizontal line at 2.0 with label 'Target'"
- "Add reference line at 3.5"

**Properties:**
- Value (y-axis position)
- Label text
- Color (default: black)
- Style (solid/dashed)
- Font size (default: 10px)

**Example:**
```
"Add horizontal line at 2.0 labeled '2% Target' in red"
```

### Vertical Reference Lines
Add vertical lines with labels:
- "Add vertical line at 2020 with label 'Event'"
- "Mark 2019 with a vertical line"

**Properties:**
- Value (x-axis position, can be date or number)
- Label text
- Color (default: gray)
- Style (solid/dashed)
- Font size (default: 10px)

### Shaded Bands
Add shaded regions to highlight time periods:
- "Add a light gray band between 2019-December and 2020-Feb with text 'Covid'"
- "Shade the region from 2018 to 2019"

**Properties:**
- Start value (x-axis)
- End value (x-axis)
- Label text
- Color (default: light gray)
- Opacity (default: 0.3)
- Font size (default: 10px)

### Annotation Font Sizes
Customize the size of annotation labels:
- "Increase horizontal annotation label font size to 16"
- "Make vertical line labels bigger"
- "Set band label font to 14"

**Default:** 10px
**Recommended:** 12-16px for better visibility

## Styling Options

### Axis Lines

#### Color
Change the color of x-axis and y-axis lines:
- "Make axis lines black"
- "Change axis color to dark gray"
- "Pure black axis lines"

**Default:** #999999 (gray)

#### Thickness
Adjust axis line thickness:
- "Make axis lines thicker"
- "Set axis line width to 2"

**Default:** 1px
**Recommended:** 2-3px for emphasis

### Axis Labels

#### Font Color
Change the color of tick labels (numbers/dates on axes):
- "Change axis label font to black"
- "Make axis labels darker"
- "Set axis label color to #333333"

**Default:** #666666 (medium gray)

#### Font Size
Adjust the size of axis labels:
- "Increase axis label font size to 12"
- "Make axis labels bigger"

**Default:** 11px

### Grid Lines

#### Color
Customize the background grid line color:
- "Change grid color to darker gray"
- "Make gridlines lighter"
- "Set grid color to #cccccc"

**Default:** #e0e0e0 (light gray)

#### Visibility
Show or hide grid lines:
- "Hide grid"
- "Remove gridlines"
- "Show grid"

**Default:** Visible

## Natural Language Commands

### Approval & Generation
- "looks good"
- "generate"
- "create chart"
- "go ahead"
- "yes"

### Modifications
The system understands natural language requests. Here are common patterns:

#### Color Changes
- "Change [element] color to [color]"
- "Make [element] [color]"
- "[color] [element]"

#### Size Changes
- "Make [element] bigger/smaller"
- "Increase/decrease [element] size"
- "Set [element] size to [number]"

#### Style Changes
- "Make lines smooth/straight"
- "Thicker/thinner [element]"
- "Show/hide [element]"

#### Adding Elements
- "Add [annotation type] at [position] with label '[text]'"
- "Add [annotation type] labeled '[text]'"

### Examples of Complex Requests
- "Make the chart lines thickness to 5, change grid color to light gray, and add a horizontal line at 2.5 labeled 'Threshold'"
- "Put headline label above its line, core label below, and make both lines smooth"
- "Change axis lines to black and thicker, hide the grid, and increase annotation font sizes to 16"

## Tips for Best Results

1. **Be specific**: "Change first series color to red" is better than "change color"
2. **Use natural language**: The AI understands conversational requests
3. **One change at a time**: While multiple changes work, single requests are clearer
4. **Reference elements clearly**: Use "axis lines" vs "chart lines" vs "grid lines"
5. **Specify positions**: "above the line" vs "at line ends" for labels
6. **Include units when relevant**: "font size 16" or "thickness 5"

## Troubleshooting

### Labels Not Appearing in Middle
Make sure to say "in the middle of chart" or "above/below the line" rather than "at line ends"

### Colors Not Changing
Specify which element: "axis label color" vs "axis line color" vs "chart line color"

### Annotations Not Visible
Check font size - increase to 14-16px for better visibility

### Grid Too Prominent
Change grid color to lighter shade: "#f5f5f5" or hide completely

## Technical Notes

- Charts use Plotly for advanced features (middle labels, bands)
- ECharts used as fallback for basic charts
- All colors support hex codes (#RRGGBB) or color names
- Font sizes in pixels (px)
- Line widths in pixels (px)
- Dates can be in various formats (YYYY-MM-DD, YYYY-MM, etc.)
