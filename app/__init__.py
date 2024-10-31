import os
from logging.config import dictConfig
from flask import Flask
from flask_session import Session
from flask_oauthlib.contrib.client import OAuth
from xero_python.api_client import ApiClient
from xero_python.api_client.configuration import Configuration
from xero_python.api_client.oauth2 import OAuth2Token
from config import logging_settings

# Configure logging
dictConfig(logging_settings.default_settings)

# Configure main Flask application
app = Flask(__name__, template_folder='../templates')
app.config.from_object("config.default_settings")  # Load default settings from a module
app.config.from_pyfile("config.py", silent=True)  # Load additional settings from a config file

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = 'True'

if app.config["ENV"] != "production":
    # Allow OAuth2 loop to run over HTTP for local testing only
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Configure Flask-Session for persistent session management
Session(app)

# Configure Flask-OAuthlib application
oauth = OAuth(app)

xero = oauth.remote_app(
    name="xero",
    version="2",
    client_id=app.config["CLIENT_ID"],
    client_secret=app.config["CLIENT_SECRET"],
    endpoint_url="https://api.xero.com/",
    authorization_url="https://login.xero.com/identity/connect/authorize",
    access_token_url="https://identity.xero.com/connect/token",
    refresh_token_url="https://identity.xero.com/connect/token",
    scope=(
        "files projects payroll.timesheets accounting.attachments files.read accounting.budgets.read projects.read accounting.settings.read payroll.payslip accounting.transactions.read payroll.settings accounting.journals.read accounting.attachments.read payroll.payruns payroll.employees assets.read offline_access accounting.reports.read accounting.transactions accounting.contacts.read profile accounting.contacts accounting.settings openid email assets",
    ),
)  # Flask-OAuthlib application

# Configure Xero-Python SDK client
api_client = ApiClient(
    Configuration(
        debug=app.config["DEBUG"],
        oauth2_token=OAuth2Token(
            client_id=app.config["CLIENT_ID"],
            client_secret=app.config["CLIENT_SECRET"]
        )
    ),
    pool_threads=1,
)

from . import routes