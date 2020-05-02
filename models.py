from app import db
from datetime import datetime
import re
from login.hash import encrypt_string


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


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(140), unique=True)
    slug = db.Column(db.String(140), unique=True)
    title = db.Column(db.String(78))
    preview = db.Column(db.String(250))
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.now())
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

    # def __repr__(self):
    #     return f'''
    #         Post id: {self.id},
    #         Post uuid: {self.uuid},
    #         title: {self.title},
    #         slug: {self.slug}
    #     ''' 
    
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
    number = db.Column(db.String(15))  # phone number
    password = db.Column(db.String(256))

    slug = db.Column(db.String(140), unique=True)
    
    created = db.Column(db.DateTime, default=datetime.now())
    last_login = db.Column(db.DateTime, default=datetime.now())

    authenticated = db.Column(db.Boolean, default=0)
    auth_key = db.Column(db.String(256))
    auth_key_create = db.Column(db.DateTime, default=created)
    admin = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kwargs):
        super(Knot, self).__init__(*args, **kwargs)
        self.slug = slugify(self.username)
        self.get_auth_key()
    
    def get_auth_key(self):
        self.auth_key = encrypt_string(self.username + str(datetime.now()))
        if self.auth_key_create is None:
            self.auth_key_create = datetime.now()
        return (self.auth_key, self.auth_key_create)

    def check_auth_key(self):
        delta = datetime.now() - self.auth_key_create
        return True if delta.seconds < 3600 else False

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
    edited = db.Column(db.DateTime, default=datetime.now())
    owner_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
        self.created = datetime.now()
        self.generate_uuid()
        self.generate_slug()

    def generate_uuid(self):
        self.uuid = comment_uuid()

    def generate_slug(self):
        if self.text:
            self.slug = f'comment_{self.uuid}'

    # def __repr__(self):
    #     return f'''
    #         Comment id: {self.id}
    #         Comment uuid: {self.uuid},
    #         text: {self.text},
    #         slug: {self.slug}.
    #         author: {self.author},
    #         created: {self.created}
    #     ''' 
