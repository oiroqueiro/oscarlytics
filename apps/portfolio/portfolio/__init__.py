from flask import Flask
import flask
import markupsafe
flask.Markup = markupsafe.Markup # Shim for Flask 2.3+ compatibility with old extensions
from flask_mail import Mail
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flaskext.markdown import Markdown
import meilisearch


portfolio = Flask(__name__)
portfolio.config.from_object(Config)

# Emails
mail = Mail(portfolio)

# Database
db = SQLAlchemy(portfolio)
migrate = Migrate(portfolio, db)

# Login
csrf = CSRFProtect(portfolio)
login = LoginManager(portfolio)

# Markdown for the detail of the project
Markdown(portfolio)

# Meilisearch
portfolio.meilisearch = meilisearch.Client(
    portfolio.config['MEILISEARCH_URL'],
    portfolio.config['MEILISEARCH_MASTER_KEY']
) if portfolio.config['MEILISEARCH_URL'] else None

from portfolio import routes, models
