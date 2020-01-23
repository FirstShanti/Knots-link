from app import db
from datetime import datetime
import re


def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)

def post_uuid():
    try: ### if post exist ###
        Post.query.order_by(db.desc(Post.created)).first().id
    except AttributeError:
        return '1'
    return str(Post.query.order_by(db.desc(Post.created)).first().id + 1)

def comment_uuid():
    try:
        Comment.query.order_by(db.desc(Comment.created)).first().id
    except AttributeError:
        return '1'
    return str(Comment.query.order_by(db.desc(Comment.created)).first().id + 1)

### TAGS FOR POST ###
post_tags = db.Table(
    'post_tags', 
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(140), unique=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.now())
    author = db.Column(db.String(32))
    

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_uuid()
        self.generate_slug()
        

    # tags and comments to post
    tags = db.relationship('Tag', passive_deletes=True, secondary=post_tags)
    comments = db.relationship('Comment', backref='owner')

    def generate_uuid(self):
        self.uuid = post_uuid()

    def generate_slug(self):
        if self.title:
            self.slug = f'post{self.uuid}_{slugify(self.title)}'

    def __repr__(self):
        return f'''
            Post id: {self.id},
            title: {self.title},
            slug: {self.slug}
        ''' 
        
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

    def __repr__(self):
        return self.name

# class Knot - (class of user)
class Knot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(32))
    s_name = db.Column(db.String(32))
    username = db.Column(db.String(32))
    slug = db.Column(db.String(140), unique=True)
    number = db.Column(db.String(15))  # phone number
    password = db.Column(db.String(256))
    created = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, *args, **kwargs):
        super(Knot, self).__init__(*args, **kwargs)
        self.slug = slugify(self.username)

    def __repr__(self):
        return f'''
            Knot id: {self.id},
            username: {self.username},
            posts: {self.posts},
            slug: {self.slug}
        ''' 

# class Comment - (class of cpmments for Post)
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

    def __repr__(self):
        return f'''
            Comment id: {self.id}
            Comment uuid: {self.uuid},
            text: {self.text},
            slug: {self.slug}.
            author: {self.author},
            created: {self.created}
        ''' 


