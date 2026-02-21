# Export Feature Documentation

## Overview
Export your charts as standalone HTML files or Python scripts that can be shared, archived, or run anywhere.

## Export Formats

### 1. HTML Export (Recommended for Sharing)
Creates a self-contained HTML file that works offline in any browser.

**What's Included:**
- `chart.html` - Interactive chart with Plotly embedded
- `data.csv` - Source data
- `README.txt` - Instructions

**Features:**
- ✅ No installation required
- ✅ Works offline (Plotly library embedded)
- ✅ Fully interactive (zoom, pan, hover)
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Easy to share via email or network

**Use Cases:**
- Share with colleagues who don't have Python
- Archive charts for future reference
- Embed in presentations or reports
- Quick viewing without running code

### 2. Python Export (Recommended for Developers)
Creates a Python script that recreates the chart with all data embedded.

**What's Included:**
- `chart.py` - Complete Python script
- `data.csv` - Source data (for reference)
- `README.txt` - Installation and usage instructions

**Features:**
- ✅ Fully editable and customizable
- ✅ Data embedded in code (standalone)
- ✅ Comments explaining each section
- ✅ Installation instructions included
- ✅ Can be integrated into other projects

**Requirements:**
```bash
pip install plotly pandas
```

**Use Cases:**
- Customize chart styling or data
- Learn how the chart was built
- Integrate into existing Python projects
- Automate chart generation
- Educational purposes

## How to Use

### Export Commands
Simply say any of these in the chat:

**HTML Export:**
- "Export as HTML"
- "Download as HTML"
- "Generate HTML file"
- "Save as HTML"

**Python Export:**
- "Export as Python"
- "Download as Python code"
- "Generate Python script"
- "Save as Python"

### File Location
All exports are saved to the `downloads/` folder with timestamped names:
- Format: `YYYYMMDD_HHMM_<type>.zip`
- Example: `20240220_1730_html.zip`

### File Management
- System keeps last 5 exports automatically
- Older exports are deleted to save space
- Each export is a complete package (chart + data + README)

## Export Package Contents

### HTML Package
```
20240220_1730_html.zip
├── chart.html          # Interactive chart
├── data.csv            # Source data
└── README.txt          # Instructions
```

### Python Package
```
20240220_1730_py.zip
├── chart.py            # Python script
├── data.csv            # Source data
└── README.txt          # Instructions
```

## Using Exported Files

### HTML Files
1. Extract the zip file
2. Double-click `chart.html`
3. Chart opens in your default browser
4. Fully interactive - no internet needed

### Python Files
1. Extract the zip file
2. Install requirements: `pip install plotly pandas`
3. Run: `python chart.py`
4. Chart opens in your browser
5. Edit the script to customize

## Python Script Structure

The generated Python script includes:

```python
# 1. Header with metadata and requirements
# 2. Data embedded as dictionary
# 3. Chart configuration
# 4. Series creation
# 5. Annotations (lines, bands)
# 6. Series labels
# 7. Layout configuration
# 8. Display command
```

All sections are commented and can be modified.

## Customization Examples

### Modify Python Script

**Change Colors:**
```python
# Find the series configuration
series_config = [
    {'color': '#FF0000', ...},  # Change to red
    ...
]
```

**Add More Data:**
```python
# Modify the data dictionary
data = {
    'date': [...],  # Add more dates
    'values': [...],  # Add more values
}
```

**Adjust Layout:**
```python
fig.update_layout(
    height=800,  # Make taller
    title="My Custom Title",  # Add title
)
```

## Technical Details

### HTML Export
- Uses `plotly.write_html()` with `include_plotlyjs='inline'`
- Plotly library (~3MB) embedded for offline use
- All chart data and configuration included
- No external dependencies

### Python Export
- Data converted to dictionary format
- All configuration preserved
- Comments added for clarity
- Includes version information
- Tested with Plotly 5.18.0+ and Pandas 2.0.0+

### File Naming
- Timestamp format: `YYYYMMDD_HHMM`
- Type suffix: `_html` or `_py`
- Extension: `.zip`
- Example: `20240220_1730_html.zip`

### Cleanup Policy
- Keeps last 5 exports
- Deletes older files automatically
- Based on file modification time
- Runs before each new export

## Troubleshooting

### "No chart found" Error
- Generate a chart first before exporting
- Make sure chart is displayed in the chat

### Python Script Won't Run
- Check Python version (3.8+ required)
- Install requirements: `pip install plotly pandas`
- Check for syntax errors if you modified the script

### HTML File Won't Open
- Try different browser (Chrome, Firefox, Edge)
- Check if file was fully extracted from zip
- Ensure file extension is `.html`

### Export Not Found
- Check `downloads/` folder in project directory
- Verify export completed successfully
- Check disk space

## Best Practices

1. **Export After Finalizing**: Make all modifications before exporting
2. **Use HTML for Sharing**: Easiest for non-technical users
3. **Use Python for Customization**: Best for developers
4. **Keep Exports Organized**: Rename files with descriptive names
5. **Test Exports**: Open/run exported files to verify they work

## Future Enhancements

Planned features:
- R script export
- PDF export
- PNG/SVG image export
- Custom export templates
- Batch export multiple charts
- Export to cloud storage

## Examples

### Example 1: Share with Team
```
User: "Export as HTML"
System: Creates 20240220_1730_html.zip
Action: Email zip file to team
Result: Team opens chart.html in browser
```

### Example 2: Customize Chart
```
User: "Export as Python"
System: Creates 20240220_1730_py.zip
Action: Extract and edit chart.py
Result: Modified chart with custom styling
```

### Example 3: Archive Charts
```
User: "Export as HTML"
System: Creates timestamped zip
Action: Move to archive folder
Result: Chart preserved for future reference
```

## Support

For issues or questions:
1. Check README.txt in the export package
2. Verify requirements are installed
3. Check SF CHAI documentation
4. Report issues on GitHub
