from login.session_time import user_or_anon
from flask import (
    render_template,
    Blueprint,
    session,
    request,
    redirect,
    url_for,
    flash,
    make_response
)

from app import app, db
from .forms import (
    EmailForm,
    RegistrationForm,
    LoginForm,
    ResetPasswordForm
)
from models import Knot
from utils import encrypt_string
from datetime import datetime, timedelta
from .send_email import send_email
from config import login_stamp
from flask_wtf.csrf import generate_csrf

# route user enter data to form for autorization process.
login = Blueprint('login', __name__, template_folder='templates')


@login.route('auth/', methods=['GET'])
def authentication():

    now = datetime.now()

    try:
        user = Knot.query.filter(Knot.slug==request.args.get('user')).first()
        time_delta = now - user.auth_key_create

        if user.authenticated:
            return redirect('/blog/')
        elif user.auth_key == request.args.get('key') and user.check_auth_key():
            user.authenticated = 1
            session['auth'] = True
            db.session.commit()
            flash(u'Your email address has been verified!', 'alert alert-success')
            return redirect(url_for('login.log_in'))
        else:
            user.get_auth_key()
            subject = "authentication"
            url = f'{request.url_root}auth/?user={user.slug}&key={user.auth_key}'
            content = lambda: render_template('emails/confirmed.html', url=url)
            send_email(user.email, subject, content)
            flash(u'Time has passed, we are sending a new link', 'alert alert-danger')
            return redirect(url_for('login.log_in'))
    except Exception as e:
        print(f'Something wrong: {e.__class__}')
        return redirect(url_for('posts.index'))


@login.route('/sign_up', methods=['GET', 'POST'])
@user_or_anon
def sign_up(current_user):

    form = RegistrationForm(request.form)

    if current_user:
        return redirect('/blog/')
    elif request.method == 'POST' and form.validate_on_submit():
        try:
            user = Knot(
                f_name=form.f_name.data,
                s_name=form.s_name.data,
                username=form.username.data,
                phone_number=form.phone_number.data,
                email=form.email.data,
                password=form.password.data
            )
            if user.email != app.config.get('MAIL_USERNAME'):
                subject = "authentication"
                url = f'{request.url_root}auth/?user={user.slug}&key={user.auth_key}'
                content = lambda: render_template('emails/confirmed.html', url=url)
                send_email(user.email, subject, content)
            else:
                user.admin = 1
                user.authenticated = 1
            db.session.add(user)
            db.session.commit()
            flash(u'Confirm you email', 'alert alert-warning')
        except Exception as e:
            print(f'Something wrong: {e.__class__}')
            raise e
        return redirect(url_for('login.log_in'))	
    return render_template('registration.html',
        title='Sign In',
        form=form,
        session=session,
        endpoint=request.endpoint
    )


@login.route('/log_in', methods=['POST', 'GET'])
@user_or_anon
def log_in(current_user, alert=None, redirect_url=None):

    form = LoginForm(request.form)
    alert = request.args.get('alert')

    csrf = generate_csrf(
        secret_key=app.config['SECRET_KEY'], token_key=login_stamp)

    if current_user:
        return redirect('/blog/')
    elif request.method == "POST" and form.validate_on_submit():
        user = Knot.query.filter_by(username=form.username.data).first()
        if user and user.password == encrypt_string(form.password.data):
            session['username'] = user.username
            session['auth'] = user.authenticated
            user.last_login = datetime.now()
            db.session.commit()
            session['last_login'] = user.last_login
            session['private_key_exp'] = user.last_login + timedelta(hours=3)
            if redirect_url:
            	return redirect(redirect_url)
            return redirect(url_for('posts.index'))
        else:
            form.password.errors.append('Incorrect data. Please try again.')
            for f in form._fields.values():
                if f.id == 'username' and user:
                    continue
                f.data = None

    response = make_response(render_template('login.html',
        title='Log in',
        alert=alert,
        csrf=csrf,
        form=form,
        session=session,
        endpoint=request.endpoint
    ))
    response.set_cookie('access_token_cookie', '', expires=0)

    return response
    
    
# @login.route('/log_out', methods=['POST', 'GET'])
# def log_out():
#     return redirect(url_for('login.log_in'))


@login.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    if request.method == 'GET':
        if not request.args:
            form = EmailForm()
            return render_template(
                'get_email.html', title='Knots password changer', form=form)
        else:
            reset_password_key = request.args.get('reset_key')
            form = ResetPasswordForm()
            response = make_response(render_template(
                'reset_password.html', title='Knots reset password', form=form))
            response.set_cookie('reset_key', reset_password_key)
            return response
    # elif request.method == 'POST':
    #     # reset_password_key = request.args.get('reset_key')
    #     data = jwt.decode(reset_password_key, options={"verify_signature": False})
    #     pass

@login.route('/privacy_policy', methods=['GET'])
def privacy():

    return render_template('privacy.html',
        title='Privacy Policy',
        session=session,
    )
