import pandas as pd
import json

# Load the CSV
df = pd.read_csv('mydata/01a-YoY-PCE.csv')

# Pivot from long to wide format
df_wide = df.pivot(index='date', columns='key', values='value').reset_index()

print("Pivoted data shape:", df_wide.shape)
print("\nColumns:", df_wide.columns.tolist())
print("\nFirst 5 rows:")
print(df_wide.head())

# Create a simple ECharts config
chart = {
    "title": {"text": "YoY PCE", "left": "center"},
    "tooltip": {"trigger": "axis"},
    "legend": {
        "data": ["YoY_pce_headline", "YoY_pce_core"],
        "bottom": "bottom"
    },
    "xAxis": {
        "type": "category",
        "data": df_wide['date'].tolist()
    },
    "yAxis": {
        "type": "value",
        "name": "Percent"
    },
    "series": [
        {
            "name": "YoY_pce_headline",
            "type": "line",
            "data": df_wide['YoY_pce_headline'].tolist(),
            "smooth": True
        },
        {
            "name": "YoY_pce_core",
            "type": "line",
            "data": df_wide['YoY_pce_core'].tolist(),
            "smooth": True
        }
    ]
}

print("\n\nChart JSON:")
print(json.dumps(chart, indent=2))

# Check data arrays
print(f"\n\nYoY_pce_headline data points: {len(chart['series'][0]['data'])}")
print(f"YoY_pce_core data points: {len(chart['series'][1]['data'])}")
print(f"X-axis data points: {len(chart['xAxis']['data'])}")
