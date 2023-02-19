from app import db, ma
from models import Chat, Message
from marshmallow import fields
from flask_jwt_extended import current_user
from user_profile.schemas import user_schema

class MessageSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Message
        load_instance = True
        sqla_session = db.session

    text = ma.auto_field()
    uuid = ma.auto_field(dump_only=True)
    created = ma.auto_field(dump_only=True)
    edited = ma.auto_field(dump_only=True)
    is_read = ma.auto_field()
    author_username = ma.auto_field(dump_only=True)
    side = fields.Function(lambda message, ctx: 'left' if message.author != ctx.get('user', current_user) else 'right')


msg_schema = MessageSchema()
msgs_schema = MessageSchema(many=True)


class ChatSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Chat

    created = ma.auto_field(dump_only=True)
    edited = ma.auto_field(dump_only=True)

    # messages = fields.Nested(MessageSchema)

    uuid = fields.Method("get_receiver_uuid", dump_only=True)
    last_msg = fields.Method("last_chat_message", dump_only=True)
    left_user = fields.Method("get_left_user", dump_only=True)
    right_user = fields.Method("get_right_user", dump_only=True)
    unread_msgs = fields.Method("get_unread_msgs", dump_only=True)

    def get_receiver_uuid(self, chat):
        users = [user for user in chat.users if user != current_user]
        return str(users[-1].uuid) if len(users) else None

    def get_left_user(self, chat):
        users = [user for user in chat.users if user != current_user]
        return user_schema.dump(users[-1]) if len(users) else None

    def get_right_user(self, chat):
        users = [user for user in chat.users if user == current_user]
        return user_schema.dump(users[-1]) if len(users) else None

    def last_chat_message(self, chat):
        data = msgs_schema.dump(chat.messages)
        return data[-1] if len(data) else []

    def get_unread_msgs(self, chat):
        return len([msg for msg in chat.messages if msg.author != current_user and not msg.is_read ])

chat_schema = ChatSchema()
chats_schema = ChatSchema(many=True)
