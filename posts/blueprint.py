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
import locale
from forms import PostForm, CommentForm
from app import db
import re
from datetime import datetime, timedelta


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
                post = Post(
                    title=form.title.data,
                    body=form.body.data,
                    author = session['username']
                )
                tag_list = re.split(r'[\s, .]', form.tags.data)
                for i in set(tag_list):
                    if Tag.query.filter_by(name=i).first():
                        tag = Tag.query.filter_by(name=i).first()
                    else:
                        tag = Tag(name=i)
                    post.tags.append(tag)
                post.author = session['username']
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

    return render_template('posts/create_post.html', form=form)


@posts.route('/<slug>/edit/', methods=['POST', 'GET'])
def edit_post(slug):
    post = Post.query.filter(Post.slug==slug).first()
    form = PostForm(
        title=post.title,
        body=post.body,
        # реализовать удаление тегов
        tags=', '.join(list(str(i) for i in post.tags.__iter__()))  
    )

    if request.method == 'POST' and session['username'] == post.author and form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        tag_list = re.split(r'[\s\[\], .]', form.tags.data)
        print(tag_list)
        # найти все теги поста и добавить те, которые не входят в список
        post.tags.clear()
        db.session.commit()      
        for i in set(tag_list):
            if Tag.query.filter_by(name=i).first():
                tag = Tag.query.filter_by(name=i).first()
            else:
                tag = Tag(name=i)
            post.tags.append(tag)

        try:
            db.session.commit()
            flash('Post save')
        except:
            print('not save')
        return redirect(url_for('posts.post_content',
            slug=post.slug)
        )
    elif not session:
        return redirect(url_for('login.log_in'))

    

    return render_template('posts/edit_post.html',
        post=post,
        form=form,
    )


@posts.route('/', methods=['GET'])
def index():
    print(session.get('username'))
    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    posts = Post.query.order_by(db.desc(Post.created)) # сортировка от последнего до первого

    for post in posts:
        #print(post.body.split("\n")[:3])
        #post.body = ''.join(i for i in re.sub(r'\\r|\\n|\\t', '', post.body)) split("<\\p>")[:3]
        post.body = re.sub(r'\\r|\\n|\\t|<ul>|<li>|</ul>|</li>', '', ''.join(i for i in post.body.split("\n")[:3]))

        #print(post.body)
        #print(re.sub(r'\\r|\\n|\\t', '', post.body))


    pages = posts.paginate(page=page, per_page=5, max_per_page=5)
 

    return render_template('posts/index.html',
        posts=posts,
        pages=pages
    )


@posts.route('/<slug>', methods=['POST', 'GET'])
def post_content(slug):

    post = Post.query.filter(Post.slug==slug).first()
    tags = post.tags
    time = post.created.strftime("%d %B %Y (%A) %H:%M")
    author = post.author
    user = Knot.query.filter(Knot.username==author).first()
    comments = post.comments
    #body_preview = re.sub(r'\\r|\\n|\\t|<ul>|<li>|</ul>|</li>', '', post.body)

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

    #### change comment time format to '19 Январь 2020 (воскресенье) 20:23' ####
    for comment in comments:
        timedelta = int(datetime.now().strftime("%d")) - int(comment.created.strftime("%d"))
        if timedelta == 1:
            comment.created = comment.created.strftime("вчера в %H:%M")
        elif timedelta < 1:
            comment.created = comment.created.strftime("сегодня в %H:%M")
        else:
            comment.created = comment.created.strftime("%d %B %Y (%A) %H:%M")

    return render_template('posts/post_content.html',
        post=post,
        tags=tags,
        time=time,
        author=author,
        user=user,
        comments = comments,
        form=form,
        slug=slug,
    )


@about.route('/<slug>')
def contacts(slug):
    print(f'slug: {slug}')
    print(f'session: {session}')
    '''
    if not session.get('username'):
        return redirect('/log_in')
    elif slug == session['username']:
        user = Knot.query.filter(Knot.username==session['username']).first()
    else:
        if session.get('username'):
            user = Knot.query.filter(Knot.slug==slug).first()
        else:
            return redirect('/log_in')
    '''
    if slug == 'anonymous':
        return redirect('/log_in')
    elif 'username' in session:
        user = Knot.query.filter(Knot.slug==slug).first()
    else:
        return redirect('/log_in')

    return render_template('posts/about.html',
        first_name=user.f_name,
        second_name=user.s_name,
        username=user.username,
        number=user.number
    )


@posts.route('/tag/<slug>/')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug == slug).first()
    posts = Post.query.filter(Post.tags.contains(tag))
    #print(posts, f'\ntype of posts: {type(posts)}')
    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    pages = posts.paginate(page=page, per_page=5)

    return render_template('posts/tag_detail.html',
        tag=tag,
        pages=pages
    )

## 
#   dont work pagination!!!
##

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
            Post.body.contains(q) |
            Post.tags.any(name=q)
            )   #Post.tags.any(name=q)    # поиск по тегам

    else:
        posts = Post.query.order_by(db.desc(Post.created))

    pages = posts.paginate(page=page, per_page=5, max_per_page=5)
    
    # print(pages.__dict__)


    return render_template('posts/search.html',
        pages=pages,
        q=q
    )