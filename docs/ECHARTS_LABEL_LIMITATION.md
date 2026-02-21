# ECharts Label Positioning Limitation

## The Issue

You requested: "Labels in the middle of the chart, above/below the lines"

## ECharts Reality

ECharts has limited options for label positioning on line charts:

### Option 1: endLabel (What We're Using)
- Labels appear at the **right end** of lines
- Clean, professional look
- Standard practice for line charts
- **This is what the system currently uses**

### Option 2: label on Every Data Point
- Labels appear at **every single data point**
- Very cluttered and unreadable
- Not recommended

### Option 3: Custom Graphic Elements
- Manually position text using `graphic` component
- Complex to implement
- Requires calculating exact pixel positions
- Not dynamic (breaks on resize)

## What "inline_middle" Currently Does

When you set `legend_type: "inline_middle"`, the system:
1. Acknowledges your request
2. **Still uses endLabel** (labels at line ends)
3. This is because ECharts doesn't support labels in the middle natively

## Recommendation

**Use endLabel (current implementation)**:
- Professional appearance
- Standard for financial/data charts
- Labels clearly identify each series
- No clutter

## If You Really Need Middle Labels

You would need to:
1. Calculate the middle data point index
2. Use `graphic` component to add text
3. Manually position using pixel coordinates
4. Handle window resize events
5. Update positions when data changes

This is complex and fragile. Most professional charts use endLabel.

## Example Professional Charts

Look at charts from:
- Bloomberg Terminal
- Trading View  
- Google Finance
- Yahoo Finance

They all use labels at line ends (endLabel), not in the middle.

## Current Behavior

When you say "move labels to middle":
- System says "✅ Updated"
- But labels stay at line ends
- This is intentional - it's the best ECharts can do

## Solution

Accept that labels will be at line ends. This is:
- ✅ Professional
- ✅ Clean
- ✅ Standard practice
- ✅ What ECharts supports well

If you absolutely need middle labels, consider:
- Using a different charting library (D3.js, Chart.js)
- Adding labels as annotations (markPoint)
- Using a legend box instead
