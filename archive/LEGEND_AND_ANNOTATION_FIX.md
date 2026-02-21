# Legend and Annotation Fixes

## Issues Fixed

### Issue 1: Legend in Wrong Place / Only One Legend Visible

**Problem**: The chart was not properly showing both series labels. Either:
- Legend box was in wrong position
- Only one inline label visible
- Labels overlapping or cut off

**Root Cause**: The AI wasn't implementing endLabel correctly for inline labels.

**Fix Applied** (`ai_client.py`):
- Made legend instructions MORE EXPLICIT in chart generation prompt
- Added EXACT properties required for endLabel:
  ```json
  "endLabel": {
    "show": true,
    "formatter": "{a}",  // Shows series name
    "fontSize": 12,
    "distance": 5
  }
  ```
- Clarified when to use inline labels vs legend box
- Added grid.right spacing requirements

**Expected Result**: Both series should now have visible labels at the end of lines (if inline) or in legend box (if box type).

---

### Issue 2: Vertical Annotation Creating Band Instead of Line

**Problem**: When asking "add vertical line at 2020", the chatbot created a gray shaded band from 2019 to 2020 instead of a single vertical line.

**Root Cause**: The AI was confusing markLine (single line) with markArea (shaded band).

**Fix Applied** (`ai_client.py`):
- Added CRITICAL section distinguishing markLine vs markArea
- Explicit examples for each type:
  - **markLine** = single vertical or horizontal line
  - **markArea** = shaded band/region for ranges
- Added rules:
  - "Add vertical line at X" → use markLine with xAxis
  - "Add band FROM X TO Y" → use markArea
  - Only use markArea when user says "FROM...TO" or "between"

**Example for Single Vertical Line**:
```json
{
  "action": "modify_chart",
  "changes": {
    "series": [{
      "markLine": {
        "data": [{
          "xAxis": "2020-01-01",
          "name": "2020",
          "lineStyle": {"color": "#000000", "type": "solid", "width": 2}
        }]
      }
    }]
  }
}
```

**Example for Shaded Band**:
```json
{
  "action": "modify_chart",
  "changes": {
    "series": [{
      "markArea": {
        "data": [[
          {"xAxis": "2020-03-01"},
          {"xAxis": "2020-10-01"}
        ]],
        "itemStyle": {"color": "rgba(200, 200, 200, 0.3)"}
      }
    }]
  }
}
```

**Expected Result**: 
- "Add vertical line at 2020" → Single vertical line
- "Add band from 2019 to 2020" → Shaded region

---

## How to Test

### Test 1: Legend/Labels
1. Generate a chart with your PCE data
2. Check if BOTH series have visible labels:
   - Either at the end of lines (inline)
   - Or in a legend box
3. Labels should not overlap or be cut off

### Test 2: Vertical Line Annotation
1. Open chatbot (🤖 button)
2. Type: "Add a vertical line at 2020-01-01"
3. Close chatbot
4. Should see: Single vertical line at 2020
5. Should NOT see: Gray shaded band

### Test 3: Shaded Band Annotation
1. Open chatbot
2. Type: "Add a shaded band from 2020-03-01 to 2020-10-01 labeled 'COVID'"
3. Close chatbot
4. Should see: Light gray shaded region
5. Should NOT see: Single line

---

## Chatbot Commands

### For Single Vertical Line:
```
"Add a vertical line at 2020-01-01"
"Mark year 2020 with a vertical line"
"Add vertical annotation at 2020-01-01"
```

### For Single Horizontal Line:
```
"Add a horizontal line at value 2.0 labeled 'Target'"
"Add red horizontal line at 5000"
"Mark target at 2.0"
```

### For Shaded Band:
```
"Add a band from 2020-03-01 to 2020-10-01 labeled 'COVID'"
"Highlight the period from 2019 to 2020"
"Shade the region between March 2020 and October 2020"
```

### For Legend/Labels:
```
"Add inline labels to both series"
"Move legend to bottom"
"Show series names at the end of lines"
```

---

## Files Modified

- `ai_client.py`:
  - Enhanced legend instructions in `CHART_GENERATION_PROMPT`
  - Added CRITICAL section for vertical line vs band in `CHAT_SYSTEM_PROMPT`
  - Added explicit examples for markLine vs markArea
  - Added important notes about the distinction

---

## Common Mistakes to Avoid

### ❌ Wrong: "Add vertical line at 2020"
If this creates a band, the AI is using markArea instead of markLine.

### ✅ Right: Should create markLine with xAxis value

### ❌ Wrong: Only one series label visible
The AI didn't add endLabel to all series.

### ✅ Right: Both series should have endLabel with show:true

---

## If Issues Persist

### Legend Still Wrong:
1. Check vision analysis - what legend type was detected?
2. Manually fix with chatbot:
   - "Add inline labels to all series"
   - "Add legend box at top right"

### Vertical Line Still Creates Band:
1. Be more explicit: "Add a SINGLE vertical LINE at 2020-01-01"
2. Or manually fix: "Remove the shaded band and add a vertical line instead"

### Date Format Issues:
- Make sure dates match your CSV format
- If CSV has "2020-01-01", use that exact format
- If CSV has "2020-01", use that format

---

## Success Criteria

✅ Both series have visible labels (inline or in legend box)
✅ "Add vertical line at X" creates a single line, not a band
✅ "Add band from X to Y" creates a shaded region
✅ Labels don't overlap or get cut off
✅ Annotations are in the correct position

Test these and let me know if there are still issues!
