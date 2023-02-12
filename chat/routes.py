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
def message_index():
    another_user = ''
    username = ''
    if request.method == 'POST':
        username = request.form.to_dict().get('username')
        another_user = get_user(username=username)
        chat = get_chat(current_user, another_user)
        if not chat and (current_user and another_user and current_user != another_user):
            chat = Chat()
            for user in [current_user, another_user]:
                chat.users.append(user)
            db.session.add(chat)
            db.session.commit()
    chats = get_all_chat(current_user)
   
    if username == current_user.username:
        another_user = [i.uuid for i in chats[0].users if i.id != current_user.id]


    return render_template('chat.html',
        current_user=current_user,
        another_user=another_user,
        chats=chats,
        root_url=request.url
    )