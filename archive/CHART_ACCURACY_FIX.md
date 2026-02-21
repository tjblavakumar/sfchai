# Chart Accuracy Fix - Making Generated Charts Match Reference

## The Problem

Generated charts were NOT matching the reference chart at all:
- Wrong colors
- Missing horizontal annotation lines (e.g., 2% target line)
- Wrong legend placement
- Missing series
- Wrong styling

This is **UNACCEPTABLE** - the whole point of the app is to replicate the reference chart!

## Root Cause Analysis

The AI was:
1. Not following the reference analysis strictly enough
2. Skipping critical elements like annotations
3. Using default colors instead of reference colors
4. Not validating its output

## Fixes Applied

### 1. Completely Rewrote Chart Generation Prompt

**Before**: Vague instructions like "match the reference"

**After**: EXPLICIT, MANDATORY requirements with validation checklist:

```
## CRITICAL REQUIREMENTS - READ CAREFULLY:

### 1. DATA MAPPING
- YOU MUST include ALL series from the CSV data
- Each series MUST have ALL data points
- Series names MUST match CSV column names EXACTLY

### 2. COLORS - EXACT MATCH REQUIRED
- Use EXACT colors from reference analysis "colors" array
- First series gets colors[0], second series gets colors[1]
- Apply colors via: series[i].itemStyle.color

### 3. LEGEND - EXACT MATCH REQUIRED
- If analysis shows legend.type = "inline":
  * ADD endLabel to EVERY series
  * DO NOT add legend component
- If analysis shows legend.type = "box":
  * ADD legend component
  * DO NOT add endLabel

### 4. ANNOTATIONS - MANDATORY IF IN REFERENCE
- If analysis has annotations.horizontal_lines:
  * YOU MUST add markLine to series[0]
  * Use EXACT value, label, color, style

### 5. LINE SMOOTHNESS
- If analysis shows smooth = true:
  * Set smooth: true AND smoothMonotone: "x"

### 6. FONT SIZES
- Use font_sizes from analysis

## VALIDATION CHECKLIST - VERIFY BEFORE RESPONDING:
☐ Number of series matches CSV columns
☐ Colors match reference analysis
☐ Legend type matches
☐ Annotations added if in reference
☐ All data points included
```

### 2. Added Post-Generation Validation

New `validate_chart_json()` function checks:
- ✅ Correct number of series
- ✅ Annotations present if in reference
- ✅ Legend type matches (inline vs box)
- ✅ Colors match reference

If validation fails, shows warnings to user with specific issues.

### 3. Better Template in Prompt

Provided complete working example showing:
- Both series with all properties
- markLine for horizontal annotation
- endLabel for inline labels
- Exact color application
- Smooth line configuration

### 4. Explicit Output Format

```
## OUTPUT FORMAT:
Return ONLY the JSON object. No markdown, no explanations, no code blocks.
Start with { and end with }.
```

## What This Means for Your PCE Chart

For the YoY PCE data with reference chart, the generated chart will now:

1. **Have BOTH series**:
   - YoY_pce_headline (blue line)
   - YoY_pce_core (orange/green line)

2. **Use EXACT colors from reference**:
   - Extracted from vision analysis
   - Applied to each series

3. **Include horizontal line at 2%**:
   - Dashed black line
   - Labeled "Target" or "2%"
   - Added via markLine

4. **Match legend style**:
   - If reference has inline labels → endLabel on series
   - If reference has legend box → legend component

5. **Smooth lines**:
   - If reference shows smooth curves → smooth: true
   - Matches the visual style

## Testing the Fix

1. **Upload your files**:
   - CSV: `mydata/01a-YoY-PCE.csv`
   - Reference: `mydata/01a-YoY-PCE.png`

2. **Click "Generate Chart"**

3. **Check validation warnings**:
   - If you see warnings, they tell you exactly what's wrong
   - Use chatbot to fix issues

4. **Compare with reference**:
   - Colors should match
   - Both series should be present
   - Horizontal line at 2% should be there
   - Legend placement should match

## If Chart Still Doesn't Match

### Check Vision Analysis First

Expand "Vision Analysis Results" and verify:
- ✅ Chart type detected correctly
- ✅ Legend type detected (inline or box)
- ✅ Annotations detected (should show "1 horizontal lines")
- ✅ Colors detected (should show hex codes)
- ✅ Series detected (should show both series names)

If vision analysis is wrong, the chart will be wrong!

### Use Validation Warnings

After generation, check for warnings like:
- "Expected 2 series but got 1" → Missing series
- "Reference has 1 horizontal annotation(s) but markLine not added" → Missing annotation
- "Series 0 color mismatch" → Wrong color

### Fix with Chatbot

If validation shows issues, use chatbot:

```
"Add both series: YoY_pce_headline in blue and YoY_pce_core in orange"
"Add a horizontal dashed line at value 2.0 labeled 'Target' in black"
"Change first series color to #5470c6"
"Add inline labels to both series"
```

## Example: Perfect PCE Chart

What the generated chart SHOULD have:

```json
{
  "series": [
    {
      "name": "YoY_pce_headline",
      "type": "line",
      "data": [1.43, 1.40, ...],  // ALL 83 data points
      "smooth": true,
      "smoothMonotone": "x",
      "lineStyle": {"width": 2},
      "itemStyle": {"color": "#5470c6"},  // Exact color from reference
      "endLabel": {"show": true, "formatter": "{a}", "fontSize": 12},
      "markLine": {
        "data": [{"yAxis": 2.0, "name": "2%", "lineStyle": {"type": "dashed"}}]
      }
    },
    {
      "name": "YoY_pce_core",
      "type": "line",
      "data": [1.84, 1.74, ...],  // ALL 83 data points
      "smooth": true,
      "smoothMonotone": "x",
      "lineStyle": {"width": 2},
      "itemStyle": {"color": "#91cc75"},  // Exact color from reference
      "endLabel": {"show": true, "formatter": "{a}", "fontSize": 12}
    }
  ],
  "xAxis": {
    "data": ["2019-01-01", "2019-02-01", ...]  // ALL 83 dates
  }
}
```

## Success Criteria

Generated chart matches reference when:
- ✅ Same number of series (2 for PCE data)
- ✅ Same colors (blue and orange/green)
- ✅ Horizontal line at 2% present
- ✅ Legend placement matches (inline or box)
- ✅ Lines are smooth if reference is smooth
- ✅ All data points included (83 points for PCE)
- ✅ No validation warnings

## Why This Matters

The ENTIRE PURPOSE of this app is to:
1. Look at a reference chart
2. Generate the EXACT SAME chart with new data

If the generated chart doesn't match the reference, the app is USELESS.

These fixes ensure the AI:
- Follows instructions strictly
- Includes ALL required elements
- Uses EXACT colors and styling
- Validates its own output

## Next Steps

1. **Test with your PCE data**
2. **Check validation warnings**
3. **Compare generated chart with reference**
4. **Use chatbot to fix any remaining issues**

The chart should now be MUCH closer to the reference!
