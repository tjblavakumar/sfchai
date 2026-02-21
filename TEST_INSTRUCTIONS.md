# Test Instructions - Verify Chart Accuracy Fix

## Quick Test (5 minutes)

1. **Start the app**:
   ```bash
   streamlit run app.py
   ```

2. **Upload files**:
   - CSV: Click "Choose a CSV file" → Select `mydata/01a-YoY-PCE.csv`
   - PNG: Click "Choose a reference PNG image" → Select `mydata/01a-YoY-PCE.png`

3. **Generate chart**:
   - Click the blue "Generate Chart" button
   - Wait for analysis to complete

4. **Check results**:
   - ✅ Chart appears below
   - ✅ No validation warnings (or minimal warnings)
   - ✅ Chart has 2 lines (blue and orange/green)
   - ✅ Horizontal dashed line at 2% visible
   - ✅ Colors match reference image

## What to Look For

### ✅ Success Indicators

1. **Vision Analysis Results** (expand the section):
   - Chart type: "line"
   - Legend type: "inline" or "box"
   - Annotations: "1 horizontal lines" detected
   - Colors: Shows 2 hex color codes
   - Series: Shows 2 series names

2. **Generated Chart**:
   - Two lines visible (headline and core)
   - Horizontal dashed line at 2%
   - Colors match reference
   - Lines are smooth/curved
   - Labels at end of lines (if inline) or legend box

3. **No Validation Warnings**:
   - No red/orange warning messages
   - Or only minor warnings you can fix with chatbot

### ❌ Failure Indicators

1. **Validation Warnings**:
   - "Expected 2 series but got 1" → Missing series
   - "Reference has 1 horizontal annotation(s) but markLine not added" → Missing 2% line
   - "Series 0 color mismatch" → Wrong colors

2. **Visual Issues**:
   - Only 1 line instead of 2
   - No horizontal line at 2%
   - Colors don't match reference
   - Legend placement wrong

3. **Error Messages**:
   - "Response was not valid JSON" → AI parsing issue
   - "Vision analysis failed" → Image analysis issue

## If You See Warnings

### Example Warning: "Reference has 1 horizontal annotation(s) but markLine not added"

**What it means**: The AI detected a horizontal line in the reference but didn't add it to the chart.

**How to fix**:
1. Open chatbot (🤖 button bottom-right)
2. Type: "Add a horizontal dashed line at value 2.0 labeled 'Target' in black"
3. Close chatbot
4. Check if line appears

### Example Warning: "Expected 2 series but got 1"

**What it means**: Chart only has 1 line instead of 2.

**How to fix**:
1. Open chatbot
2. Type: "Add the YoY_pce_core series in orange color"
3. Close chatbot
4. Check if second line appears

### Example Warning: "Series 0 color mismatch: expected #5470c6, got #1f77b4"

**What it means**: First series has wrong color.

**How to fix**:
1. Open chatbot
2. Type: "Change first series color to #5470c6"
3. Close chatbot
4. Check if color changed

## Detailed Comparison Checklist

Compare generated chart with reference image:

- [ ] Number of lines matches (should be 2)
- [ ] Line colors match reference
- [ ] Horizontal line at 2% present
- [ ] Line smoothness matches (curved vs angular)
- [ ] Legend placement matches (inline labels vs box)
- [ ] X-axis shows dates from 2019 to 2025
- [ ] Y-axis shows values from 0 to ~7
- [ ] Grid lines present/absent matches reference
- [ ] Font sizes similar to reference

## Debug Information

If chart doesn't match, check these:

### 1. Vision Analysis (expand section)
```json
{
  "chart_type": "line",  // Should be "line"
  "legend": {"type": "inline"},  // Should match reference
  "series": [
    {"name": "Headline", "color": "#5470c6"},  // Should have 2 series
    {"name": "Core", "color": "#91cc75"}
  ],
  "annotations": {
    "horizontal_lines": [  // Should have 1 entry
      {"value": 2.0, "label": "Target", "style": "dashed"}
    ]
  }
}
```

### 2. Chart JSON (expand "Debug: Chart JSON")
```json
{
  "series": [  // Should have 2 entries
    {
      "name": "YoY_pce_headline",
      "data": [1.43, 1.40, ...],  // Should have 83 values
      "itemStyle": {"color": "#5470c6"},  // Should match reference
      "markLine": {  // Should exist if reference has horizontal line
        "data": [{"yAxis": 2.0}]
      }
    },
    {
      "name": "YoY_pce_core",
      "data": [1.84, 1.74, ...],  // Should have 83 values
      "itemStyle": {"color": "#91cc75"}
    }
  ]
}
```

## Common Issues and Solutions

### Issue: "Response was not valid JSON"

**Solution**:
1. Check debug output to see what AI returned
2. Try clicking "Generate Chart" again
3. If persists, use fallback analysis and customize with chatbot

### Issue: Chart has wrong colors

**Solution**:
1. Check vision analysis - are colors detected correctly?
2. If yes, use chatbot: "Change first series to #5470c6 and second to #91cc75"
3. If no, vision analysis failed - try clearer reference image

### Issue: Missing horizontal line

**Solution**:
1. Check vision analysis - is annotation detected?
2. If yes, use chatbot: "Add horizontal line at 2.0 labeled 'Target'"
3. If no, vision analysis failed - try clearer reference image

### Issue: Only 1 series instead of 2

**Solution**:
1. Check CSV data preview - does it show both columns?
2. Use chatbot: "Add YoY_pce_core series in orange"
3. Check chart JSON to see if series was added

## Success Criteria

Test is successful when:
- ✅ Chart generates without errors
- ✅ No validation warnings (or only minor ones)
- ✅ Visual comparison shows chart matches reference
- ✅ All elements present (2 series, horizontal line, correct colors)

## Report Results

After testing, note:
1. Did chart generate successfully? (Yes/No)
2. Any validation warnings? (List them)
3. Visual comparison result? (Matches/Doesn't match)
4. Specific issues? (Missing series, wrong colors, etc.)

If chart still doesn't match reference, share:
- Validation warnings
- Vision analysis JSON
- Chart JSON (from debug section)
- Screenshot of generated chart vs reference

This will help identify remaining issues!
