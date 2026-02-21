# Code Cleanup Plan

## Current Issues

1. Chart generation is unstable - missing elements
2. Chatbot button not floating properly
3. Too much debug code cluttering the files
4. Prompts are too complex and confusing the AI
5. Code has become fragile from too many patches

## Cleanup Strategy

### Phase 1: Remove Debug Code
- Remove all `st.write("DEBUG: ...")` statements
- Remove all `st.info()` about series counts
- Clean up error handling to be production-ready

### Phase 2: Simplify AI Prompts
- Make vision analysis prompt shorter and clearer
- Make chart generation prompt focused on essentials
- Remove overly complex instructions that confuse the AI

### Phase 3: Fix Floating Button
- Use simple, proven CSS approach
- Ensure button is truly fixed position
- Make sure it works with Streamlit's rendering

### Phase 4: Stabilize Chart Generation
- Focus on getting basic chart right first
- Add features incrementally
- Test each change before adding more

### Phase 5: Test & Validate
- Test with PCE data
- Verify all core features work
- Document what works and what doesn't

## What to Keep

✅ Core functionality:
- CSV upload and parsing
- Image upload
- Vision analysis (simplified)
- Chart generation (simplified)
- Basic chatbot

✅ Essential features:
- Session save/load
- Chart rendering
- Summary generation

## What to Remove/Simplify

❌ Remove:
- All debug statements
- Overly complex validation
- Redundant error messages
- Confusing prompt instructions

🔧 Simplify:
- AI prompts (make them shorter)
- Floating button CSS (use proven approach)
- Error handling (less verbose)

## Implementation

I'll create clean versions of:
1. `app.py` - Remove debug, fix floating button
2. `ai_client.py` - Simplify prompts
3. Test with your PCE data
4. Verify stability

Ready to proceed?
