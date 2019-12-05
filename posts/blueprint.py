from flask import Blueprint, render_template, request, redirect, url_for
from models import Post, Tag
import locale
from .forms import PostForm
from app import db
import re

locale.setlocale(locale.LC_ALL, "")

posts = Blueprint('posts', __name__, template_folder='templates')
about = Blueprint('about', __name__, template_folder='templates')


@posts.route('/create', methods=['POST', 'GET'])
def create_post():

	form = PostForm()

	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		t = re.split(r'[\s, .]', request.form['name'])

		try:
			if title and body and t:
				post = Post(title=title, body=body)
				for i in t:
					if Tag.query.filter_by(name=i).first():
						tag = Tag.query.filter_by(name=i).first()
					else:
						tag = Tag(name=i)
					post.tags.append(tag)	
				db.session.add(post)
				db.session.commit()
		except:
			print('Something wrong')

		return redirect( url_for('posts.index') )

	
	return render_template('posts/create_post.html', form=form)


@posts.route('/')
def index():

	q = request.args.get('q')

	if q:
		posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q)).all()
	else:
		posts = Post.query.all()[-1::-1]
	
	return render_template('posts/index.html', posts=posts)


@posts.route('/<slug>')
def post_content(slug):
    post = Post.query.filter(Post.slug==slug).first()
    tags = post.tags
    time = post.created.strftime("%d %B %Y (%A) %I:%M")
    return render_template('posts/post_content.html', post=post, tags=tags, time=time)


@about.route('/')
def contacts():
    return render_template('posts/about.html', post=about)


@posts.route('/tag/<slug>')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug == slug).first()
    posts = tag.posts.all()
    return render_template('posts/tag_detail.html', tag=tag, posts=posts)


