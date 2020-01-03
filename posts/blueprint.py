from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash
)
from models import Post, Tag, Knot
import locale
from forms import PostForm
from app import db
import re


locale.setlocale(locale.LC_ALL, "")

posts = Blueprint('posts',
    __name__,
    template_folder='templates'
)
about = Blueprint('about',
    __name__,
    template_folder='templates'
)


### Create post page ###

'''Page with form for write Title Body and Tag. 
   Than its information put in class Post and add in db.'''  

@posts.route('/create', methods=['POST', 'GET'])
def create_post():

    form = PostForm(request.form)

    if 'username' in session:
        if request.method == 'POST' and form.validate_on_submit():
            try:
                post = Post(title=form.title.data, body=form.body.data)
                tag_list = re.split(r'[\s, .]', form.tags.data)
                for i in tag_list:
                    if Tag.query.filter_by(name=i).first():
                        tag = Tag.query.filter_by(name=i).first()
                    else:
                        tag = Tag(name=i)
                    post.tags.append(tag)
                post.author = session['username']
                db.session.add(post)
                db.session.commit()
                flash('Post create')
            except:
                print('Something wrong')
            return redirect( url_for('posts.index') )
        elif not form.validate_on_submit():
            print('validate: ', form.validate_on_submit())

    else:
        return redirect('/log_in')

    return render_template('posts/create_post.html', form=form)


@posts.route('/<slug>/edit/', methods=['POST', 'GET'])
def edit_post(slug):
    post = Post.query.filter(Post.slug==slug).first()
    form = PostForm(request.form)

    if request.method == 'POST' and session['username'] == post.author and form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        t = re.split(r'[\s\[\], .]', form.tags.data)

        for i in t:
            if Tag.query.filter_by(name=i).first():
                tag = Tag.query.filter_by(name=i).first()
            else:
                tag = Tag(name=i)
            post.tags.append(tag)

        db.session.commit()
        flash('Post save')
        return redirect(url_for('posts.post_content',
            slug=post.slug)
        )
    elif not session:
        return redirect(url_for('login.log_in'))

    form = PostForm(
        title=post.title,
        body=post.body,
        tags=', '.join(list(str(i) for i in post.tags.__iter__()))
        )

    return render_template('posts/edit_post.html',
        post=post,
        form=form,
    )


@posts.route('/', methods=['GET'])
def index():

    q = request.args.get('q') # search value from form

    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    if q:
        posts = Post.query.filter(
            Post.title.contains(q) | # поиск по заголовку
            Post.body.contains(q) |  # поиск по тексту
            Post.tags.any(name=q)    # поиск по тегам
        )
    else:
        posts = Post.query.order_by(db.desc(Post.created)) # сортировка от последнего до первого

    pages = posts.paginate(page=page, per_page=5)
    
    return render_template('posts/index.html',
        posts=posts,
        pages=pages
    )


@posts.route('/<slug>')
def post_content(slug):
    post = Post.query.filter(Post.slug==slug).first()
    tags = post.tags
    time = post.created.strftime("%d %B %Y (%A) %H:%M")
    author = post.author
    return render_template('posts/post_content.html',
        post=post,
        tags=tags,
        time=time,
        author=author
    )


@about.route('/')
def contacts():
    print(f'session: {session}')
    if not session.get('username'):
        return redirect('/log_in')
    user = Knot.query.filter_by(username=session['username']).first()
    return render_template('posts/about.html',
        first_name=user.f_name,
        second_name=user.s_name,
        username=user.username,
        number=user.number,
    )


@posts.route('/tag/<slug>')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug == slug).first()
    posts = tag.posts

    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    pages = posts.paginate(page=page, per_page=5)

    return render_template('posts/tag_detail.html',
        tag=tag,
        posts=posts,
        pages=pages
    )
