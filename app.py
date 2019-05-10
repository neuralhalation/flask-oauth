from flask import Flask, redirect, url_for, session
from authorization import OAuthSignIn
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["OAUTH_CREDENTIALS"] = {
    "github": {
        "base_uri": "http://localhost:5000",
        "client_id": "<client id>",
        "secret": "<client secret>",
        "token_url": "https://github.com/login/oauth/access_token",
        "authorize_url": "https://github.com/login/oauth/authorize",
        "client_kwargs": {
            "scope": "user repo"
        },
        "authorization_kwargs": {
            "grant_type": "authorization_code"
        },
        "flow_type": "web",
        "redirect_uri": ""
    },
    "implicit": {
        "base_uri": "http://localhost:5000",
        "client_id": "<client id>",
        "secret": "secret",
        "token_url": "<token url>",
        "authorize_url": "<auth url>",
        "client_kwargs": {
            "scope": "openid cactus read",
            "nonce": "gang",
            "response_type": "token",
            "state": "abc"
        },
        "authorization_kwargs": {
            "grant_type": ""
        },
        "flow_type": "implicit",
        "redirect_uri": "http://localhost:5000/callback/implicit"
    }
}


@app.route("/")
def index():
    return "Welcome to the base page"


@app.route("/login/<provider>")
def login(provider):
    auth_provider = OAuthSignIn(provider)
    registered_provider = auth_provider.register(app)
    provider_session = auth_provider.provider_session()
    return auth_provider.authorize(registered_provider, provider_session)


@app.route("/callback/<provider>", methods=["GET", "POST"])
def callback(provider):
    auth_provider = OAuthSignIn(provider)
    registered_provider = auth_provider.register(app)
    return auth_provider.authenticate(registered_provider, "templates/implicit.html")


@app.route("/implicit/<provider>")
def implicit(provider):
    auth_provider = OAuthSignIn(provider)
    token = auth_provider.authenticate_implict_helper()
    session[f'{provider}_token'] = token
    return redirect(url_for("home", provider=provider))


@app.route("/home/<provider>", methods=["GET"])
def home(provider):
    return f"You made it."


if __name__ == "__main__":
    app.run(debug=True)
