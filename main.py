from app import app
from app import db
import view

from posts.blueprint import posts, user_profile
from login.login import login

app.register_blueprint(login, url_prefix='/')
app.register_blueprint(posts, url_prefix='/blog')
app.register_blueprint(user_profile, url_prefix='/contacts')


if __name__ == '__main__':
    app.run()