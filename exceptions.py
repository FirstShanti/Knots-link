class ApiException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class InternalServerError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class EmailValidationError(Exception):
    pass


class NotFoundError(Exception):
    pass


class DublicatedPassword(Exception):
    pass


class PasswordResetKeyExprired(Exception):
    pass 


class DBError(Exception):
    pass 


errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
    "UnauthorizedError": {
        "message": "Invalid username or password",
        "status": 401
    },
    "EmailValidationError": {
        "message": "Invalid email",
        "status": 400
    },
    "NotFoundError": {
        "message": "Not found",
        "status": 404
    },
    "DublicatedPassword": {
        "message": "Please choose another password",
        "status": 400
    },
    "PasswordResetKeyExprired": {
        "message": "The time to reset your password has expired",
        "status": 403
    },
    "DBError": {
        "message": "Error while saving token to black list",
        "status": 500
    }
}
