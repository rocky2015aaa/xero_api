from flask import session, redirect, url_for, request, render_template, json
from xero_python.accounting import AccountingApi, Item, Items
from xero_python.exceptions import AccountingBadRequestException
from xero_python.utils import getvalue
from .utils import jsonify, serialize_model
from app import app, xero, api_client
from .services import obtain_xero_oauth2_token, store_xero_oauth2_token, xero_token_required, get_xero_tenant_id

@app.route("/")
def index():
    xero_access = dict(obtain_xero_oauth2_token() or {})
    return render_template(
        "code.html",
        title="Home | oauth token",
        code=json.dumps(xero_access, sort_keys=True, indent=4),
    )

@app.route("/login")
def login():
    redirect_url = url_for("oauth_callback", _external=True)
    session["state"] = app.config["STATE"]
    try:
        response = xero.authorize(callback_uri=redirect_url, state=session["state"])
    except Exception as e:
        print(e)
        raise
    return response

@app.route("/callback")
def oauth_callback():
    if request.args.get("state") != session["state"]:
        return "Error, state doesn't match, no token for you."
    try:
        response = xero.authorized_response()
    except Exception as e:
        print(e)
        raise
    if response is None or response.get("access_token") is None:
        return "Access denied: response=%s" % response
    store_xero_oauth2_token(response)
    return redirect(url_for("index", _external=True))

@app.route("/logout")
def logout():
    store_xero_oauth2_token(None)
    return redirect(url_for("index", _external=True))


@app.route("/create_items")
@xero_token_required
def create_items():
    xero_tenant_id = get_xero_tenant_id()
    accounting_api = AccountingApi(api_client)
    summarize_errors = 'True'
    idempotency_key = 'KEY_VALUE'

    item = Item(
        code = "abcXYZ123",
        name = "HelloWorld",
        description = "Foobar"
    )

    items = Items( 
        items = [item])
    unitdp = 4
    try:
        created_items = accounting_api.create_items(xero_tenant_id, items, summarize_errors, unitdp, idempotency_key)
    except AccountingBadRequestException as exception:
        sub_title = "Error: " + exception.reason
        code = jsonify(exception.error_data)
    else:
        sub_title = "Item {} created.".format(
            getvalue(created_items, "items.0.name", "")
        )
        code = serialize_model(created_items)

    return render_template(
        "code.html", title="Create Items", code=code, sub_title=sub_title
    )
