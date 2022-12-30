from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for
)
from flask_jwt_extended import current_user

from app import db#, csrf
from login.session_time import session_time
from models import (
    Chat,
    get_chat,
    get_user,
    get_all_chat
)

message = Blueprint('message',
    __name__,
    template_folder='templates')


@message.route('/', methods=['GET', 'POST'])
@session_time
# @csrf.exempt
def message_index():
    if request.method == 'POST':
        username = request.form.to_dict().get('username')
        another_user = get_user(username=username)
        chat = get_chat(current_user, another_user)
        if not chat and (current_user and another_user):
            chat = Chat()
            for user in [current_user, another_user]:
                chat.users.append(user)
            db.session.add(chat)
            db.session.commit()
    chats = get_all_chat(current_user)
   
    if chats:
        users = [i.username for i in chats[0].users if i.id != current_user.id]
        another_user = users[0]
    else:
        users = []
        chats = []
        another_user = ''

    return render_template('chat.html',
        users=users,
        current_user=current_user,
        another_user=another_user,
        chats=chats,
        root_url=request.url)