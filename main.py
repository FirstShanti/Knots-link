from app import app
import view
from posts.blueprint import posts, user_profile
from login.login import login
from admin.admin import admin 

app.register_blueprint(login, url_prefix='/')
app.register_blueprint(posts, url_prefix='/blog')
app.register_blueprint(user_profile, url_prefix='/contacts')
app.register_blueprint(admin, url_prefix='/admin')


if __name__ == '__main__':
    app.run(port=5555)
