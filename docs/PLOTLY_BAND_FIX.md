# Plotly Band Annotation Fix

## Issue
TypeError when generating Plotly charts with shaded bands: `unsupported operand type(s) for +: 'int' and 'str'`

## Root Cause
The `add_vrect()` method's `annotation_text` parameter was causing type conflicts when the x-axis contained string values (like dates). Plotly internally tries to calculate the middle position for the annotation, which fails when mixing string and numeric types.

## Solution
Removed the `annotation_text` parameter from `add_vrect()` and added annotations separately using `add_annotation()`. This approach:

1. Adds the shaded rectangle without any text
2. Calculates the middle position manually based on x-axis data type
3. Adds the label as a separate annotation at the calculated position

## Changes Made
- Modified `plotly_chart_generator.py` lines 163-180
- Separated band rectangle creation from label annotation
- Added logic to handle both string and numeric x-axis values
- Labels now appear at the top center of each band

## Testing
Run the app and test with:
1. Upload CSV and PNG files
2. Request chart generation with `inline_middle` legend type
3. Add a band annotation: "add a light gray colored vertical annotation band between 2019-December and 2020-Feb with text 'Covid'"
4. Verify the band appears with the label at the top

## Status
✅ Fixed - Ready for testing
