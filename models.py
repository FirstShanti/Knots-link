import hashlib

from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app import db

from utils import encrypt_string
from config import local, lang


### TAGS FOR POST ###
post_tags = db.Table(
    'post_tags', 
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

chat_users = db.Table(
    'chat_users', 
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), primary_key=True),
    db.Column('knot_id', db.Integer, db.ForeignKey('knot.id'), primary_key=True)
)

chat_msgs = db.Table(
    'chat_msgs',
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), primary_key=True),
    db.Column('message_id', db.Integer, db.ForeignKey('message.id'), primary_key=True),
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(78))
    preview = db.Column(db.String(250))
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    author = db.Column(db.String(32))
    visible = db.Column(db.Boolean, default=1)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        
    def invisible(self):
        self.visible = False

    def created_to_str(self, formatter=None):
        timedelta = abs(datetime.utcnow().day - self.created.day)
        if timedelta > 1:
            return self.created.strftime("%d %B %y / %H:%M")
        elif timedelta == 1:
            return self.created.strftime("{}%H:%M").format(f'{lang[local]["comment"][0]}')
        elif timedelta >= 0:
            return self.created.strftime("{}%H:%M").format(f'{lang[local]["comment"][1]}')
    
    # tags and comments to post
    tags = db.relationship(
        'Tag',
        passive_deletes=True,
        secondary=post_tags
    )
    comments = db.relationship('Comment', backref='owner')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(46), unique=True)
    short_name = db.Column(db.String(46), unique=True)
    
    posts = db.relationship('Post', backref='category')

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)


# class Tag (class of tag for Post)
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(46), unique=True)

    posts = db.relationship(
        'Post',
        passive_deletes=True,
        secondary=post_tags,
        overlaps="tags"
    )

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)


# class Knot - (class of user)
class Knot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, nullable=False, unique=True)
    f_name = db.Column(db.String(32))
    s_name = db.Column(db.String(32))
    username = db.Column(db.String(32), unique=True)
    email = db.Column(db.String(129), unique=True)
    phone_number = db.Column(db.String(15))  # phone number
    password = db.Column(db.String(256))
    
    created = db.Column(db.DateTime, default=datetime.utcnow())
    updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    last_login = db.Column(db.DateTime, default=datetime.utcnow())

    authenticated = db.Column(db.Boolean, default=0)
    auth_key = db.Column(db.String(256))
    auth_key_create = db.Column(db.DateTime, default=created)
    admin = db.Column(db.Boolean, default=0)

    messages = db.relationship('Message', backref='author')
    chats = db.relationship('Chat', passive_deletes=True, secondary=chat_users)

    comments = db.relationship('Comment', backref='author')

    def __init__(self, *args, **kwargs):
        super(Knot, self).__init__(*args, **kwargs)
        self.password = encrypt_string(self.password)
        self.get_auth_key()
    
    def get_auth_key(self):
        self.auth_key = encrypt_string(self.username + str(datetime.utcnow()))
        self.auth_key_create = datetime.utcnow()
        return (self.auth_key, self.auth_key_create)

    def check_auth_key(self):
        delta = datetime.utcnow() - self.auth_key_create
        return True if delta.seconds < 3600 else False

    def avatar(self, size=50):
        hash_key = hashlib.sha256(self.email.lower().encode()).hexdigest()
        return f'https://www.gravatar.com/avatar/{hash_key}?d=identicon&s={size}'

    @property
    def chat_ids(self):
        return [chat.uuid for chat in self.chats]

    def __repr__(self):
        return str(self.uuid)

# class Comment - (class of comments for Post)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000))
    created = db.Column(db.DateTime)
    edited = db.Column(db.DateTime, default=datetime.utcnow())
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('knot.id'))

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self.created = datetime.utcnow()

    def created_to_str(self):
        timedelta = abs(int(datetime.utcnow().strftime("%d")) - int(self.created.strftime("%d")))
        if timedelta >= 1:
            return self.created.strftime("%d %B %Y (%A) %H:%M")
        elif timedelta == 1:
            return self.created.strftime("{}%H:%M").format(f'{lang[local]["comment"][0]}')
        elif timedelta >= 0:
            return self.created.strftime("{}%H:%M").format(f'{lang[local]["comment"][1]}')


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(140), unique=True, default=str(uuid4()))
    created = db.Column(db.DateTime, default=datetime.utcnow())
    edited = db.Column(db.DateTime, default=datetime.utcnow())


    def __init__(self, *args, **kwargs):
        super(Chat, self).__init__(*args, **kwargs)
        self.check_uuid_unique()

    def check_uuid_unique(self):
        dupliate = Chat.query.filter(Chat.uuid==self.uuid).first()
        if dupliate:
            while self.uuid == dupliate.uuid:
                self.uuid = str(uuid4())

    users = db.relationship('Knot', passive_deletes=True, secondary=chat_users, overlaps="chats")
    messages = db.relationship('Message', passive_deletes=True, secondary=chat_msgs)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid4, nullable=False)
    text = db.Column(db.String(5000), nullable=False)

    created = db.Column(db.DateTime)
    edited = db.Column(db.DateTime, default=datetime.utcnow())
    is_read = db.Column(db.Boolean, default=False)
    # author = db.Column(db.Integer, db.ForeignKey('knot.username'))
    author_username = db.Column(db.String(32), db.ForeignKey('knot.username'))
    # owner_id = db.Column(db.String, db.ForeignKey('chat.id'))

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.created = datetime.utcnow()

    @property
    def chat(self):
        if (chat:= Chat.query.filter(Chat.messages.contains(self)).first()):
            return chat


class TokenBlackList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(512), nullable=True)


### Utils
def get_user(username=None, user_id=None, uuid=None):
    if username:
        return Knot.query.filter_by(username=username).first()
    elif user_id:
        return Knot.query.filter_by(id=user_id).first()
    elif uuid:
        return Knot.query.filter_by(uuid=uuid).first()
    else:
        return None


def get_chat(current_user=None, another_user=None, chat_id=None, all_chats=False):
    if chat_id:
        return Chat.query.filter(Chat.uuid==chat_id).first()
    elif current_user and another_user:
        return Chat.query.filter(Chat.users.contains(current_user)).filter(Chat.users.contains(another_user)).first()
    elif current_user:
        return Chat.query.filter(Chat.users.contains(current_user)).first()
    elif another_user:
        return Chat.query.filter(Chat.users.contains(another_user)).first()
    else:
        return None

def get_all_chat(user):
    return Chat.query.filter(Chat.users.contains(user)).all()


def get_message(chat=None, chat_id=None, msg_ig=None, username=None):
    if not chat and chat_id:
        chat = Chat.query.filter(Chat.uuid==chat_id).first()
    query = Message.query.filter(Message.id.in_([msg.id for msg in chat.messages])).order_by(desc(Message.created))
    return query
