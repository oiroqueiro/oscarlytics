from flask import render_template, send_from_directory, request, redirect, \
    url_for, flash, abort, jsonify, Response
from portfolio import portfolio, db
from portfolio.emails import send_email
from flask_login import current_user, login_user, logout_user
from portfolio.forms import LoginForm
from portfolio.models import Languages, Content, Users, Projects
import readtime
from datetime import datetime
from babel.dates import format_date, format_datetime, format_time
from babel.dates import get_month_names
import traceback
from cutecharts.charts import Radar
import requests
import os
import frontmatter
from werkzeug.utils import secure_filename

portfolio.app_context().push()


@portfolio.errorhandler(404)
def page_not_found(e):
    lang = request.lang
    proj_n = request.proj_n

    value = Content.get_value('', lang, '404_error')
    error400 = '' if not value else str(value['value'])
    value = Content.get_value('', lang, 'back_home')
    back_home = '' if not value else str(value['value'])
    
    context_data = inject_data()

    return render_template('404.html', error400=error400, back_home=back_home,
                           **context_data), 404


@portfolio.errorhandler(Exception)
def handle_all_errors(e):
    traceback.print_exc()
    response = {
        "error": str(e),
        "message": "An unexpected error occurred."
    }

    lang = getattr(request, 'lang', getattr(request.view_args, 'lang', None) if request.view_args else None)
    proj_n = getattr(request, 'proj_n', 1)

    if lang is None:
        lang = get_default_language()

    set_lang(lang)

    value = Content.get_value('', lang, 'danger')
    error_text = '' if not value else str(value['value'])
    value = Content.get_value('', lang, 'error_subtitle')
    error_subtitle = '' if not value else str(value['value'])
    value = Content.get_value('', lang, 'back_home')
    back_home = '' if not value else str(value['value'])

    return render_template('error.html', error_text=error_text,
                           error_subtitle=error_subtitle, back_home=back_home,
                           lang=lang, proj_n=proj_n), 500

# Managing the context processor with multilanguage and title slugs for projects


@portfolio.before_request
def set_lang(lang=None):
    request.lang = request.args.get('lang', lang)


@portfolio.before_request
def set_proj(proj_n=1):
    """Since when the user can change the language, the webpage should to be the
    same, I need to save a reference to the exact line for the language that
    was changed, the id is different for every row (so if the user change the
    language, cannot find the same id for different language), the title_slug
    could change if the user wants to translate the titles, so I will use the
    project_n with the date to define the project that needs to translate

    Keyword arguments:
    date date of the project
    proj_n number of the project inside the date

    """

    request.proj_n = request.args.get('proj_n', proj_n)


@portfolio.before_request
def set_date(proj_date=None):
    request.proj_date = request.args.get('proj_date', proj_date)


@portfolio.before_request
def set_slug(slug=None):
    request.title_slug = request.args.get('title_slug', slug)


@portfolio.context_processor
def inject_data():
    lang = request.lang
    proj_n = request.proj_n
    proj_date = request.proj_date
    title_slug = request.title_slug

    languages = list([str(l) for l in Languages.get_all()])

    menu_home = menu_about = menu_contact = menu_projects = menu_manage = \
        menu_manage_home = menu_manage_about = menu_manage_projects = \
        menu_manage_contact = menu_manage_logout = foot = search_hint = \
        gtm_key = recaptcha_site_key = ''

    try:
        value = Content.get_value('', lang, 'menu_home')
        menu_home = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'menu_about')
        menu_about = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'menu_contact')
        menu_contact = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'menu_projects')
        menu_projects = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'menu_manage')
        menu_manage = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'menu_manage_home')
        menu_manage_home = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'menu_manage_about')
        menu_manage_about = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'menu_manage_projects')
        menu_manage_projects = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'menu_manage_contact')
        menu_manage_contact = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'menu_manage_logout')
        menu_manage_logout = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'foot')
        foot = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'search')
        search_hint = '' if not value else str(value['value'])

        value = Content.get_value('', lang, 'menu_manage_upload')
        menu_manage_upload = '' if not value else str(value['value'])

        gtm_key = portfolio.config['GOOGLE_TAGMANAGER_KEY']

        # Google ReCaptcha v3
        recaptcha_site_key = portfolio.config['RECAPTCHA_SITE_KEY']

    except KeyError as k:
        abort(500, k)

    return dict(languages=languages,
                menu_home=menu_home, menu_about=menu_about,
                menu_contact=menu_contact, menu_projects=menu_projects,
                menu_manage=menu_manage, menu_manage_home=menu_manage_home,
                menu_manage_upload=menu_manage_upload,
                menu_manage_about=menu_manage_about,
                menu_manage_projects=menu_manage_projects,
                menu_manage_contact=menu_manage_contact,
                menu_manage_logout=menu_manage_logout, foot=foot,
                proj_n=proj_n, proj_date=proj_date, title_slug=title_slug,
                search_hint=search_hint, gtm_key=gtm_key,
                recaptcha_site_key=recaptcha_site_key)

# Functions


def get_default_language():
    available_langs = [str(l) for l in Languages.get_all()]
    best_match = request.accept_languages.best_match(available_langs)
    return best_match if best_match else 'en'


def replace_image_tags(text, img_n, image):
    '''
    Function to replace the string <img>image(n)</img> with the html needed
    to render the images in a responsive way

    text: the text where need to replace
    img_n: the number of image to replace (image1, image2 or image3)
    image: the name of the image

    return modified_text: the text ready to render
    '''

    replacement_html = f'''<img loading="lazy" decoding="async"
                        src="{url_for('static', filename='img/projects/')}{image}_1110.jpg"
                        srcset="{url_for('static', filename='img/projects/')}{image}_545x.webp 545w,
                                {url_for('static', filename='img/projects/')}{image}_600x.webp 600w,
                                {url_for('static', filename='img/projects/')}{image}_700x.webp 700w,
                                {url_for('static', filename='img/projects/')}{image}_1110x.webp 1110w"
                        sizes="(max-width: 575px) 545px,
                                (max-width: 767px) 600px,
                                (max-width: 991px) 700px,
                                1110px"
                        class="w-100 card-img-top img-fluid"
                         alt="{image}"
                        width="1200"
                        height="800">'''

    modified_text = text.replace(f"<img>{img_n}</img>", replacement_html)

    return modified_text


def replace_link_tag(text, proj_link):
    links = [proj_link.link1, proj_link.link2, proj_link.link3,
             proj_link.link4, proj_link.link5]

    for i in range(5):
        text = text.replace(f"<lnk>link{i+1}</lnk>", links[i])

    return text


def get_date_name(language, date):
    """"Function to get the name of the month in the selected language

    Keyword arguments:
    language -- iso code
    date
    Return: the date
    """

    date_ojb = datetime.strptime(str(date), '%Y-%m-%d')
    day = date_ojb.day
    month_number = date_ojb.month
    year = date_ojb.year

    return f"{get_month_names(locale=language)[month_number]} {day}, {year}"


def get_lang_name_proj(proj_id):
    langid = Projects.query.filter_by(id=proj_id).first().languageid
    return Languages.query.filter_by(id=langid).first().language


# Views


# Healthcheck

@portfolio.route('/~/health/')
def health():
    return 'ok'

# index


@portfolio.route('/')
@portfolio.route('/index/')
@portfolio.route('/<lang>/index/')
def index(lang=None, proj_date=None, proj_n=1, title_slug=None):
    if lang is None:
        lang = get_default_language()

    set_lang(lang)
    set_proj(proj_n)
    set_date(proj_date)
    set_slug(title_slug)

    # value = Content.get_value('', lang, 'menu_home')
    #    menu_home = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'get_touch')
    get_touch = '' if not value else str(value['value'])

    value = Content.get_value('index', lang, 'hello')
    hello = '' if not value else str(value['value'])

    value = Content.get_value('index', lang, 'name')
    name = '' if not value else str(value['value'])

    value = Content.get_value('index', lang, 'subtitle')
    subtitle = '' if not value else str(value['value'])

    return render_template('index.html', lang=lang, hello=hello, name=name,
                           subtitle=subtitle, get_touch=get_touch)

# about


@portfolio.route('/about/')
@portfolio.route('/<lang>/about/')
def about(lang=None, proj_date=None, proj_n=1, title_slug=None):
    if lang is None:
        lang = get_default_language()

    set_lang(lang)
    set_proj(proj_n)
    set_date(proj_date)
    set_slug(title_slug)

    value = Content.get_value('about', lang, 'hello')
    hello = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'parragraph1')
    parragraph1 = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'parragraph2')
    parragraph2 = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'parragraph3')
    parragraph3 = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'parragraph4')
    parragraph4 = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'parragraph5')
    parragraph5 = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'parragraph6')
    parragraph6 = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'skills_title')
    skills_title = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'skill1')
    skill1 = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'skill2')
    skill2 = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'skill3')
    skill3 = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'skill4')
    skill4 = '' if not value else str(value['value'])

    value = Content.get_value('about', lang, 'youtube')
    youtube = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'more')
    more = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'keyw_title')
    keyw_title = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'menu_projects')
    projs_n = '' if not value else str(value['value'])

    # Keywords
    langid = Languages.getid(lang)
    query_keyw = request.args.get('q')
    all_keywords, keywords_freq = Projects.get_all_keyws_and_freq(langid,
                                                                  query_keyw)
    all_keywords_and_freq = sorted(
        keywords_freq.items(), key=lambda x: [1], reverse=True)
    x, y = zip(*all_keywords_and_freq)
    x = list(x)
    y = list(y)

    # Creating the charts

    chart = Radar(keyw_title)
    chart.set_options(labels=x)
    chart.add_series(projs_n, y)

    html = chart.render(dest='/tmp/render.html')

    return render_template('about/index.html', lang=lang, hello=hello,
                           parragraph1=parragraph1, parragraph2=parragraph2,
                           parragraph3=parragraph3, parragraph4=parragraph4,
                           parragraph5=parragraph5, parragraph6=parragraph6,
                           skills_title=skills_title, skill1=skill1,
                           skill2=skill2, skill3=skill3, skill4=skill4, more=more,
                           youtube=youtube, plot=html)


# projects


@portfolio.route('/projects/', methods=['GET', 'POST'])
@portfolio.route('/projects/<keyw>/', methods=['GET', 'POST'])
@portfolio.route('/<lang>/projects/', methods=['GET', 'POST'])
@portfolio.route('/<lang>/projects/<keyw>/', methods=['GET', 'POST'])
def projects(lang=None, proj_date=None, proj_n=None, title_slug=None,
             keyw=None):
    if lang is None:
        lang = get_default_language()

    set_lang(lang)
    set_proj(proj_n)
    set_date(proj_date)
    set_slug(title_slug)

    langid = Languages.getid(lang)

    # Keywords
    query_keyw = request.args.get('q')
    all_keywords, keywords_freq = Projects.get_all_keyws_and_freq(langid,
                                                                  query_keyw)
    # Projects. Main template

    value = Content.get_value('', lang, 'keyw_title')
    keyw_title = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'search_keyw')
    key_search = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'more')
    more = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'view_details')
    view_details = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'previous')
    previous = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'next')
    next = '' if not value else str(value['value'])

    page = request.args.get('page', 1, type=int)

    projs = Projects.query

    if keyw:
        projs = projs.filter(Projects.languageid == langid,
                             Projects.keywords.like(f"%{keyw}%"))
    elif query_keyw:
        return redirect(url_for('search', lang=lang, q=query_keyw))
    else:
        projs = projs.filter(Projects.languageid == langid)

    projs = (
        projs
        .order_by(Projects.date.desc(), Projects.project_n.desc())
        .paginate(page=page, per_page=portfolio.config['PROJECTS_PAGE'],
                  error_out=False)
    )

    next_url = url_for('projects', lang=lang, keyw=keyw, proj_n=proj_n,
                       proj_date=proj_date, page=projs.next_num) \
        if projs.has_next else None

    prev_url = url_for('projects', lang=lang, proj_n=proj_n,
                       proj_date=proj_date, page=projs.prev_num) \
        if projs.has_prev else None

    return render_template('projects/index.html', lang=lang, projs=projs.items,
                           page=page, next_url=next_url, prev_url=prev_url,
                           more=more, view_details=view_details, previous=previous, next=next,
                           all_keywords=all_keywords,
                           keywords_freq=keywords_freq, keyw_title=keyw_title,
                           keyw=keyw, proj_n=proj_n, proj_date=proj_date,
                           get_date_name=get_date_name, key_search=key_search)


@portfolio.route('/project/<proj_date>/<proj_n>/<title_slug>/')
@portfolio.route('/<lang>/project/<proj_date>/<proj_n>/<title_slug>/')
def project(lang=None, proj_date=None, proj_n=1, title_slug=None):
    if lang is None:
        lang = get_default_language()

    project = Projects.get_by_projn(Languages.getid(lang), proj_date, proj_n)

    set_lang(lang)
    set_proj(proj_n)
    set_date(proj_date)
    set_slug(project.title_slug)

    value = Content.get_value('', lang, 'keyw_title')
    keyw_title = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'project_action')
    header_action = 'Action' if not value else str(value['value'])

    value = Content.get_value('', lang, 'project_resolution')
    header_resolution = 'Resolution' if not value else str(value['value'])

    value = Content.get_value('', lang, 'read')
    read = '' if not value else str(value['value'])

    time_reading = str(readtime.
                       of_markdown(" ".join(
                           [project.resume if project.resume else '',
                            project.exposition if project.exposition else '',
                            project.action if project.action else '',
                            project.resolution if project.resolution else '']))
                       ).replace('read', read)

    # Create the replacements for the images
    def process_images(text):
        if not text: return text
        text = replace_image_tags(text, 'image1', project.image1)
        text = replace_image_tags(text, 'image2', project.image2)
        text = replace_image_tags(text, 'image3', project.image3)
        text = replace_image_tags(text, 'image4', project.image4)
        text = replace_image_tags(text, 'image5', project.image5)
        return text

    project.exposition = process_images(project.exposition)
    project.action = process_images(project.action)
    project.resolution = process_images(project.resolution)

    return render_template('projects/project_detail.html', lang=lang,
                           proj_date=proj_date, proj_n=proj_n,
                           title_slug=title_slug, project=project,
                           keyw_title=keyw_title, time_reading=time_reading,
                           get_date_name=get_date_name,
                           header_action=header_action,
                           header_resolution=header_resolution)


# contact

@portfolio.route('/contact/', methods=['GET', 'POST'])
@portfolio.route('/<lang>/contact/', methods=['GET', 'POST'])
def contact(lang=None, proj_date=None, proj_n=1, title_slug=None):
    if lang is None:
        lang = get_default_language()

    set_lang(lang)
    set_proj(proj_n)
    set_date(proj_date)
    set_slug(title_slug)

    value = Content.get_value('contact', lang, 'title')
    title = '' if not value else str(value['value'])

    value = Content.get_value('contact', lang, 'subtitle')
    subtitle = '' if not value else str(value['value'])

    value = Content.get_value('contact', lang, 'first_name')
    first_name = '' if not value else str(value['value'])

    value = Content.get_value('contact', lang, 'last_name')
    last_name = '' if not value else str(value['value'])

    value = Content.get_value('contact', lang, 'email')
    email = '' if not value else str(value['value'])

    value = Content.get_value('contact', lang, 'message')
    message = '' if not value else str(value['value'])

    value = Content.get_value('contact', lang, 'submit')
    submit = '' if not value else str(value['value'])

    value = Content.get_value('contact', lang, 'email_subject')
    email_subject = '' if not value else str(value['value'])

    # Google ReCaptcha v3
    recaptcha_site_key = portfolio.config['RECAPTCHA_SITE_KEY']
    recaptcha_secret_key = portfolio.config['RECAPTCHA_SECRET_KEY']

    if request.method == 'POST':
        # Verify reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')

        if not recaptcha_response:
            flash('reCAPTCHA verification failed. Please try again.', 'danger')
            return redirect(request.url)

        verification_url = 'https://www.google.com/recaptcha/api/siteverify'
        verification_data = {
            'secret': recaptcha_secret_key,
            'response': recaptcha_response,
            'remoteip': request.remote_addr
        }

        verification_result = requests.post(
            verification_url, data=verification_data).json()
        score_recaptcha = verification_result.get('score')

        # Emailing

        first_name_post = request.form['First Name']
        last_name_post = request.form['Last Name']
        email_post = request.form['Email']
        message_post = request.form['Type your message...']

        if verification_result.get('success'):
            if verification_result.get('score') < 0.7:
                email_subject = f'[SPAM] {email_subject}'
            message_post = f'{message_post} \n\n***score: {score_recaptcha}'
        else:
            email_subject = f'[probably SPAM] {email_subject}'
            message_post = \
                f'{message_post} \n\n***result: {verification_result}'

        msg_body = f"Name: {first_name_post} {last_name_post}\n\nEmail: \
            {email_post}\n\nMessage:\n {message_post}"

        send_email(portfolio.config['MAIL_USERNAME'],
                   portfolio.config['MAIL_RECIPIENT'], email_subject, msg_body)

        flash('Your message has been sent successfully!', 'success')

        return redirect(request.url)

    return render_template('contact/index.html', lang=lang, title=title,
                           subtitle=subtitle, first_name=first_name,
                           last_name=last_name, email=email, message=message,
                           submit=submit, recaptcha_site_key=recaptcha_site_key)

# search


@portfolio.route('/search/')
@portfolio.route('/<lang>/search/')
def search(lang=None, proj_date=None, proj_n=1, title_slug=None):
    if lang is None:
        lang = get_default_language()

    set_lang(lang)
    set_proj(proj_n)
    set_date(proj_date)
    set_slug(title_slug)

    query = request.args.get('q')

    if not query:
        return redirect(request.referrer)

    # Projects

    value = Content.get_value('', lang, 'more')
    more = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'view_details')
    view_details = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'previous')
    previous = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'next')
    next = '' if not value else str(value['value'])

    page = request.args.get('page', 1, type=int)

    langid = Languages.getid(lang)

    projs, proj_total = Projects.search(query,
                                         page,
                                         portfolio.config['PROJECTS_PAGE'],
                                         langid=langid)

    next_url = url_for('search', q=query, page=page + 1) \
        if proj_total > page * portfolio.config['PROJECTS_PAGE'] else None

    prev_url = url_for('search', q=query, page=(page - 1)) \
        if page > 1 else None

    return render_template('search/index.html', lang=lang, projs=projs,
                           page=page, next_url=next_url, prev_url=prev_url,
                           more=more, view_details=view_details, previous=previous, next=next,
                           proj_n=proj_n, proj_date=proj_date,
                           get_date_name=get_date_name,
                           get_lang_name_proj=get_lang_name_proj)


# login


@portfolio.route(f"/{portfolio.config['PORTFOLIO_LOGIN_URL']}/",
                 methods=['GET', 'POST'])
@portfolio.route(f"/<lang>/{portfolio.config['PORTFOLIO_LOGIN_URL']}/",
                 methods=['GET', 'POST'])
def login(lang=None, proj_date=None, proj_n=1, title_slug=None):
    if lang is None:
        lang = get_default_language()

    set_lang(lang)
    set_proj(proj_n)
    set_date(proj_date)
    set_slug(title_slug)

    if current_user.is_authenticated:
        return redirect(url_for('index', lang=lang))

    form = LoginForm()

    value = Content.get_value('', lang, 'username')
    form.username.label.text = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'password')
    form.password.label.text = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'rememberme')
    form.remember_me.label.text = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'signin')
    form.submit.label.text = '' if not value else str(value['value'])

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            value = Content.get_value('', lang, 'errorlogin')
            flash('' if not value else value['value'])

            return redirect(url_for('login', lang=lang))

        login_user(user, remember=form.remember_me.data)

        return redirect(url_for('index', lang=lang))

    value = Content.get_value('', lang, 'login_subtitle')
    login_subtitle = '' if not value else str(value['value'])

    value = Content.get_value('', lang, 'back_home')
    back_home = '' if not value else str(value['value'])

    return render_template('login.html', form=form, lang=lang,
                           signin=form.submit.label.text,
                           login_subtitle=login_subtitle,
                           back_home=back_home)

# logout


@portfolio.route(f"/{portfolio.config['PORTFOLIO_LOGOUT_URL']}/",
                 methods=['GET', 'POST'])
@portfolio.route(f"/<lang>/{portfolio.config['PORTFOLIO_LOGOUT_URL']}/",
                 methods=['GET', 'POST'])
def logout(lang=None, proj_date=None, proj_n=1, title_slug=None):
    if lang is None:
        lang = get_default_language()

    set_lang(lang)
    set_proj(proj_n)
    set_date(proj_date)
    set_slug(title_slug)

    logout_user()
    return redirect(url_for('index', lang=lang))

# manifest


@portfolio.route('/manifest.webmanifest')
def manifest():
    return send_from_directory('static', 'manifest.webmanifest')

# --- ADMIN PANEL ---
from flask_login import login_required
import os
import frontmatter
from datetime import datetime
from werkzeug.utils import secure_filename

@portfolio.route('/manage/dashboard/', methods=['GET'])
@portfolio.route('/<lang>/manage/dashboard/', methods=['GET'])
@login_required
def dashboard(lang=None):
    if lang is None:
        lang = get_default_language()
    set_lang(lang)
    t = Content.get_template_texts('dashboard', lang)
    return render_template('admin/dashboard.html', lang=lang, t=t)

@portfolio.route('/manage/reload_yaml/', methods=['POST'])
@portfolio.route('/<lang>/manage/reload_yaml/', methods=['POST'])
@login_required
def reload_yaml(lang=None):
    from portfolio.init_content import init_content
    if lang is None:
        lang = get_default_language()
    set_lang(lang)
    init_content()
    flash('YAML Content reloaded successfully.', 'success')
    return redirect(url_for('dashboard', lang=lang))

@portfolio.route('/manage/projects/', methods=['GET'])
@portfolio.route('/<lang>/manage/projects/', methods=['GET'])
@login_required
def manage_projects(lang=None):
    if lang is None:
        lang = get_default_language()
    set_lang(lang)
    t = Content.get_template_texts('manage_projects', lang)
    try:
        langid = Languages.getid(lang)
        projs = Projects.query.filter(Projects.languageid == langid).order_by(Projects.date.desc(), Projects.project_n.desc()).all()
    except Exception as e:
        projs = []
    return render_template('admin/manage_projects.html', lang=lang, projs=projs, t=t, get_date_name=get_date_name)

@portfolio.route('/manage/upload_project/', methods=['GET', 'POST'])
@portfolio.route('/<lang>/manage/upload_project/', methods=['GET', 'POST'])
@login_required
def upload_project(lang=None):
    if lang is None:
        lang = get_default_language()
    set_lang(lang)

    if request.method == 'POST':
        if 'markdown_file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['markdown_file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and file.filename.endswith('.md'):
            # Parse the markdown file
            try:
                # Read the file content
                file_content = file.read().decode('utf-8')
                post = frontmatter.loads(file_content)
                
                # Extract metadata
                title = post.get('title', 'Untitled')
                p_lang = post.get('language', 'en').lower()
                date_str = post.get('date', datetime.today().strftime('%Y-%m-%d'))
                date_obj = date_str if isinstance(date_str, datetime) else datetime.strptime(str(date_str), '%Y-%m-%d').date()
                project_n = int(post.get('project_n', 1))
                keywords = post.get('keywords', '')
                if isinstance(keywords, list):
                    keywords = ', '.join(keywords)
                
                image_title = post.get('image_title', '')
                image1 = post.get('image1', '')
                image2 = post.get('image2', '')
                image3 = post.get('image3', '')
                link1 = post.get('link1', '')
                link2 = post.get('link2', '')
                link3 = post.get('link3', '')
                link4 = post.get('link4', '')
                link5 = post.get('link5', '')

                # The main content body
                content_body = post.content

                # Resolve language ID
                lang_id_obj = Languages.query.filter(Languages.language == p_lang).first()
                if not lang_id_obj:
                    flash(f'Language {p_lang} not found in database.', 'danger')
                    return redirect(request.url)
                
                lang_id = lang_id_obj.id

                # Generate slug
                title_slug = Projects.set_title_slug(lang_id, title)

                # Check if exists to update or insert
                project_item = Projects.query.filter(Projects.date == date_obj,
                                                     Projects.languageid == lang_id,
                                                     Projects.project_n == project_n).first()

                if not project_item:
                    project_item = Projects(
                        date=date_obj, languageid=lang_id, project_n=project_n,
                        title=title, title_slug=title_slug,
                        resume="", exposition=content_body, # Storing unified content in exposition temporarily
                        action="", resolution="", keywords=keywords,
                        link1=link1, link2=link2, link3=link3, link4=link4, link5=link5,
                        image_title=image_title, image1=image1, image2=image2, image3=image3
                    )
                    db.session.add(project_item)
                else:
                    project_item.title = title
                    project_item.title_slug = title_slug
                    project_item.exposition = content_body
                    project_item.keywords = keywords
                    project_item.image_title = image_title
                    project_item.image1 = image1
                    project_item.image2 = image2
                    project_item.image3 = image3
                    project_item.link1 = link1
                    project_item.link2 = link2
                    project_item.link3 = link3
                    project_item.link4 = link4
                    project_item.link5 = link5
                
                db.session.commit()

                # --- PERSISTENCE ---
                # Save the uploaded file to the persistent mounted volume
                mounted_dir = os.path.join(os.path.dirname(__file__), 'mounted', 'projects')
                os.makedirs(mounted_dir, exist_ok=True)
                
                # We format the filename to match existing ones: YYYY-MM-DD-lang-slug.md
                safe_slug = secure_filename(title_slug)
                date_str_file = date_obj.strftime('%Y-%m-%d')
                persistent_filename = f"{date_str_file}-{p_lang}-{safe_slug}.md"
                persistent_filepath = os.path.join(mounted_dir, persistent_filename)
                
                try:
                    # Write the raw frontmatter post back to disk
                    with open(persistent_filepath, 'wb') as f:
                        frontmatter.dump(post, f)
                except Exception as e:
                    print(f"Error saving persistent file: {e}")

                flash('Project successfully uploaded and indexed.', 'success')
                return redirect(url_for('dashboard', lang=lang))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error processing Markdown: {str(e)}', 'danger')
                return redirect(request.url)

    t = Content.get_template_texts('upload', lang)
    return render_template('admin/upload.html', lang=lang, t=t)


@portfolio.route('/manage/edit_project/<int:proj_id>/', methods=['GET', 'POST'])
@portfolio.route('/<lang>/manage/edit_project/<int:proj_id>/', methods=['GET', 'POST'])
@login_required
def edit_project(proj_id, lang=None):
    if lang is None:
        lang = get_default_language()
    set_lang(lang)

    project_item = Projects.query.get_or_404(proj_id)
    lang_obj = Languages.query.get(project_item.languageid)
    p_lang = lang_obj.language.lower() if lang_obj else 'en'

    if request.method == 'POST':
        # Retrieve form data
        title = request.form.get('title', project_item.title)
        keywords = request.form.get('keywords', project_item.keywords)
        exposition = request.form.get('exposition', project_item.exposition)
        date_str = request.form.get('date', project_item.date.strftime('%Y-%m-%d'))
        project_n = request.form.get('project_n', project_item.project_n, type=int)
        
        image_title = request.form.get('image_title', project_item.image_title or '')
        image1 = request.form.get('image1', project_item.image1 or '')
        image2 = request.form.get('image2', project_item.image2 or '')
        image3 = request.form.get('image3', project_item.image3 or '')
        image4 = request.form.get('image4', project_item.image4 or '')
        image5 = request.form.get('image5', project_item.image5 or '')
        link1 = request.form.get('link1', project_item.link1 or '')
        link2 = request.form.get('link2', project_item.link2 or '')
        link3 = request.form.get('link3', project_item.link3 or '')
        link4 = request.form.get('link4', project_item.link4 or '')
        link5 = request.form.get('link5', project_item.link5 or '')

        try:
            date_obj = datetime.strptime(str(date_str), '%Y-%m-%d').date()
        except ValueError:
            date_obj = project_item.date

        # Generate a new slug if the title has changed. Otherwise, keep the old one.
        if title != project_item.title:
            title_slug = Projects.set_title_slug(project_item.languageid, title)
        else:
            title_slug = project_item.title_slug

        # Update the database
        project_item.title = title
        project_item.title_slug = title_slug
        project_item.date = date_obj
        project_item.project_n = project_n
        project_item.keywords = keywords
        project_item.exposition = exposition
        project_item.image_title = image_title
        project_item.image1 = image1
        project_item.image2 = image2
        project_item.image3 = image3
        project_item.image4 = image4
        project_item.image5 = image5
        project_item.link1 = link1
        project_item.link2 = link2
        project_item.link3 = link3
        project_item.link4 = link4
        project_item.link5 = link5

        db.session.commit()

        # --- PERSISTENCE ---
        # Generate the Markdown representation and save to the persistent volume
        mounted_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mounted', 'projects')
        os.makedirs(mounted_dir, exist_ok=True)
        
        # We format the filename to match YYYY-MM-DD-lang-slug.md
        safe_slug = secure_filename(title_slug)
        date_str_file = date_obj.strftime('%Y-%m-%d')
        persistent_filename = f"{date_str_file}-{p_lang}-{safe_slug}.md"
        persistent_filepath = os.path.join(mounted_dir, persistent_filename)

        # Construct the frontmatter
        post = frontmatter.Post(exposition)
        post['title'] = title
        post['language'] = p_lang
        post['date'] = date_str_file
        post['project_n'] = project_n
        post['keywords'] = keywords
        if image_title: post['image_title'] = image_title
        if image1: post['image1'] = image1
        if image2: post['image2'] = image2
        if image3: post['image3'] = image3
        if link1: post['link1'] = link1
        if link2: post['link2'] = link2
        if link3: post['link3'] = link3
        if link4: post['link4'] = link4
        if link5: post['link5'] = link5

        try:
            with open(persistent_filepath, 'wb') as f:
                frontmatter.dump(post, f)
        except Exception as e:
            print(f"Error saving persistent file during edit: {e}")

        flash('Project successfully updated.', 'success')
        return redirect(url_for('manage_projects', lang=lang))

    t = Content.get_template_texts('edit_project', lang)
    return render_template('admin/edit_project.html', lang=lang, t=t, project=project_item)


@portfolio.route('/manage/restore_project/<int:proj_id>/', methods=['POST'])
@portfolio.route('/<lang>/manage/restore_project/<int:proj_id>/', methods=['POST'])
@login_required
def restore_project(proj_id, lang=None):
    if lang is None:
        lang = get_default_language()
    set_lang(lang)

    project_item = Projects.query.get_or_404(proj_id)
    lang_obj = Languages.query.get(project_item.languageid)
    p_lang = lang_obj.language.lower() if lang_obj else 'en'
    
    date_str_file = project_item.date.strftime('%Y-%m-%d')
    safe_slug = secure_filename(project_item.title_slug)
    persistent_filename = f"{date_str_file}-{p_lang}-{safe_slug}.md"
    
    mounted_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mounted', 'projects')
    persistent_filepath = os.path.join(mounted_dir, persistent_filename)

    if os.path.exists(persistent_filepath):
        try:
            os.remove(persistent_filepath)
            
            # --- Auto trigger sync to update database immediately ---
            try:
                from sync_projects import sync_projects
                sync_projects()
                flash('Persistent modification removed and original file restored successfully.', 'success')
            except Exception as se:
                flash(f'Persistent modification removed, but sync failed: {str(se)}', 'warning')
                
        except Exception as e:
            flash(f'Error deleting file: {str(e)}', 'danger')
    else:
        flash('No web-edited version found to restore. Project is already using the original source file.', 'info')

    return redirect(url_for('manage_projects', lang=lang))

@portfolio.route('/delete_project/<int:proj_id>', methods=['POST'])
@portfolio.route('/<lang>/delete_project/<int:proj_id>', methods=['POST'])
@login_required
def delete_project(proj_id, lang=None):
    if lang is None:
        lang = get_default_language()
    set_lang(lang)

    project_item = Projects.query.get_or_404(proj_id)
    lang_obj = Languages.query.get(project_item.languageid)
    p_lang = lang_obj.language.lower() if lang_obj else 'en'
    
    date_str_file = project_item.date.strftime('%Y-%m-%d')
    safe_slug = secure_filename(project_item.title_slug)
    persistent_filename = f"{date_str_file}-{p_lang}-{safe_slug}.md"
    
    mounted_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mounted', 'projects')
    persistent_filepath = os.path.join(mounted_dir, persistent_filename)

    # 1. Delete from mounted volume if it exists
    if os.path.exists(persistent_filepath):
        try:
            os.remove(persistent_filepath)
        except Exception as e:
            flash(f'Error deleting physical file: {str(e)}', 'danger')
    
    # 2. Delete from Database
    try:
        db.session.delete(project_item)
        db.session.commit()
        Projects.reindex() # update search index
        flash('Project deleted successfully from the database.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting project from database: {str(e)}', 'danger')

    return redirect(url_for('manage_projects', lang=lang))



@portfolio.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml dynamically."""
    from flask import Response
    import urllib.parse
    
    base_url = "https://" + request.host
    pages = []
    
    # Static pages for all active languages
    langs = Languages.query.all()
    for lang in langs:
        l = lang.language
        pages.append(url_for('index', lang=l))
        pages.append(url_for('about', lang=l))
        pages.append(url_for('projects', lang=l))
        pages.append(url_for('contact', lang=l))

    # Dynamic project pages
    all_projects = Projects.query.all()
    for proj in all_projects:
        lang_obj = Languages.query.get(proj.languageid)
        if lang_obj:
            pages.append(url_for('project', 
                                lang=lang_obj.language, 
                                proj_date=proj.date.strftime('%Y-%m-%d'), 
                                proj_n=proj.project_n, 
                                title_slug=proj.title_slug))

    xml_sitemap = render_template('sitemap.xml', pages=pages, base_url=base_url)
    return Response(xml_sitemap, mimetype='application/xml')

@portfolio.route('/<path:path>')
@portfolio.route('/<lang>/<path:path>')
def catch_all(path, lang=None):
    if lang is None:
        lang = get_default_language()
    print(f"***Non-existent route requested: {path}")
    abort(404)
