# Testing Guide - After Cleanup

## Quick Start

1. Start the app:
```bash
streamlit run app.py
```

2. The app should open in your browser at `http://localhost:8501`

## Test 1: Basic Chart Generation

### Steps:
1. Click "Load Sample Data" or upload your files:
   - CSV: `mydata/01a-YoY-PCE.csv`
   - PNG: `mydata/01a-YoY-PCE.png`

2. Click "Generate Chart" button

### Expected Results:
✅ Chart should display with:
- 2 series (YoY_pce_headline and YoY_pce_core)
- Smooth curved lines
- Proper colors matching reference
- Horizontal line at 2% (if in reference)
- Legend (inline labels or box)

❌ Should NOT see:
- Debug messages
- Multiple st.info boxes about series counts
- Verbose error messages with full tracebacks

## Test 2: Floating Chat Button

### Steps:
1. Look for the 🤖 button in the bottom-right corner
2. Scroll up and down the page

### Expected Results:
✅ Button should:
- Stay fixed in bottom-right corner
- Remain visible when scrolling
- Have a nice gradient and shadow
- Hover effect (scale up slightly)

❌ Should NOT:
- Move with page scroll
- Disappear
- Be positioned incorrectly

## Test 3: Chat Functionality

### Steps:
1. Click the 🤖 button
2. Try these commands:
   - "Add vertical line at 2020-01-01"
   - "Change first series to red"
   - "Add horizontal line at 2.5"

### Expected Results:
✅ Chat should:
- Open in a compact panel (not full screen)
- Show last 5 messages
- Apply modifications correctly
- Show "✅ Chart updated!" message

❌ Should NOT:
- Cover the entire chart
- Show debug JSON
- Fail silently

## Test 4: Annotations

### Test Vertical Line:
Command: "Add vertical line at 2020-01-01"

Expected: Single vertical line at that date (NOT a shaded band)

### Test Horizontal Line:
Command: "Add horizontal line at 2.0"

Expected: Single horizontal line at y=2.0

### Test Shaded Band:
Command: "Add band from 2020-03 to 2020-10"

Expected: Shaded region between those dates

## Test 5: Error Handling

### Steps:
1. Try uploading an invalid CSV
2. Try uploading a non-image file as PNG

### Expected Results:
✅ Should show:
- Clear error message
- What went wrong
- How to fix it

❌ Should NOT show:
- Full Python tracebacks in main UI
- Debug expanders with raw responses
- Confusing technical details

## Common Issues & Solutions

### Issue: Chart not generating
**Check:**
- Both CSV and PNG uploaded?
- CSV has correct format (date, key, value)?
- PNG is a valid image?

### Issue: Floating button not visible
**Check:**
- Scroll to bottom of page
- Check browser console for CSS errors
- Try refreshing the page

### Issue: Chat modifications not working
**Check:**
- Chart generated successfully first?
- Command is clear and specific?
- Try simpler commands first

## Success Criteria

The cleanup is successful if:

1. ✅ No debug messages in UI
2. ✅ Chart generates correctly
3. ✅ Floating button stays fixed
4. ✅ Chat works for modifications
5. ✅ Annotations work correctly
6. ✅ Error messages are user-friendly
7. ✅ Code is cleaner and more maintainable

## Report Issues

If you find any problems:
1. Note the exact steps to reproduce
2. Check browser console for errors
3. Try with sample data first
4. Report what you expected vs what happened

The code is now much cleaner and should be more stable!
