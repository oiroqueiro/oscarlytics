import sys
import json

try:
    import pandas as pd
    df = pd.read_excel('apps/portfolio/content.xlsx')
    print(df.to_json(orient="records"))
except Exception as e:
    print(f"ERROR: {e}")
