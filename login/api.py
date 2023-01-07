
import jwt
from datetime import datetime
from datetime import timezone

from flask import jsonify, request, render_template
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError

from app import app, db#, csrf
from models import Knot, TokenBlackList
from exceptions import (
    UnauthorizedError,
    EmailValidationError,
    NotFoundError,
    DublicatedPassword,
    PasswordResetKeyExprired,
    DBError
)
from utils import encrypt_string
from utils import args_to_parser
from utils import fromisoformat
from .forms import email_validation
from .send_email import send_email


validator = {
    'auth_get': {
        'process': dict(type=str, required=False, help='This field cannot be blank.'),
        'email': dict(type=str, required=False, help='This field cannot be blank.'),
    }
}

# RESOURCES
class AuthApi(Resource):

    def get(self):
        parser = args_to_parser(validator, 'auth_get', 'args')
        data = parser.parse_args()

        try:
            if data.get('process') == 'check_email':
                email = data.get('email', None)
                email_validation(email)
                user = Knot.query.filter(Knot.email==email).first()
                if not user:
                    raise NotFoundError
                else:
                    data = {'user': user.id, 'created_at': datetime.utcnow().isoformat()}
                    reset_password_key = jwt.encode(data, app.config['JWT_SECRET_KEY'])
                    url = f'{request.url_root}reset_password?reset_key={reset_password_key}'
                    subject = "Reset password"
                    content = lambda: render_template('emails/reset_password.html', url=url, name=user.f_name)
                    send_email(user.email, subject, content)
                    return jsonify(status=200)
        except ValidationError:
            raise EmailValidationError

    def post(self):
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username:
            # RESET PASSWORD
            reset_key = request.cookies['reset_key']
            data = jwt.decode(reset_key, options={"verify_signature": False})
            date = fromisoformat(data['created_at'])
            user = Knot.query.get(data['user'])
            new_password = encrypt_string(password)
            if not user:
                raise NotFoundError
            elif user.password == new_password:
                raise DublicatedPassword
            elif user.updated > date or (datetime.utcnow() - date).seconds / 60 > 30:
                raise PasswordResetKeyExprired
            else:
                user.password = new_password
                db.session.commit()
            return jsonify(status=200)

        user = Knot.query.filter(Knot.username==username).first()

        if user and encrypt_string(password) == user.password:
            created_at = datetime.now()
            data = {'user': user.id, 'created_at': created_at.isoformat()}
            expired_at = datetime.now(timezone.utc).timestamp() + app.config['JWT_ACCESS_TOKEN_EXPIRES'].seconds
            data = dict(
                username=user.username,
                user_icon=user.avatar(size=50),
                access_token_cookie=create_access_token(identity=data),
                refresh_token_cookie=create_refresh_token(identity=data),
                expired_at=int(expired_at))
            return data, 200

        raise UnauthorizedError

    def delete(self):
        access_token = request.cookies['access_token_cookie']
        try:
            used_token = TokenBlackList(access_token=access_token)
            db.session.add(used_token)
            db.session.commit()
        except Exception as e:
            raise DBError 
        return


    # def put(self):
    #     validate_csrf(request.headers.get('X-CSRFToken'))

    #     data = request.json