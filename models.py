from app import db
from datetime import datetime
import re


def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)


post_tags = db.Table(
    'post_tags', 
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

'''post_knot = db.Table('post_knot',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('knot_id', db.Integer, db.ForeignKey('knot.id'))
)'''


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.now())
    author = db.Column(db.String(32))

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_slug()

    # теги прикрепленные к посту и юзер написавший пост
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))
    #knot = db.relationship('Knot', secondary=post_knot, backref=db.backref('posts', lazy='dynamic'))


    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)


    def __repr__(self):
        return f'Post id: {self.id}, title: {self.title}, slug: {self.slug}' 
        

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(46), unique=True)
    slug = db.Column(db.String(100), unique=True)

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
    number = db.Column(db.String(15))  # phone number
    password = db.Column(db.String(256))

    def __init__(self, *args, **kwargs):
        super(Knot, self).__init__(*args, **kwargs)

    # посты созданные юзером
    #posts = db.relationship('Post', secondary=post_knot, backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return f'Knot id: {self.id}, username: {self.username}, posts: {self.posts}' 