import json
import re

from forms import PostForm, CommentForm, CategoryForm, get_category
from app import db
from datetime import datetime, timedelta
from login.session_time import session_time
from login.send_email import send_email
from login.is_email_authenticated import is_email_authenticated
from admin.admin_handler import admin_handler
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    jsonify
)
from models import (
    Post,
    Tag,
    Knot,
    Comment,
    Category,
    slugify,
    Chat
)
from utility import get_user, get_chat, get_all_chat
from config import local, lang
# from sqlalchemy.exc import IntegrityError


SUCCESSFUL = 'alert alert-success'
ERROR = 'alert alert-danger'
WARNING = "alert alert-warning"

posts = Blueprint('posts',
    __name__,
    template_folder='templates'
)
user_profile = Blueprint('user_profile',
    __name__,
    template_folder='templates'
)
message = Blueprint('message',
    __name__,
    template_folder='templates'
)


@message.route('/', methods=['GET', 'POST'])
@session_time
@is_email_authenticated
def message_index():
    if session.get('username'):
        current_user = get_user()
        if request.method == 'POST':
            username = request.form.to_dict().get('username')
            another_user = get_user(username=username)
            chat = get_chat(current_user, another_user)
            if not chat:
                chat = Chat()
                for user in [current_user, another_user]:
                    chat.users.append(user)
                db.session.add(chat)
                db.session.commit()
        chats = get_all_chat(current_user.id)
        if chats:
            users = [i.username for i in chats[0].users if i.username != session['username']]
            another_user = users[0]
        else:
            users = []
            chats = []
            another_user = ''
        return render_template('chat.html',
            users=users,
            another_user=another_user,
            chats=chats,
            user=session.get('username'),
            root_url=request.url)
    else:
        return redirect(url_for('/log_in'))
        
### Create post ###
'''Page with form for write Title Body and Tag. 
   Than its information put in class Post and add in db.''' 

@posts.route('/create', methods=['POST', 'GET'])
# @session_time
@is_email_authenticated
def create_post():

    form = PostForm(request.form)
    form.category.choices = get_category()
    print('form.category.choices: ', form.category.choices)
    
    if 'username' in session:
        if request.method == 'POST' and form.validate_on_submit():
            try:
                post = Post(
                    title = form.title.data,
                    preview = form.preview.data,
                    body = form.body.data,
                    owner_id = Category.query.filter(Category.short_name==form.category.data).first().id, 
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
                try:
                    user = get_user()
                    if user:
                        send_email(user, post)
                except Exception as e:
                    print(e)
                    flash(u'Post create, but not send to email', WARNING)
                flash(u'Post create', SUCCESSFUL)
            except Exception as e:
                flash(u'ERROR: {}'.format(e.__class__), ERROR)
                raise e
            return redirect(url_for('posts.index'))
    else:
        return redirect('/log_in')


    return render_template('create_post.html', form=form, categories=Category.query.all())


@posts.route('/<slug>/edit/', methods=['POST', 'GET'])
# @session_time
@is_email_authenticated
def edit_post(slug):
    post = Post.query.filter(Post.slug==slug).filter(Post.author==session.get('username')).first()
    form = PostForm(
        title = post.title,
        body = post.body,
        preview = post.preview,
        category = Category.query.get(post.owner_id).short_name,
        # реализовать удаление тегов
        tags=', '.join(list(str(i.name) for i in post.tags.__iter__()))  
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
        post.owner_id = Category.query.filter(Category.short_name==form.category.data).first().id
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
            try:
                user = get_user()
                if user:
                    send_email(user, post)
            except Exception as e:
                print(e)
                flash(u'Post create, but not send to email', WARNING)
            flash(u'Changes saved successfully', SUCCESSFUL)
        except Exception as e:
            flash(u'ERROR: {e}', ERROR)
        return redirect(url_for('posts.post_content', slug=post.slug))
    elif not session:
        return redirect(url_for('login.log_in'))

    return render_template('edit_post.html',
        post=post,
        form=form,
        categories=Category.query.all()
    )

@posts.route('/<slug>/delete/', methods=['POST', 'GET'])
@session_time
def delete_post(slug):
    post = Post.query.filter(Post.slug==slug).filter(Post.visible==True).first()
    post_title = post.title

    if 'username' in session and session.get('username') == post.author:
        try:
            post.invisible()
            db.session.commit()
            flash(u'Post moved to trash', WARNING)
        except Exception as e:
            flash(u'Something happened', ERROR)
    return redirect('/blog/')


@posts.route('/', methods=['GET'])
def index():
    
    # if session.get('username'):
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
    print(dir(pages))
    print(pages.total)

    return render_template('index_posts.html',
        posts=posts,
        pages=pages,
        title="Blog",
        categories=Category.query.all(),
        с='',
        root_url=f'{request.url_root}',
        user=session.get('username')
    )
    # else:
    #     return redirect('/log_in')


@posts.route('/<slug>', methods=['POST', 'GET'])
def post_content(slug):

    try:
        post = Post.query.filter(Post.slug==slug).filter(Post.visible==True).first() or \
            Post.query.filter(Post.slug==slug).filter(Post.author==session.get('username')).first()
        tags = post.tags
        time = post.created_to_str() #post.created.strftime('%H:%M (%d %B %Y)')
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
                flash('Comment create', SUCCESSFUL)
            except Exception as e:
                print(f'Something wrong\n{e.__class__}')
                raise e
            return redirect(url_for('posts.post_content', slug=slug))
        else:
            return redirect(url_for('login.log_in'))

    return render_template('post_content.html',
        post=post,
        tags=tags,
        time=time,
        author=author,
        user=user,
        comments=comments,
        form=form,
        slug=slug,
        categories=Category.query.all()
    )


@user_profile.route('/<slug>')
@session_time
def get_user_data(slug):
    page = request.args.get('page')
    try:
        if slug == 'anonymous':
            return redirect('/log_in')
        elif 'username' in session:
            user = Knot.query.filter(Knot.slug==slug).first()
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
        phone_number=user.phone_number,
        posts=posts,
        pages=pages,
        categories=Category.query.all()
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
        title=tag.name,
        content_title=f'#{tag}',
        categories=Category.query.all()
    )


@posts.route('/category/add', methods=['GET', 'POST'])
@admin_handler
@session_time
def category_create():

    form = CategoryForm(request.form)

    if 'username' in session:
        if request.method == 'POST' and form.validate_on_submit():
            try:
                category = Category(
                    name=form.name.data,
                    short_name=form.short_name.data
                )
                db.session.add(category)
                db.session.commit()
                flash('Category create', SUCCESSFUL)
            except Exception as e:
                print(f'Something wrong\n{e.__class__}')
            return redirect(url_for('admin.admin_index'))
    else:
        return redirect('/log_in')


@posts.route('/category/<slug>/', methods=['GET'])
def category_detail(slug):

    headers = request.headers
    api_header = headers.get('api_header')

    if slug == 'none':
        posts = Post.query.filter(Post.visible==True)
    elif Category.query.filter(Category.name==slug).first():
        category = Category.query.filter(Category.slug==slug).first()
        posts = Post.query.filter(Post.owner_id==category.id).filter(Post.visible==True)
    else:
        return jsonify({'json_list':0})

    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    pages = posts.paginate(page=page, per_page=6)
    categories = Category.query.all()

    pagination = {}
    pagination['pages'] = [i for i in pages.iter_pages()]
    pagination['items'] = [i.__dict__ for i in pages.items]
    pagination['has_prev'] = pages.has_prev
    pagination['has_next'] = pages.has_next
    pagination['next_num'] = pages.next_num
    pagination['prev_num'] = pages.prev_num

    for i in pagination['items']:
        del i['_sa_instance_state']
        i['created'] = i['created'].isoformat(timespec='seconds')
    # print(pagination)
    if api_header:
        num_list = []
        for i in pages.iter_pages():
            num_list.append(i)
        # return jsonify({'json_list' : [{'title':i.title, 'preview':i.preview, 'slug':i.slug} for i in pages.items], 'pages_list' : num_list})
        return jsonify(pagination)

    return render_template('index_posts.html',
        title=category.name,
        pages=pages,
        c=category,
        categories=categories
    )


@posts.route('/search/')
def search():
    q = request.args.get('q') # search value from form
    cat = request.args.get('c')
    print(f'q: {q}\ncategory: {cat}')
    page = request.args.get('page')
    try:
        category = Category.query.filter(Category.name==cat).first()
    except Exception as e:
        category = False
    # print(category)
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    if q and category:
        posts = Post.query.filter(Post.owner_id.contains(category.id)).filter(
            Post.title.contains(q) |
            Post.title.contains(q.lower()) |
            Post.title.contains(q.capitalize()) |
            Post.title.contains(' '.join(i.capitalize() for i in q.split(' '))) |
            Post.body.contains(q) |
            Post.tags.any(name=q.lower()) |
            Post.author.contains(q)
        ).filter(Post.visible==True)
    elif q and not category:
        posts = Post.query.filter(
            Post.title.contains(q) | # поиск по заголовку
            Post.body.contains(q) | #поиск по телу поста
            Post.tags.any(name=q.lower()) |
            Post.author.contains(q) # поиск по тегам
        ).filter(Post.visible==True)
    elif not q and category:
        posts = Post.query.filter(Post.owner_id.contains(category.id)).filter(Post.visible==True)
        q = ''
    else:
        posts = Post.query.order_by(db.desc(Post.created)).filter(Post.visible==True)
    pages = posts.paginate(page=page, per_page=6, max_per_page=6)

    return render_template('index_posts.html',
        pages=pages,
        q=q,
        title=f'Search: {q} {category.name if category else "All category"}',
        content_title=f'Result for <span style="color: #718F94">{q}</span>:',
        categories=Category.query.all(),
        c=category
    )