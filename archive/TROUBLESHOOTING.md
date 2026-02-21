# Troubleshooting Guide - SF CHAI

## Error: "Vision analysis failed: Response was not valid JSON"

This error occurs when the AI model returns text instead of properly formatted JSON.

### What I Fixed

1. **Enhanced JSON extraction** - Now tries multiple methods to extract JSON from the response:
   - Direct JSON parsing
   - Extract from markdown code blocks (```json ... ```)
   - Find JSON object in text using regex
   
2. **Better error messages** - Shows the actual AI response so you can see what went wrong

3. **Fallback analysis** - If JSON can't be parsed, uses a basic fallback analysis so you can still generate a chart

4. **Improved prompt** - Made the vision prompt more explicit about returning ONLY JSON

### How to Fix This Error

#### Option 1: Try Again (Simplest)
Sometimes the AI just has a bad response. Click "Generate Chart" again.

#### Option 2: Check Your Reference Image
The error often happens with:
- Low quality/blurry images
- Very complex charts
- Images with lots of text
- Screenshots with UI elements

**Try**:
- Use a cleaner, higher resolution image
- Crop the image to show only the chart (no surrounding UI)
- Use a simpler chart as reference

#### Option 3: Use Fallback Analysis
If you see: "Using fallback analysis to generate a basic chart"
- The app will create a basic chart from your CSV data
- You can then customize it using the chatbot
- This is a workaround when vision analysis fails

#### Option 4: Switch AI Provider
If using AWS Bedrock, try OpenAI (or vice versa):
1. Go to sidebar
2. Select different AI provider
3. Try generating again

#### Option 5: Check API Credentials
Make sure your `.env` file has valid credentials:
```bash
# For AWS Bedrock
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-1

# For OpenAI (fallback)
OPENAI_API_KEY=your_key_here
```

### What You'll See Now

When this error occurs, you'll see:
1. **Warning message**: "Could not parse JSON from response - using fallback analysis"
2. **Debug section**: Click to see the raw AI response
3. **Info message**: "Using fallback analysis to generate a basic chart"
4. **Chart generated**: A basic chart will be created from your CSV data

### Using the Fallback Chart

If you get a fallback chart:
1. The chart will have basic styling (default colors, no annotations)
2. Open the chatbot (🤖 button)
3. Customize it:
   - "Change first series color to #1f77b4"
   - "Add a red horizontal line at value 2.0 labeled 'Target'"
   - "Make lines smooth"
   - "Move legend to bottom"

### Example Chatbot Commands After Fallback

```
"Change the first series color to blue"
"Change the second series color to orange"
"Add a horizontal dashed line at value 2.0 labeled 'Target' in black"
"Make the lines smooth"
"Increase line width to 3"
"Add inline labels to the series"
```

### Debugging Steps

1. **Check the raw response**:
   - Expand "Debug: Raw AI Response"
   - See what the AI actually returned
   - If it's descriptive text instead of JSON, the image might be too complex

2. **Check your image**:
   - Is it clear and high resolution?
   - Is it cropped to just the chart?
   - Does it have any overlays or UI elements?

3. **Check API status**:
   - AWS Bedrock: Check if your credentials are valid
   - OpenAI: Check if your API key is valid and has credits

4. **Try with sample data**:
   - Use the "Load Sample Data" feature
   - Upload a simple reference chart
   - If this works, your original image might be the issue

### Common Causes

1. **Image Quality Issues**
   - Blurry or low resolution
   - Compressed/artifacted
   - Too small or too large

2. **Image Complexity**
   - Too many elements
   - Multiple charts in one image
   - Lots of text annotations
   - Complex color schemes

3. **API Issues**
   - Expired credentials
   - Rate limiting
   - Service outage
   - Wrong region

4. **Model Behavior**
   - AI sometimes returns explanatory text
   - Model might be confused by the image
   - Prompt interpretation varies

### Prevention Tips

1. **Use high-quality reference images**:
   - PNG format preferred
   - At least 800x600 resolution
   - Clear, uncompressed
   - Cropped to just the chart

2. **Keep charts simple**:
   - 2-3 series maximum for first try
   - Clear colors
   - Minimal annotations
   - Standard chart types (line, bar)

3. **Test incrementally**:
   - Start with a simple chart
   - Once working, try more complex ones
   - Build up complexity gradually

### Still Having Issues?

If you continue to get this error:

1. **Check the logs**:
   - Look at the Streamlit terminal output
   - Check for any error messages

2. **Verify dependencies**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Test API connection**:
   ```python
   # Test AWS Bedrock
   import boto3
   client = boto3.client('bedrock-runtime', region_name='us-east-1')
   print("AWS connection OK")
   
   # Test OpenAI
   from openai import OpenAI
   client = OpenAI(api_key="your_key")
   print("OpenAI connection OK")
   ```

4. **Use fallback and customize**:
   - Let the fallback analysis create a basic chart
   - Use chatbot to add all the features you need
   - This is often faster than debugging vision issues

### Success Indicators

You'll know it's working when:
- ✅ No error messages
- ✅ Vision analysis results show in expander
- ✅ Chart type, legend type, and annotations are detected
- ✅ Generated chart appears below
- ✅ Chart matches your reference image

### Contact/Support

If none of these solutions work:
1. Check the raw AI response in the debug section
2. Try with a different reference image
3. Use the fallback analysis and chatbot customization
4. Check AWS/OpenAI service status pages
