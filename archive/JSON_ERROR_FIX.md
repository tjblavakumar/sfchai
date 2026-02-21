# Fix for "Response was not valid JSON" Error

## What Was the Problem?

The AI vision model was returning descriptive text instead of properly formatted JSON, causing the vision analysis to fail.

## What I Fixed

### 1. Enhanced JSON Extraction (`ai_client.py`)

**BedrockClient.analyze_image()**:
- Added multiple fallback methods to extract JSON:
  1. Try direct JSON parsing (original)
  2. Extract from markdown code blocks: ```json { ... } ```
  3. Find JSON object in text using regex: `{ ... }`
- Now much more resilient to different response formats

**analyze_chart_image()**:
- Added same JSON extraction logic
- Creates a fallback analysis if all parsing fails
- Returns useful error with raw response for debugging

### 2. Improved Vision Prompt (`ai_client.py`)

Changed the prompt to be more explicit:
- "You MUST respond with ONLY valid JSON"
- "Start your response with { and end with }"
- "Do not wrap the JSON in code blocks or markdown"
- Removed the example code block (was confusing the AI)

### 3. Better Error Handling (`app.py`)

**run_vision_analysis()**:
- Shows warning instead of error (less scary)
- Displays raw AI response in debug expander
- Uses fallback analysis if available
- Provides helpful guidance to user

### 4. Fallback Analysis

If JSON parsing fails completely:
- Creates a basic default analysis structure
- Allows chart generation to continue
- User can customize via chatbot
- Better than complete failure

## How It Works Now

### Scenario 1: AI Returns Valid JSON
```
AI Response: {"chart_type": "line", ...}
→ Parsed successfully ✅
→ Chart generated with accurate analysis
```

### Scenario 2: AI Returns JSON in Code Block
```
AI Response: ```json\n{"chart_type": "line", ...}\n```
→ Extracted from code block ✅
→ Chart generated with accurate analysis
```

### Scenario 3: AI Returns Text with JSON
```
AI Response: "Here's the analysis: {"chart_type": "line", ...}"
→ Extracted JSON from text ✅
→ Chart generated with accurate analysis
```

### Scenario 4: AI Returns Only Text (No JSON)
```
AI Response: "This is a line chart with two series..."
→ All parsing methods fail ❌
→ Use fallback analysis ⚠️
→ Chart generated with basic styling
→ User can customize via chatbot
```

## What You'll See

### Success (Scenarios 1-3)
- ✅ Vision analysis completes
- ✅ Chart type, legend, annotations detected
- ✅ Chart generated matching reference

### Fallback (Scenario 4)
- ⚠️ Warning: "Could not parse JSON from response - using fallback analysis"
- 📊 Info: "Using fallback analysis to generate a basic chart"
- 🔍 Debug section shows raw AI response
- ✅ Basic chart generated from CSV data
- 💬 Can customize via chatbot

## Testing

Run the app and try generating a chart:

```bash
streamlit run app.py
```

### If You Get the Warning

1. **Check the debug section** - See what the AI actually returned
2. **Try again** - Sometimes AI just has a bad response
3. **Use fallback** - Customize the basic chart via chatbot
4. **Try different image** - Use clearer/simpler reference

### Chatbot Commands for Fallback Chart

```
"Change first series color to #1f77b4"
"Change second series color to #ff7f0e"
"Add a horizontal line at value 2.0 labeled 'Target'"
"Make lines smooth"
"Add inline labels"
```

## Files Modified

1. **ai_client.py**
   - Enhanced `BedrockClient.analyze_image()` with JSON extraction
   - Enhanced `analyze_chart_image()` with fallback
   - Improved `VISION_ANALYSIS_PROMPT` to be more explicit

2. **app.py**
   - Enhanced `run_vision_analysis()` with better error handling
   - Shows debug information
   - Uses fallback analysis when available

## Why This Happens

The AI vision models sometimes:
- Return explanatory text instead of JSON
- Wrap JSON in markdown code blocks
- Add commentary before/after the JSON
- Get confused by complex images

Our fixes handle all these cases gracefully.

## Next Steps

1. **Test with your reference image**
2. **If you get the warning, check the debug output**
3. **Use the fallback chart and customize via chatbot**
4. **Try with a clearer/simpler reference image if needed**

The app should now be much more resilient to AI response variations!
