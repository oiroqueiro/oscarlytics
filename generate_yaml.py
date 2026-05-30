import pandas as pd
import yaml
import math
import os

xls = pd.ExcelFile('apps/portfolio/content.xlsx')
portfolio_df = pd.read_excel(xls, sheet_name='portfolio')
content_df = pd.read_excel(xls, sheet_name='content')

output = {
    "languages": [{"id": "en"}, {"id": "es"}],
    "content": {
        "en": {},
        "es": {}
    }
}

# Add all from 'portfolio' sheet -> global
for _, row in portfolio_df.iterrows():
    lang = row['language']
    var = row['variable']
    val = row['value']
    
    if isinstance(val, float) and math.isnan(val):
        val = ""
        
    if 'global' not in output['content'][lang]:
        output['content'][lang]['global'] = {}
    output['content'][lang]['global'][var] = str(val)

# Add all from 'content' sheet -> specific templates
for _, row in content_df.iterrows():
    lang = row['language']
    tmpl = row['template']
    var = row['variable']
    val = row['value']
    
    if isinstance(val, float) and math.isnan(val):
        val = ""
        
    if isinstance(tmpl, float) and math.isnan(tmpl):
        tmpl = "global"
        
    if tmpl not in output['content'][lang]:
        output['content'][lang][tmpl] = {}
        
    output['content'][lang][tmpl][var] = str(val)

# Write to YAML
yaml_path = 'apps/portfolio/content/content.yaml'
with open(yaml_path, 'w', encoding='utf-8') as f:
    f.write("# Contenido Estático de la Web\n")
    f.write("# Este fichero alimenta las traducciones y textos base del sitio.\n\n")
    yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("✅ content.yaml successfully generated.")
