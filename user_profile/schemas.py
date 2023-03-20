from app import ma
from models import Knot
from marshmallow import fields

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Knot

    username = ma.auto_field()
    avatar = fields.Method("get_avatar", dump_only=True)

    def get_avatar(self, user):
        return user.avatar(size=75)

user_schema = UserSchema()
users_schema = UserSchema(many=True)