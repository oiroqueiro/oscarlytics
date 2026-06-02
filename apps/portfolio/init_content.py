import os
import yaml
from portfolio import portfolio, db
from portfolio.models import Users, Languages, Content

def init_admin():
    admin_user = os.environ.get('ADMIN_USER')
    admin_pass = os.environ.get('ADMIN_PASSWORD')

    if not admin_user or not admin_pass:
        print("⚠️ ADMIN_USER or ADMIN_PASSWORD not set. Skipping admin creation.")
        return

    user = Users.query.filter_by(username=admin_user).first()
    if not user:
        user = Users(username=admin_user, email=f"{admin_user}@example.com")
        user.set_password(admin_pass)
        db.session.add(user)
        db.session.commit()
        print(f"✅ Admin user '{admin_user}' created successfully.")
    else:
        # Optionally update password on every restart just in case it was changed in .env
        user.set_password(admin_pass)
        db.session.commit()
        print(f"ℹ️ Admin user '{admin_user}' already exists. Password updated.")

def init_content():
    yaml_path = os.path.join(os.path.dirname(__file__), 'content', 'content.yaml')
    
    if not os.path.exists(yaml_path):
        print(f"⚠️ content.yaml not found at {yaml_path}. Skipping static content load.")
        return

    with open(yaml_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    if not data:
        return

    # Process languages
    if 'languages' in data:
        for lang_code in data['languages']:
            lang_id = lang_code.get('id', '').lower()
            if not lang_id:
                continue
                
            lang_exists = Languages.query.filter(Languages.language == lang_id).first()
            if not lang_exists:
                lang_item = Languages(language=lang_id)
                db.session.add(lang_item)
                db.session.commit()
                print(f"✅ Language '{lang_id}' added.")

    # Process static templates/content
    if 'content' in data:
        for lang_id, templates_dict in data['content'].items():
            lang_obj = Languages.query.filter(Languages.language == lang_id).first()
            if not lang_obj:
                print(f"⚠️ Language '{lang_id}' not found in DB. Skipping content.")
                continue
                
            for template_name, vars_dict in templates_dict.items():
                actual_template = '' if template_name == 'global' else template_name
                for variable, value in vars_dict.items():
                    content_item = Content.query.filter(
                        Content.template == actual_template,
                        Content.languageid == lang_obj.id,
                        Content.variable == variable
                    ).first()

                    # Convert to string to avoid NoneType issues, though YAML values might be ints
                    str_value = str(value) if value is not None else ""

                    if not content_item:
                        content_item = Content(
                            template=actual_template, 
                            languageid=lang_obj.id,
                            variable=variable, 
                            value=str_value
                        )
                        db.session.add(content_item)
                    else:
                        if str(content_item.value) != str_value:
                            content_item.value = str_value
                            
            db.session.commit()
            print(f"✅ Static content for '{lang_id}' loaded.")

def init_search():
    if not portfolio.meilisearch:
        print("⚠️ Meilisearch not configured. Skipping search initialization.")
        return

    try:
        # Configure filterable attributes for projects
        portfolio.meilisearch.index('portfolio_projects').update_filterable_attributes([
            'languageid'
        ])
        print("✅ Meilisearch filterable attributes configured.")
    except Exception as e:
        print(f"❌ Error configuring Meilisearch: {e}")

if __name__ == '__main__':
    # Push app context so SQLAlchemy works
    portfolio.app_context().push()
    print("🚀 Initializing Database...")
    db.create_all()
    init_admin()
    init_content()
    init_search()
    print("🏁 Initialization complete.")
