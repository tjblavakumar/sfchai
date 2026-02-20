"""
SF CHAI - Sample Data Module
Provides sample CSV data for testing and demonstration.
"""

import pandas as pd
from io import StringIO


def get_sample_data(name: str = "sales"):
    """
    Get sample CSV data by name.
    
    Args:
        name: Sample data name ('sales', 'traffic', 'revenue')
        
    Returns:
        Tuple of (csv_data, csv_filename, description)
    """
    samples = {
        "sales": {
            "data": """Month,Product_A,Product_B,Product_C
Jan,120,180,90
Feb,135,195,85
Mar,150,210,95
Apr,165,225,100
May,180,240,110
Jun,195,255,120
Jul,210,270,130
Aug,225,285,140
Sep,240,300,150
Oct,255,315,160
Nov,270,330,170
Dec,300,350,190""",
            "description": "Monthly sales data for 3 products over a year"
        },
        "traffic": {
            "data": """Day,Website_Visits,Page_Views,Unique_Visitors
Mon,5420,12500,3200
Tue,6100,14200,3800
Wed,5900,13800,3600
Thu,6300,15000,4100
Fri,5800,13500,3500
Sat,3200,7800,2100
Sun,2800,6500,1800""",
            "description": "Weekly web traffic data"
        },
        "revenue": {
            "data": """Quarter,Revenue,Expenses,Profit
Q1_2023,125000,80000,45000
Q2_2023,145000,85000,60000
Q3_2023,168000,92000,76000
Q4_2023,195000,98000,97000
Q1_2024,210000,105000,105000
Q2_2024,235000,110000,125000""",
            "description": "Quarterly revenue, expenses, and profit data"
        }
    }
    
    if name not in samples:
        name = "sales"
    
    sample = samples[name]
    csv_data = pd.read_csv(StringIO(sample["data"]))
    
    return csv_data, f"{name}_sample.csv", sample["description"]


def list_samples():
    """
    List available sample data.
    
    Returns:
        Dict of sample names and descriptions
    """
    return {
        "sales": "Monthly sales data for 3 products (12 months)",
        "traffic": "Weekly website traffic data (7 days)",
        "revenue": "Quarterly revenue and profit data (6 quarters)"
    }
