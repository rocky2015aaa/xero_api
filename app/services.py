from functools import wraps
from flask import session, redirect, url_for
from xero_python.identity import IdentityApi
from app import app, xero, api_client

# Configure token persistence and exchange point between Flask-OAuthlib and Xero-Python
@xero.tokengetter
@api_client.oauth2_token_getter
def obtain_xero_oauth2_token():
    """Retrieve the OAuth2 token from the session."""
    return session.get("token")

@xero.tokensaver
@api_client.oauth2_token_saver
def store_xero_oauth2_token(token):
    """Store the OAuth2 token in the session."""
    session["token"] = token
    session.modified = True

def xero_token_required(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        xero_token = obtain_xero_oauth2_token()
        if not xero_token:
            return redirect(url_for("login", _external=True))
        return function(*args, **kwargs)
    return decorator

def get_xero_tenant_id():
    token = obtain_xero_oauth2_token()
    if not token:
        return None
    identity_api = IdentityApi(api_client)
    for connection in identity_api.get_connections():
        if connection.tenant_type == "ORGANISATION":
            return connection.tenant_id
