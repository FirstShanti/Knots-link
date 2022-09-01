from app import db
from datetime import datetime
import re
from login.hash import encrypt_string
from uuid import uuid4
from config import local, lang


def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)


def post_uuid():
    try: ### if post exist ###
        Post.query.order_by(db.desc(Post.id)).first().id
    except AttributeError:
        return '1'
    return str(Post.query.order_by(db.desc(Post.id)).first().id + 1)


def comment_uuid():
    try:
        Comment.query.order_by(db.desc(Comment.id)).first().id
    except AttributeError:
        return '1'
    return str(Comment.query.order_by(db.desc(Comment.id)).first().id + 1)


### TAGS FOR POST ###
post_tags = db.Table(
    'post_tags', 
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

chat_users = db.Table(
    'chat_users', 
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.uuid'), primary_key=True),
    db.Column('knot_id', db.Integer, db.ForeignKey('knot.id'), primary_key=True)
)

chat_msgs = db.Table(
    'chat_msgs',
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.uuid'), primary_key=True),
    db.Column('message_id', db.Integer, db.ForeignKey('message.id'), primary_key=True)
    )

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(140), unique=True)
    slug = db.Column(db.String(140), unique=True)
    title = db.Column(db.String(78))
    preview = db.Column(db.String(250))
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    author = db.Column(db.String(32))
    visible = db.Column(db.Boolean, default=1)
    owner_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_uuid()
        self.generate_slug()
        
    def invisible(self):
        self.visible = False

    def generate_uuid(self):
        self.uuid = post_uuid()

    def generate_slug(self):
        if self.title:
            self.slug = f'post{self.uuid}_{slugify(self.title)}'

    def created_to_str(self, formatter=None):
        timedelta = int(datetime.utcnow().strftime("%d")) - int(self.created.strftime("%d"))
        if timedelta > 1:
            return self.created.strftime("%d %B %y {} %H:%M".format(f'{lang[local]["comment"][2]}'))
        elif timedelta == 1:
            return self.created.strftime("{}%H:%M").format(f'{lang[local]["comment"][0]}')
        elif timedelta >= 0:
            return self.created.strftime("{}%H:%M").format(f'{lang[local]["comment"][1]}')
    
    # tags and comments to post
    tags = db.relationship('Tag', passive_deletes=True, secondary=post_tags)
    comments = db.relationship('Comment', backref='owner')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(46), unique=True)
    short_name = db.Column(db.String(46), unique=True)
    slug = db.Column(db.String(100), unique=True)
    
    posts = db.relationship('Post', backref='owner')

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
        self.slug = slugify(self.name)


# class Tag (class of tag for Post)
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(46), unique=True)
    slug = db.Column(db.String(100), unique=True)

    posts = db.relationship(
        'Post',
        passive_deletes=True,
        secondary=post_tags
    )

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.slug = slugify(self.name)

    # def __repr__(self):
    #     return self.name


# class Knot - (class of user)
class Knot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(32))
    s_name = db.Column(db.String(32))
    username = db.Column(db.String(32))
    email = db.Column(db.String(129), unique=True)
    phone_number = db.Column(db.String(15))  # phone number
    password = db.Column(db.String(256))

    slug = db.Column(db.String(140), unique=True)
    
    created = db.Column(db.DateTime, default=datetime.utcnow())
    last_login = db.Column(db.DateTime, default=datetime.utcnow())

    authenticated = db.Column(db.Boolean, default=0)
    auth_key = db.Column(db.String(256))
    auth_key_create = db.Column(db.DateTime, default=created)
    admin = db.Column(db.Boolean, default=0)

    messages = db.relationship('Message', backref='author')
    chats = db.relationship('Chat', passive_deletes=True, secondary=chat_users)

    def __init__(self, *args, **kwargs):
        super(Knot, self).__init__(*args, **kwargs)
        self.slug = slugify(self.username)
        self.password = encrypt_string(self.password)
        self.get_auth_key()
    
    def get_auth_key(self):
        self.auth_key = encrypt_string(self.username + str(datetime.utcnow()))
        if self.auth_key_create is None:
            self.auth_key_create = datetime.utcnow()
        return (self.auth_key, self.auth_key_create)

    def check_auth_key(self):
        delta = datetime.utcnow() - self.auth_key_create
        return True if delta.seconds < 3600 else False

    def avatar(self, size):
        return f'https://www.gravatar.com/avatar/{self.auth_key}?d=identicon&s={size}'

    def __repr__(self):
        return f'''
            Knot id: {self.id},
            username: {self.username},
            slug: {self.slug}
        ''' 
            #posts: {self.posts},

# class Comment - (class of comments for Post)
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(140))
    text = db.Column(db.String(2000))
    slug = db.Column(db.String(140), unique=True)
    author = db.Column(db.String(32))
    created = db.Column(db.DateTime)
    edited = db.Column(db.DateTime, default=datetime.utcnow())
    owner_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self.created = datetime.utcnow()
        self.generate_uuid()
        self.generate_slug()

    def generate_uuid(self):
        self.uuid = comment_uuid()

    def generate_slug(self):
        if self.text:
            self.slug = f'comment_{self.uuid}'

    def created_to_str(self):
        timedelta = int(datetime.utcnow().strftime("%d")) - int(self.created.strftime("%d"))
        if timedelta >= 1:
            return self.created.strftime("%d %B %Y (%A) %H:%M")
        elif timedelta == 1:
            return self.created.strftime("{}%H:%M").format(f'{lang[local]["comment"][0]}')
        elif timedelta >= 0:
            return self.created.strftime("{}%H:%M").format(f'{lang[local]["comment"][1]}')


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(140), unique=True)
    created = db.Column(db.DateTime)


    def __init__(self, *args, **kwargs):
        super(Chat, self).__init__(*args, **kwargs)
        self.created = datetime.utcnow()
        self.uuid = str(uuid4())


    users = db.relationship('Knot', passive_deletes=True, secondary=chat_users)
    messages = db.relationship('Message', passive_deletes=True, secondary=chat_msgs)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(140), unique=True)
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
        self.uuid = str(uuid4())

    def data(self):
        return {
            'text': self.text,
            'created': self.created.timestamp(),
            'author_username': self.author_username,
            'is_read': self.is_read
        }