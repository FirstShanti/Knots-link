from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash
)
from models import (
    Post,
    Tag,
    Knot,
    Comment,
    slugify
)
from sqlalchemy.exc import IntegrityError
import locale
from forms import PostForm, CommentForm
from app import db
import re
from datetime import datetime, timedelta


locale.setlocale(locale.LC_ALL, "")
local = locale.getdefaultlocale()[0]
lang = {'ru_RU':{'comment':['вчера в ', 'сегодня в ']},
        'en_US':{'comment':['yesterday at ', 'today at ']}
    }

posts = Blueprint('posts',
    __name__,
    template_folder='templates'
)
user_profile = Blueprint('user_profile',
    __name__,
    template_folder='templates'
)

### Create post ###
'''Page with form for write Title Body and Tag. 
   Than its information put in class Post and add in db.''' 

@posts.route('/create', methods=['POST', 'GET'])
def create_post():

    form = PostForm(request.form)
    
    if 'username' in session:
        if request.method == 'POST' and form.validate_on_submit():
            try:
                post = Post(
                    title=form.title.data,
                    preview = form.preview.data,
                    body=form.body.data,
                    author = session['username']
                )
                tag_list = re.sub(r'[\s, .]', ' ', form.tags.data).split()
                for i in set(tag_list):
                    if Tag.query.filter_by(name=i).first():
                        tag = Tag.query.filter_by(name=i).first()
                    else:
                        tag = Tag(name=i)
                    post.tags.append(tag)
                post.author = session['username']
                if request.form['submit'] == 'draft':
                    post.visible = False
                db.session.add(post)
                db.session.commit()
                flash('Post create')
            except Exception as e:
                print(f'Something wrong\n{e.__class__}')
                raise e
            return redirect(url_for('posts.index'))
        elif not form.validate_on_submit():
            print('validate: ', form.validate_on_submit())
    else:
        return redirect('/log_in')

    return render_template('create_post.html', form=form)


@posts.route('/<slug>/edit/', methods=['POST', 'GET'])
def edit_post(slug):
    post = Post.query.filter(Post.slug==slug).filter(Post.author==session.get('username')).first()
    form = PostForm(
        title=post.title,
        body=post.body,
        preview = post.preview,
        # реализовать удаление тегов
        tags=', '.join(list(str(i) for i in post.tags.__iter__()))  
    )

    try:
        if request.form['submit'] == 'cancel':
            return redirect(url_for('posts.index'))
    except KeyError:
        pass
    if request.method == 'POST' and session['username'] == post.author and form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.preview = form.preview.data
        tag_list = re.sub(r'[\s, .]', ' ', form.tags.data).split()
        post.tags.clear()
        db.session.commit()      
        for i in set(tag_list):
            if Tag.query.filter_by(name=i).first():
                tag = Tag.query.filter_by(name=i).first()
            else:
                tag = Tag(name=i)
            post.tags.append(tag)
        try:
            if request.form['submit'] == 'publish':
                post.visible = True
            db.session.commit()
            print('Post save')
        except:
            print('not save')
        return redirect(url_for('posts.post_content', slug=post.slug))
    elif not session:
        return redirect(url_for('login.log_in'))

    return render_template('edit_post.html',
        post=post,
        form=form,
    )

@posts.route('/<slug>/delete/', methods=['POST', 'GET'])
def delete_post(slug):
    post = Post.query.filter(Post.slug==slug).filter(Post.visible==True).first()
    post_title = post.title

    if 'username' in session and session.get('username') == post.author:
        try:
            post.invisible()
            db.session.commit()
        except Exception as e:
            print(f'Something wrong\n{e.__class__}')
    return redirect('/blog/')


@posts.route('/', methods=['GET'])
def index():
    print(f"user: {session.get('username')}")
    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    # сортировка видимых от последнего до первого 
    posts = Post.query.order_by(db.desc(Post.created)).filter(Post.visible==True)

    for post in posts:
        post.body = re.sub(r'\\r|\\n|\\t|<ul>|<li>|</ul>|</li>|<table|<tr|<td|</table|</td|</tr', '', ''.join(i for i in post.body.split("\n")[:3]))

    pages = posts.paginate(page=page, per_page=6, max_per_page=6)

    return render_template('index_posts.html',
        posts=posts,
        pages=pages,
        title="Blog"
    )


@posts.route('/<slug>', methods=['POST', 'GET'])
def post_content(slug):

    try:
        post = Post.query.filter(Post.slug==slug).filter(Post.visible==True).first() or \
            Post.query.filter(Post.slug==slug).filter(Post.author==session.get('username')).first()
        tags = post.tags
        time = post.created.strftime('%H:%M (%d %B %Y)')
        author = post.author
        user = Knot.query.filter(Knot.username==author).first()
        comments = post.comments
    except AttributeError:
        return redirect('/blog/')

    form = CommentForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        if 'username' in session:
            try:
                comment = Comment(
                    text=form.text.data,
                    author=session['username'],
                    owner=post
                )
                db.session.add(comment)
                db.session.commit()
                flash('Comment create')
            except Exception as e:
                print(f'Something wrong\n{e.__class__}')
                raise e
            return redirect(url_for('posts.post_content', slug=slug))
        else:
            return redirect(url_for('login.log_in'))

    #### change comment time format to '19 <Month> 2020 (<Week day>) 20:23' ####
    for comment in comments:
        timedelta = int(datetime.now().strftime("%d")) - int(comment.created.strftime("%d"))
        if timedelta == 1:
            comment.created = comment.created.strftime("{}%H:%M").format(f'{lang[local]["comment"][0]}')
        elif timedelta >= 0:
            comment.created = comment.created.strftime("{}%H:%M").format(f'{lang[local]["comment"][1]}')
        else:
            comment.created = comment.created.strftime("%d %B %Y (%A) %H:%M")

    return render_template('post_content.html',
        post=post,
        tags=tags,
        time=time,
        author=author,
        user=user,
        comments = comments,
        form=form,
        slug=slug,
    )


@user_profile.route('/<slug>/')
def get_user_data(slug):
    print(f'session: {session}')
    page = request.args.get('page')
    try:
        if slug == 'anonymous':
            return redirect('/log_in')
        elif 'username' in session:
            user = Knot.query.filter(Knot.slug==slug).first()
            print(f'get_user_data: {user.username}')
            posts = Post.query.filter(Post.author==user.username) #.filter(Post.visible==True)

            if page and page.isdigit():
                page = int(page)
            else:
                page = 1

        else:
            return redirect('/log_in')
    except Exception as e:
        print(f'get_user_data: \n{e}')
        return redirect(url_for('login.log_in'))

    pages = posts.paginate(page=page, per_page=6)

    return render_template('about.html',
        first_name=user.f_name,
        second_name=user.s_name,
        username=user.username,
        number=user.number,
        posts=posts,
        pages=pages
    )


@posts.route('/tag/<slug>/')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug == slug).first()
    posts = Post.query.filter(Post.tags.contains(tag)).filter(Post.visible==True)
    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    pages = posts.paginate(page=page, per_page=6)

    return render_template('index_posts.html',
        tag=tag,
        pages=pages,
        title=tag,
        content_title=f'#{tag}'
    )


@posts.route('/search/')
def search():
    q = request.args.get('q') # search value from form
    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    if q:
        posts = Post.query.filter(
            Post.title.contains(q) | # поиск по заголовку
            Post.body.contains(q) | #поиск по телу поста
            Post.tags.any(name=q.lower()) |
            Post.author.contains(q) # поиск по тегам
        ).filter(Post.visible==True)
    else:
        posts = Post.query.order_by(db.desc(Post.created))

    pages = posts.paginate(page=page, per_page=6, max_per_page=6)

    return render_template('index_posts.html',
        pages=pages,
        q=q,
        title=f'{q} results',
        content_title=f'Result for <span style="color: #718F94">{q}</span>:'
    )