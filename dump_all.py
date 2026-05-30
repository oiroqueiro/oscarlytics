import json
import pandas as pd

xls = pd.ExcelFile('apps/portfolio/content.xlsx')
data = {}
for sheet in xls.sheet_names:
    df = pd.read_excel('apps/portfolio/content.xlsx', sheet_name=sheet)
    data[sheet] = df.to_dict(orient="records")

with open('all_content.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
