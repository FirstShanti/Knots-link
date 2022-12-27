from flask.sessions import SecureCookieSessionInterface, SessionMixin


class CustomSessionInterface(SecureCookieSessionInterface):
    def should_set_cookie(self, app: "Flask", session: SessionMixin) -> bool:
        return False