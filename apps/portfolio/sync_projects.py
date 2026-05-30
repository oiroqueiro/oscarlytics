import os
import frontmatter
from datetime import datetime
from portfolio import portfolio, db
from portfolio.models import Projects, Languages

def sync_projects():
    base_dir = os.path.join(os.path.dirname(__file__), 'content', 'projects')
    mounted_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mounted', 'projects')
    
    # Process base first, then mounted so mounted prevails
    directories = [base_dir, mounted_dir]

    # Localized headers map
    HEADER_MAP = {
        'es': {
            'resume': 'Resumen',
            'exposition': 'Exposición',
            'action': 'Acción',
            'resolution': 'Resolución'
        },
        'en': {
            'resume': 'Resume',
            'exposition': 'Exposition',
            'action': 'Action',
            'resolution': 'Resolution'
        }
    }

    print("🔄 Syncing projects...")
    
    for projects_dir in directories:
        if not os.path.exists(projects_dir):
            if projects_dir == base_dir:
                print(f"⚠️ Base directory {projects_dir} not found.")
            continue
            
        print(f"📂 Processing directory {projects_dir}...")
        for filename in os.listdir(projects_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(projects_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                # Metadata extraction
                title = post.get('title', 'Untitled')
                p_lang = post.get('language', 'en').lower()
                date_val = post.get('date', datetime.today().date())
                
                # Ensure date is a date object
                if isinstance(date_val, str):
                    try:
                        date_obj = datetime.strptime(date_val, '%Y-%m-%d').date()
                    except ValueError:
                        date_obj = datetime.today().date()
                else:
                    date_obj = date_val
                    
                project_n = int(post.get('project_n', 1))
                keywords = post.get('keywords', '')
                if isinstance(keywords, list):
                    keywords = ', '.join(keywords)
                
                image_title = post.get('image_title', '')
                image1 = post.get('image1', '')
                image2 = post.get('image2', '')
                image3 = post.get('image3', '')
                image4 = post.get('image4', '')
                image5 = post.get('image5', '')
                link1 = post.get('link1', '')
                link2 = post.get('link2', '')
                link3 = post.get('link3', '')
                link4 = post.get('link4', '')
                link5 = post.get('link5', '')
                
                content_body = post.content
                
                # Split content into sections if headers are present
                import re
                
                def extract_section(content, header_name):
                    # Find the header and everything until the next ## header
                    pattern = rf"## {header_name}\s*(.*?)(?=\n## |$)"
                    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
                    return ""

                # Get localized headers for the project language
                headers = HEADER_MAP.get(p_lang, HEADER_MAP['en'])
                
                resume = extract_section(content_body, headers['resume'])
                exposition = extract_section(content_body, headers['exposition'])
                action = extract_section(content_body, headers['action'])
                resolution = extract_section(content_body, headers['resolution'])

                # If no sections found, fallback to putting everything in exposition
                if not any([resume, exposition, action, resolution]):
                    exposition = content_body

                # Language lookup
                lang_obj = Languages.query.filter(Languages.language == p_lang).first()
                if not lang_obj:
                    print(f"⚠️ Language '{p_lang}' not found for {filename}. Skipping.")
                    continue
                
                lang_id = lang_obj.id

                # Upsert project
                project_item = Projects.query.filter(
                    Projects.date == date_obj,
                    Projects.languageid == lang_id,
                    Projects.project_n == project_n
                ).first()

                title_slug = Projects.set_title_slug(lang_id, title)

                if not project_item:
                    project_item = Projects(
                        date=date_obj, languageid=lang_id, project_n=project_n,
                        title=title, title_slug=title_slug,
                        resume=resume, exposition=exposition,
                        action=action, resolution=resolution, keywords=keywords,
                        link1=link1, link2=link2, link3=link3, link4=link4, link5=link5,
                        image_title=image_title, image1=image1, image2=image2, image3=image3,
                        image4=image4, image5=image5
                    )
                    db.session.add(project_item)
                    print(f"✅ Created: {title} ({p_lang})")
                else:
                    # Update existing fields
                    project_item.title = title
                    # Keep existing slug or update? 
                    # Usually better to keep unless title changed significantly.
                    # project_item.title_slug = title_slug 
                    project_item.resume = resume
                    project_item.exposition = exposition
                    project_item.action = action
                    project_item.resolution = resolution
                    project_item.keywords = keywords
                    project_item.image_title = image_title
                    project_item.image1 = image1
                    project_item.image2 = image2
                    project_item.image3 = image3
                    project_item.image4 = image4
                    project_item.image5 = image5
                    project_item.link1 = link1
                    project_item.link2 = link2
                    print(f"ℹ️ Updated: {title} ({p_lang})")

                db.session.commit()

            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

    # Reindex search
    print("🔍 Reindexing search engine...")
    Projects.reindex()
    print("✨ Sync complete.")

if __name__ == '__main__':
    with portfolio.app_context():
        sync_projects()
