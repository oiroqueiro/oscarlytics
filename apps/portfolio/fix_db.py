from portfolio import create_app, db
from portfolio.models import Content

app = create_app()

with app.app_context():
    print("ALL FOOT AND SIGNIN DB ENTRIES:")
    for v in ['foot', 'followme', 'signin', 'more']:
        for c in Content.query.filter_by(variable=v).all():
            print(f"[{c.variable}] template='{c.template}' lang='{c.languageid}' value='{c.value}'")
    
    # We want to clear the entire Content table and reseed to avoid weirdness
    print("Clearing Content table...")
    Content.query.delete()
    db.session.commit()
    print("Cleared.")

from init_content import init_content
with app.app_context():
    init_content()

with app.app_context():
    print("VERIFYING AFTER RE-INIT:")
    for v in ['foot', 'followme', 'signin', 'more']:
        for c in Content.query.filter_by(variable=v).all():
            print(f"[{c.variable}] template='{c.template}' lang='{c.languageid}' value='{c.value}'")
