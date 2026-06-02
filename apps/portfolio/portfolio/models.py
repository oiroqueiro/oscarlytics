from portfolio import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from collections import Counter
from slugify import slugify
from portfolio.search import add_to_index, remove_from_index, query_index
from flask import abort, current_app
from sqlalchemy import cast, VARCHAR, or_


# Searching class


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page, langid=None):
        if current_app.config['MEILISEARCH_URL'] is None:
            # Alternate search if no elasticsearch configured

            filters = []

            query_alt = cls.query
            if langid:
                query_alt = query_alt.filter(cls.languageid == langid)

            for column in cls.__searchable__:
                filters.append(cast(getattr(cls, column),
                               VARCHAR).ilike(f"%{expression}%"))
            query_alt = query_alt.filter(or_(*filters))

            projs_alt = [project for project in query_alt]

            # total of number of results
            total = len(projs_alt)

            # Paginate the results
            query_alt = query_alt.limit(per_page).offset((page - 1) * per_page)

            return projs_alt, total

        try:
            # Searching with Meilisearch
            filter_str = f"languageid = {langid}" if langid else None
            ids, total = query_index(cls.__tablename__, expression, page,
                                     per_page, filter=filter_str)
        except Exception as e:
            abort(500, e)

        if total == 0:
            return cls.query.filter_by(id=0), 0

        when = {}
        for i in range(len(ids)):
            when[ids[i]] = i

        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        if current_app.config['MEILISEARCH_URL'] is None:
            return

        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        if current_app.config['MEILISEARCH_URL'] is None:
            return

        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                try:
                    add_to_index(obj.__class__.__tablename__, obj)
                except Exception as e:
                    abort(500, e)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                try:
                    add_to_index(obj.__class__.__tablename__, obj)
                except Exception as e:
                    abort(500, e)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                try:
                    remove_from_index(obj.__class__.__tablename__, obj)
                except Exception as e:
                    abort(500, e)
        session._changes = None

    @classmethod
    def reindex(cls):
        if current_app.config['MEILISEARCH_URL'] is None:
            return

        for obj in cls.query:
            try:
                add_to_index(cls.__tablename__, obj)
            except Exception as e:
                abort(500, e)

# Event listeners


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

# Users


class Users(UserMixin, db.Model):
    _tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_user(self, uname):
        return Users.query.filter_by(username=uname).first()

    def get_all():
        return Users.query.all()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password_hash,
            'email': self.email
        }

# Languages


class Languages(db.Model):
    __tablename__ = 'languages'

    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(2), index=True, unique=True)

    def __repr__(self):
        # return '<Language {}>'.format(self.language)
        return self.language.lower()

    def get_all():
        return Languages.query.all()

    def upper(self):
        return self.language.upper()

    def getid(lang):
        return Languages.query.filter(Languages.language == lang).first().id

# Content of the Portfolio


class Content(db.Model):
    __tablename__ = 'portfolio_content'

    id = db.Column(db.Integer, primary_key=True)
    template = db.Column(db.String(100), index=True)
    variable = db.Column(db.String(100), index=True)
    languageid = db.Column(db.Integer, db.ForeignKey(
        'languages.id', name='fk_languageid'))
    value = db.Column(db.Text)

    def __repr__(self):
        return '<Content {} {} {} {}>'.format(self.template, self.variable,
                                              self.languageid, self.value)

    def get_value(tem, lang, var) -> dict:
        if lang is None:
            return dict()
        langid = Languages.query.filter(Languages.language == lang).first().id

        cont = Content.query.filter(Content.template == str(tem or ''),
                                    Content.languageid == langid,
                                    Content.variable == var).first()

        if cont:
            d = dict()
            d['value'] = cont.value
            return d
        else:
            return {}

    def get_template_texts(tem, lang) -> dict:
        if lang is None:
            return {}
        langid = Languages.query.filter(Languages.language == lang).first().id
        conts = Content.query.filter(Content.template == str(tem or ''),
                                     Content.languageid == langid).all()
        return {c.variable: c.value for c in conts}

# Projects


class Projects(SearchableMixin, db.Model):
    __tablename__ = 'portfolio_projects'
    __searchable__ = ['date', 'title', 'title_slug', 'resume', 'exposition',
                      'action', 'resolution', 'keywords']

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    # This colum is the project number within the date
    project_n = db.Column(db.Integer)
    languageid = db.Column(db.Integer, db.ForeignKey(
        'languages.id', name='fk_languageid'))
    title = db.Column(db.String(50), index=True)
    title_slug = db.Column(db.String(60), unique=False,
                           nullable=False, index=True)
    resume = db.Column(db.Text, index=True)
    exposition = db.Column(db.String())
    action = db.Column(db.String())
    resolution = db.Column(db.String())
    keywords = db.Column(db.String(), index=True)
    link1 = db.Column(db.String(250))
    link2 = db.Column(db.String(250))
    link3 = db.Column(db.String(250))
    link4 = db.Column(db.String(250))
    link5 = db.Column(db.String(250))
    image_title = db.Column(db.String(50))
    image1 = db.Column(db.String())
    image2 = db.Column(db.String())
    image3 = db.Column(db.String())
    image4 = db.Column(db.String())
    image5 = db.Column(db.String())

    def __repr__(self):
        return '<Project {} {} {} {}>'.format(self.date, self.languageid,
                                              self.title, self.resume)

    def get_by_id(proj_id):
        return Projects.query.filter(Projects.id == proj_id).first()

    def get_by_slug(lang_id, slug):
        return Projects.query.filter(Projects.languageid == lang_id,
                                     Projects.title_slug == slug).first()

    def get_by_projn(lang_id, proj_date, proj_n):
        return Projects.query.filter(Projects.languageid == lang_id,
                                     Projects.date == proj_date,
                                     Projects.project_n == proj_n).first()

    def get_all():
        return Projects.query.all()

    def get_all_keyws_and_freq(langid, q_keyw=None):
        """This function will get all the keywords of the projects
        and will calculate their frequencies

        Keyword arguments:

        Return: one tuple with the distinct keywords and one dictionary 
        with the frequencies
        """

        base_query = Projects.query.filter(Projects.languageid == langid)

        if q_keyw is not None:
            base_query = base_query.filter(Projects.keywords
                                           .ilike(f"%{q_keyw}%"))

        all_keyw = [tp.strip() for tuples in base_query
                    .with_entities(Projects.keywords).all()
                    for tp in tuples[0].split(',')]

        keyws = sorted(tuple(set(all_keyw)))

        keyws_freq = dict(Counter(all_keyw))

        return keyws, keyws_freq

    def set_title_slug(langid, title):
        title_slug = f"{slugify(title)}"
        saved = False
        count = 0
        while not saved:
            if not Projects.get_by_slug(langid, title_slug):
                saved = True
            else:
                count += 1
                title_slug = f"{slugify(title)}-{count}"

        return title_slug

# Login users


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))
