# Grid Line Color Support

## What Are Grid Lines?
Grid lines are the light gray horizontal and vertical lines in the background of your chart that help you read values more easily.

## How to Change Grid Color

You can now customize the grid line color by saying any of these:

### Change Color
- "Change grid color to blue"
- "Make gridlines darker"
- "Change gridline color to #cccccc"
- "Set grid color to light blue"

### Hide/Show Grid
- "Hide grid" or "Remove gridlines"
- "Show grid" or "Show gridlines"

## Examples

**Make grid darker:**
```
"Change grid color to #cccccc"
```

**Make grid lighter:**
```
"Change grid color to #f5f5f5"
```

**Remove grid completely:**
```
"Hide grid"
```

**Custom color:**
```
"Change gridline color to light blue"
```

## Technical Details

### Implementation
- Added `grid.color` property to proposal structure
- Default color: `#e0e0e0` (light gray)
- Supports any hex color code or color name
- Applied to both x-axis and y-axis grid lines

### Modification Structure
```json
{
  "grid_updates": {
    "color": "#cccccc",
    "show": true
  }
}
```

## Status
✅ Implemented and ready to use

Just tell the chatbot what you want and it will understand!
