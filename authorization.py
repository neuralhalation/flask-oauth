from authlib.client import OAuth2Session
from authlib.flask.client import OAuth
from flask import current_app, redirect, render_template, request, session, url_for


class OAuthSignIn(object):
    """Base auth class.
    """

    def __init__(self, provider_name):
        self.name = provider_name
        credentials = current_app.config["OAUTH_CREDENTIALS"][provider_name]
        self.api_base_url = credentials["base_uri"]
        self.client_id = credentials["client_id"]
        self.client_secret = credentials["secret"]
        self.access_token_url = credentials["token_url"]
        self.authorize_url = credentials["authorize_url"]
        self.client_kwargs = credentials["client_kwargs"]
        self.authorization_kwargs = credentials["authorization_kwargs"]
        self.flow_type = credentials["flow_type"]
        self.redirect_uri = credentials["redirect_uri"]

    def fetch_token_from_session(self):
        return session.get(f"{self.name}_token")

    def register(self, app):
        oauth = OAuth(app)
        oauth.register(
            name=self.name,
            client_id=self.client_id,
            client_secret=self.client_secret,
            access_token_url=self.access_token_url,
            authorize_url=self.authorize_url,
            client_kwargs=self.client_kwargs,
            fetch_token=self.fetch_token_from_session,
        )
        return oauth

    def provider_session(self):
        return OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.client_kwargs["scope"],
        )

    def authorize(self, registered_provider=None, provider_session=None):
        """Login
        """
        if self.flow_type == "web" and registered_provider is not None:
            redirect_uri = url_for("callback", provider=self.name, _external=True)
            return eval(
                f"registered_provider.{self.name}"
                f".authorize_redirect('{redirect_uri}')"
            )
        if self.flow_type == "client" and provider_session is not None:
            return provider_session.fetch_access_token(
                self.access_token_url, self.authorization_kwargs
            )
            return redirect(url_for("home"))
        if self.flow_type == "implicit" and provider_session is not None:
            uri, state = provider_session.create_authorization_url(
                client_id=self.client_id,
                scope=self.client_kwargs["scope"],
                redirect_uri=self.redirect_uri,
            )
            return redirect(uri)

    def authenticate_from_server(self, registered_provider):
        return eval(f"registered_provider.{self.name}.authorize_access_token()")

    def authenticate_implicit(self, template_path):
        return render_template(template_path)

    def authenticate(self, registered_provider=None, template_path=None):
        if self.flow_type == "web" and registered_provider is not None:
            response = self.authenticate_from_server(registered_provider)
            if response is None or response.get("access_token") is None:
                return (
                    f"Access Denied: Reason={request.args['error']} "
                    f"error={request.args['error_description']} "
                    f"response={response}"
                )
            session["token"] = response
            return redirect(url_for("home", provider=self.name))
        elif self.flow_type == "implicit" and template_path is not None:
            return self.authenticate_implicit(template_path)
        elif self.flow_type == "client":
            return redirect(url_for("home", provider=self.name))
        else:
            raise Exception(
                "Invalid flow type, registered_provider is None, "
                "or template_path not specified"
            )

    def authenticate_implicit_helper(self):
        token = request.args.get("response")
        token_pieces = [i for i in token.split("&")]
        token_dict = {}
        for t in token_pieces:
            split_value = t.split("=")
            token_dict[split_value[0]] = split_value[1]
        return token_dict
