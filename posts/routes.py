import re
from flask_jwt_extended import current_user
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

from app import db#, csrf
from .forms import PostForm, CommentForm, CategoryForm, get_category
from login.session_time import session_time, user_or_anon
from login.send_email import send_email
from login.is_email_authenticated import is_email_authenticated
from admin.admin_handler import admin_handler
from models import (
    Post,
    Tag,
    Knot,
    Comment,
    Category,
)


SUCCESSFUL = 'alert alert-success'
ERROR = 'alert alert-danger'
WARNING = "alert alert-warning"

posts = Blueprint('posts',
    __name__,
    template_folder='templates')

        
### Create post ###
'''Page with form for write Title Body and Tag. 
   Than its information put in class Post and add in db.''' 

@posts.route('/create', methods=['POST', 'GET'])
@session_time
@is_email_authenticated
def create_post():
    form = PostForm(request.form)
    form.category.choices = get_category()

    if request.method == 'POST' and current_user.authenticated and form.validate_on_submit():
        try:
            post = Post(
                title=form.title.data,
                preview=form.preview.data,
                body=form.body.data,
                author=current_user.username
            )
            if form.category.data != 'ch':
                post.category_id = Category.query.filter(Category.short_name==form.category.data).first().id
            tag_list = re.sub(r'[\s, .]', ' ', form.tags.data).split()
            for i in set(tag_list):
                if Tag.query.filter_by(name=i).first():
                    tag = Tag.query.filter_by(name=i).first()
                else:
                    tag = Tag(name=i)
                post.tags.append(tag)
            if request.form['submit'] == 'draft':
                post.visible = False
            db.session.add(post)
            db.session.commit()
            try:
                subject = "Good job!"
                content = lambda: render_template('emails/post_to_email.html', post=post)
                send_email(current_user.email, subject, content)
            except Exception as e:
                print('email error:', e)
                flash(u'Post create, but not send to email', WARNING)
            flash(u'Post create', SUCCESSFUL)
        except Exception as e:
            print('some error:', e)
            flash(u'ERROR: {}'.format(e.__class__), ERROR)
            raise e
        return redirect(url_for('posts.index'))
    elif request.method == 'POST' and not current_user.authenticated:
        flash(u'Before saving the changes, you must confirm the email address.', 'alert alert-warning')
    else:
        return render_template('create_post.html', form=form, categories=Category.query.all())


@posts.route('/<slug>/edit/', methods=['POST', 'GET'])
@session_time
@is_email_authenticated
def edit_post(slug):

    post = Post.query.filter(Post.slug==slug, Post.author==current_user.username).first()
    fields = dict(
        title = post.title,
        body = post.body,
        preview = post.preview,
        tags=', '.join(list(str(i.name) for i in post.tags.__iter__()))
    )
    category = Category.query.get(post.category_id)
    if category:
        fields['category'] = category.short_name

    form = PostForm(**fields)
    if not category:
        form.category.choices = get_category()

    try:
        if request.form['submit'] == 'cancel':
            return redirect(url_for('posts.index'))
    except KeyError:
        pass

    if request.method == 'POST' and current_user.authenticated and current_user.username == post.author and form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.preview = form.preview.data
        if form.category.data != 'ch':
            post.category_id = Category.query.filter(Category.short_name==form.category.data).first().id
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
                subject = "Good job!"
                content = lambda: render_template('emails/post_to_email.html', post=post)
                send_email(current_user.email, subject, content)
            except Exception as e:
                flash(u'Post create, but not send to email', WARNING)
            flash(u'Changes saved successfully', SUCCESSFUL)
        except Exception as e:
            flash(u'ERROR: {e}', ERROR)
        return redirect(url_for('posts.post_content', slug=post.slug))
    elif request.method == 'POST' and not current_user.authenticated:
        flash(u'Before saving the changes, you must confirm the email address.', 'alert alert-warning')
        return render_template('edit_post.html',
            post=post,
            form=form,
            categories=Category.query.all()
        )
    else:
        return render_template('edit_post.html',
            post=post,
            form=form,
            categories=Category.query.all()
        )

@posts.route('/<slug>/delete/', methods=['POST', 'GET'])
@session_time
def delete_post(slug):
    post = Post.query.filter(Post.slug==slug).filter(Post.visible==True).first()

    if current_user.username == post.author:
        try:
            post.invisible()
            db.session.commit()
            flash(u'Post moved to trash', WARNING)
        except Exception as e:
            flash(u'Something happened', ERROR)
    return redirect('/blog/')


@posts.route('/', methods=['GET'])
@user_or_anon
def index(current_user):

    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    posts = Post.query.order_by(db.desc(Post.created)).filter(Post.visible==True)

    for post in posts:
        post.body = re.sub(r'\\r|\\n|\\t|<ul>|<li>|</ul>|</li>|<table|<tr|<td|</table|</td|</tr', '', ''.join(i for i in post.body.split("\n")[:3]))

    pages = posts.paginate(page=page, per_page=6, max_per_page=6)

    return render_template('index_posts.html',
        posts=posts,
        pages=pages,
        title="Blog",
        categories=Category.query.all(),
        с='',
        root_url=f'{request.url_root}',
        user=current_user
    )


@posts.route('/<slug>', methods=['POST', 'GET'])
@user_or_anon
def post_content(current_user, slug):
    try:
        post = Post.query.filter(Post.slug==slug).first()
        if (not current_user or current_user.username != post.author) and not post.visible:
            post = None
        tags = post.tags
        time = post.created_to_str()
        author = post.author
        comments = post.comments
    except AttributeError as e:
        print(e)
        return redirect('/blog/')

    form = CommentForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        if current_user and current_user.authenticated:
            try:
                comment = Comment(
                    text=form.text.data,
                    author_id=current_user.id,
                    post_id=post.id
                )
                db.session.add(comment)
                db.session.commit()
                flash('Comment added', SUCCESSFUL)
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
        user=current_user,
        comments=comments,
        form=form,
        slug=slug,
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

    category = Category.query.filter(Category.name==slug).first()
    if not category:
        posts = Post.query.filter(Post.visible==True)
    elif category:
        posts = Post.query.filter(Post.category_id==category.id).filter(Post.visible==True)
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

    if api_header:
        num_list = []
        for i in pages.iter_pages():
            num_list.append(i)
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
    page = request.args.get('page')
    try:
        category = Category.query.filter(Category.name==cat).first()
    except Exception as e:
        category = False

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
