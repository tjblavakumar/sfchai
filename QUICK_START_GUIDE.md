# SF CHAI - Quick Start Guide

## What Was Fixed

✅ **Chart generation now accurately replicates reference charts** including:
- Legends (inline labels or legend boxes)
- Horizontal annotation lines (targets, thresholds)
- Vertical annotation lines (events, dates)
- Shaded bands (time periods)
- Exact colors from reference
- Font sizes and styles

✅ **Chatbot is now much larger** (80% width, 85% height) for comfortable interaction

✅ **Chatbot modifications work properly** - All chart customizations now apply correctly

✅ **README merge conflict resolved**

---

## How to Run

1. **Install dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your API keys** in `.env`:
   - AWS Bedrock credentials (recommended)
   - OR OpenAI API key (fallback)

3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

4. **Open in browser**: http://localhost:8501

---

## How to Use

### Step 1: Upload Files
1. **CSV Data**: Upload your data file (left column)
2. **Reference Chart**: Upload a PNG/JPG image of the chart you want to replicate (right column)

### Step 2: Generate Chart
1. Click the **"Generate Chart"** button
2. Wait for vision analysis to complete
3. Expand **"Vision Analysis Results"** to see what was detected:
   - Chart type
   - Legend type (inline or box)
   - Annotations (horizontal lines, vertical lines, bands)
   - Colors and fonts

### Step 3: Review Generated Chart
1. The chart should appear below
2. Check if it matches your reference:
   - ✅ Colors match
   - ✅ Legend placement matches
   - ✅ Annotations are present
3. If annotations are missing, you'll see a warning message

### Step 4: Customize with Chatbot (Optional)
1. Click the **🤖 floating button** (bottom-right corner)
2. Large dialog opens (80% of screen)
3. Try commands like:
   - "Change the first series color to blue"
   - "Add a red horizontal line at value 5000 labeled 'Target'"
   - "Move legend to bottom"
   - "Make lines thicker"
4. Close dialog to see changes

### Step 5: Save Your Work
1. Enter a session name in the sidebar
2. Click **"💾 Save Session"**
3. Load it later from the dropdown

---

## Troubleshooting

### Problem: Annotations Not Applied

**Check**:
1. Expand "Vision Analysis Results"
2. Look for: "📍 Annotations detected: X horizontal lines..."
3. If detected but not applied, you'll see: "⚠️ Reference has horizontal annotations but they were NOT applied"

**Solutions**:
1. Try regenerating the chart (click Generate again)
2. Use chatbot to add manually: "Add a red horizontal line at value 2.0 labeled 'Target'"
3. Check if the reference image is clear and high-quality

### Problem: Legend Not Matching

**Check**:
1. Vision analysis should show: "📊 Legend type: inline" or "box"
2. If wrong type detected, the AI misread the reference

**Solutions**:
1. Use a clearer reference image
2. Use chatbot: "Move legend to bottom" or "Add inline labels to series"

### Problem: Colors Don't Match

**Check**:
1. Vision analysis shows detected colors in the "colors" array
2. AI may approximate colors if they're not clear

**Solutions**:
1. Use chatbot: "Change first series color to #1f77b4"
2. Be specific with hex color codes

### Problem: Chatbot Modifications Not Showing

**Solution**:
1. After chatbot makes changes, **close the dialog**
2. Changes appear on the main page
3. If still not showing, try refreshing the page (F5)

---

## Example Commands for Chatbot

### Colors
- "Change the first series color to blue"
- "Use red for the second line"
- "Change background color to white"

### Annotations
- "Add a red horizontal line at value 5000 labeled 'Target'"
- "Add a band from March 2020 to October 2020 labeled 'COVID'"
- "Mark the average value with a dashed line"

### Layout
- "Move legend to bottom"
- "Hide the legend"
- "Increase font size to 14px"
- "Make lines thicker"

### Chart Type
- "Change to bar chart"
- "Convert to stacked area chart"

---

## Tips for Best Results

1. **Use High-Quality Reference Images**
   - Clear, high-resolution PNG or JPG
   - No compression artifacts
   - Good contrast

2. **Check Vision Analysis First**
   - Always expand the analysis results
   - Verify what was detected
   - If something is missing, it won't be in the chart

3. **Be Specific with Chatbot**
   - Say "first series" or "second series" instead of just "the line"
   - Use exact values: "at value 5000" not "around 5000"
   - Use hex colors: "#ff0000" instead of "red"

4. **Save Frequently**
   - Sessions are saved to SQLite
   - You can load them later
   - Includes CSV data, chart config, and chat history

5. **Use Debug Output**
   - Expand "Debug: Chart JSON" to see the raw ECharts config
   - Useful for understanding what's in the chart
   - Can copy/paste for manual editing if needed

---

## Known Limitations

1. **AI Accuracy**: Vision analysis depends on image quality and AI model capabilities
2. **Complex Charts**: Very complex charts may not be fully replicated
3. **Font Families**: Exact font families may not be detected (only sizes)
4. **Color Precision**: Colors may be approximated

---

## Need Help?

1. Check the vision analysis results first
2. Try using the chatbot to fix issues
3. Review the debug output (Chart JSON)
4. Try with a clearer reference image
5. Check that your API keys are configured correctly

---

## Files in This Project

- `app.py` - Main Streamlit application
- `ai_client.py` - AI integration (Bedrock/OpenAI)
- `database.py` - Session persistence
- `samples.py` - Sample data
- `FIXES_APPLIED.md` - Detailed list of fixes
- `test_fixes.py` - Test script to verify fixes
- `QUICK_START_GUIDE.md` - This file

---

## Next Steps

1. Run `python test_fixes.py` to verify everything is working
2. Run `streamlit run app.py` to start the application
3. Try with your own data and reference charts
4. Experiment with the chatbot customization features

Enjoy using SF CHAI! 🎉
