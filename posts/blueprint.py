from flask import Blueprint, render_template
from models import Post, Tag

posts = Blueprint('posts', __name__, template_folder='templates')
about = Blueprint('about', __name__, template_folder='templates')

@posts.route('/')
def index():
    posts = Post.query.all()
    return render_template('posts/index.html', posts=posts)

# http://localhost/blog/first_post
@posts.route('/<slug>')
def post_content(slug):
    post = Post.query.filter(Post.slug==slug).first()
    tags = post.tags
    return render_template('posts/post_content.html', post=post, tags=tags)


@about.route('/')
def contacts():
    return render_template('posts/about.html', post=about)


@posts.route('/tag/<slug>')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug == slug).first()
    posts = tag.posts.all()
    return render_template('posts/tag_detail.html', tag=tag, posts=posts)


